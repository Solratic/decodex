import json
import traceback
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging import Logger
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

import pytz
from multicall import Call
from multicall import Multicall
from web3 import Web3

from decodex.convert.address import AddrTagger
from decodex.convert.address import TaggerFactory
from decodex.convert.signature import SignatureFactory
from decodex.convert.signature import SignatureLookUp
from decodex.decode import eth_decode_log
from decodex.search import SearcherFactory
from decodex.translate.events import AAVEV2Events
from decodex.translate.events import AAVEV3Events
from decodex.translate.events import BancorEV3Events
from decodex.translate.events import CompoundV3Events
from decodex.translate.events import CurveV2Events
from decodex.translate.events import ERC20Events
from decodex.translate.events import UniswapV2Events
from decodex.translate.events import UniswapV3Events
from decodex.type import AccountBalanceChanged
from decodex.type import Action
from decodex.type import AssetBalanceChanged
from decodex.type import EventHandleFunc
from decodex.type import TaggedAddr
from decodex.type import TaggedTx
from decodex.type import TransferAction
from decodex.type import Tx
from decodex.type import UTF8Message
from decodex.utils import parse_ether
from decodex.utils import parse_gwei
from decodex.utils import parse_utf8


class Translator:
    evt_opts: Dict[str, Any] = {
        "uniswapv2": UniswapV2Events,
        "uniswapv3": UniswapV3Events,
        "bancorv3": BancorEV3Events,
        "curvev2": CurveV2Events,
        "aavev2": AAVEV2Events,
        "aavev3": AAVEV3Events,
        "compoundv3": CompoundV3Events,
    }

    def __init__(
        self,
        provider_uri: str,
        chain: str = "ethereum",
        tagger: AddrTagger = "json",
        sig_lookup: SignatureLookUp = "csv",
        defis: Union[Iterable[str], Literal["all"]] = "all",
        verbose: bool = False,
        logger: Logger = None,
        *args,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        provider_uri : str
            URI of the Ethereum http provider
        tagger : AddrTagger, optional
            Address tagger or the `tagger_types` in TaggerFactory, default is "json"
        sig_lookup : SignatureLookUp, optional
            Signature lookup or the `sig_lookup_types` in SignatureFactory, default is "csv"
        defis : Union[Iterable[str], Literal["all"]], optional
            List of defi protocols to decode or "all" to decode all supported protocols, default is "all"
            You can get the list of supported protocols by calling `Translator.supported_defis()`
        verbose : bool, optional
            Whether to print error messages when decoding logs, default is False
        logger : Logger, optional
            Logger to log error messages, default is None
        """
        self.tagger = TaggerFactory.create(tagger) if isinstance(tagger, str) else tagger

        self.sig_lookup = (
            SignatureFactory.create(fmt=sig_lookup, chain=chain) if isinstance(sig_lookup, str) else sig_lookup
        )

        self.searcher = SearcherFactory.create("web3", uri=provider_uri)
        self.mc = Multicall(provider_uri, logger=logger)
        self.hdlrs: Dict[str, EventHandleFunc] = {}
        self.__register__(self.evt_opts.keys() if defis == "all" else defis)

        self.verbose = verbose
        if logger is None and verbose:
            self.logger = Logger(name=self.__class__.__name__)

    def translate(self, txhash: str, *, max_workers: int = 10) -> TaggedTx:
        tx: Tx = self.searcher.get_tx(txhash)
        return self._process_tx(tx, max_workers=max_workers)

    def simulate(self, from_address: str, to_address: str, value: int, data: str, *, max_workers: int = 10) -> TaggedTx:
        tx: Tx = self.searcher.simluate_tx(from_address=from_address, to_address=to_address, value=value, data=data)
        return self._process_tx(tx, max_workers=max_workers)

    @classmethod
    def supported_defis(cls) -> List[str]:
        return list(cls.evt_opts.keys())

    def __register__(self, defis: Iterable[str]) -> None:
        # ERC20Events must be registered
        opts = self.evt_opts
        opts["erc20"] = ERC20Events

        for defi in defis:
            assert defi in opts, f"defi protocol {defi} is not yet supported"
            cls = opts.get(defi)(self.mc, self.tagger, self.sig_lookup)
            for attr in dir(cls):
                if attr.startswith("_"):
                    continue
                handle_func = getattr(cls, attr)
                if not callable(handle_func):
                    continue
                text_sig, decoder = handle_func()
                byte_sig = Web3.keccak(text=text_sig).hex()
                self.hdlrs[byte_sig] = decoder

    def _decode_log(self, log: Dict[str, Any]) -> Optional[Action]:
        topics = log.get("topics", [])
        if len(topics) == 0:
            raise ValueError("Log topics is empty")
        handler = self.hdlrs.get(topics[0], None)
        if handler is None:
            return None
        abi_textsign_list = self.sig_lookup(topics[0])
        for abi, _ in abi_textsign_list:
            abi = json.loads(abi)
            try:
                _, params = eth_decode_log(abi, topics, log.get("data", "0x"))
                result = handler({"address": log["address"], "params": params})
                return result
            except Exception as e:
                if self.verbose:
                    traceback.print_exc()
                    self.logger.error(f"Error when decoding log {log} with error {e}")
        return None

    def _get_balance_of(
        self,
        addr_token_pairs: Iterable[Tuple[str, str]],
        blk_num: int,
    ) -> Dict[str, float]:
        """
        Get the balance of a list of (address, ERC20 token) pairs, and return a dict of str((addr,token)) -> balance.
        """

        # Get all decimals
        decimal_calls: List[Call] = []
        involved_tokens: Set[str] = set(token for _, token in addr_token_pairs)
        for token in involved_tokens:
            decimal_calls.append(
                Call(
                    target=token,
                    function="decimals()(uint8)",
                    request_id=token,
                    block_id=blk_num,
                )
            )
        decimals: Dict[str, int] = self.mc.agg(decimal_calls, as_dict=True)

        # Get all balances
        calls: List[Call] = []
        for addr, token in addr_token_pairs:
            calls.append(
                Call(
                    target=token,
                    function="balanceOf(address)(uint256)",
                    args=(addr,),
                    request_id=str((addr, token)),
                    block_id=blk_num,
                )
            )
        balances: Dict[str, int] = self.mc.agg(calls, as_dict=True)
        return {addr_token: balances[addr_token] / 10 ** decimals[token] for addr_token in balances}

    def _process_erc20_transfer(
        self,
        actions: List[TransferAction],
        blk_num: int,
    ) -> List[AccountBalanceChanged]:
        tagged_mapping: Dict[str, TaggedAddr] = {}
        addr_token_pairs = set()

        for action in actions:
            sender = action.sender["address"]
            receiver = action.receiver["address"]
            token = action.token["address"]

            tagged_mapping[sender] = action.sender
            tagged_mapping[receiver] = action.receiver
            tagged_mapping[token] = action.token

            addr_token_pairs.add((sender, token))
            addr_token_pairs.add((receiver, token))

        initial_balances = self._get_balance_of(addr_token_pairs, blk_num)

        balance_changed: Dict[str, Dict[str, AssetBalanceChanged]] = {}
        for account, token in addr_token_pairs:
            if account not in balance_changed:
                balance_changed[account] = {}

            initial_balance = initial_balances.get(str((account, token)), 0.0)
            balance_changed[account][token] = {
                "asset": tagged_mapping[token],
                "balance_before": initial_balance,
                "balance_change": 0.0,
                "balance_after": 0.0,  # placeholder, to be calculated later
            }

        for action in actions:
            sender = action.sender["address"]
            receiver = action.receiver["address"]
            token = action.token["address"]
            amount = action.amount

            balance_changed[sender][token]["balance_change"] -= amount
            balance_changed[receiver][token]["balance_change"] += amount

        for account, tokens in balance_changed.items():
            for token, changes in tokens.items():
                changes["balance_after"] = changes["balance_before"] + changes["balance_change"]

        account_balance_changed_list: List[AccountBalanceChanged] = []
        for account, assets_dict in balance_changed.items():
            tagged_account = tagged_mapping[account]
            asset_list = list(assets_dict.values())
            account_balance_changed_list.append({"address": tagged_account, "assets": asset_list})

        return account_balance_changed_list

    def _process_tx(self, tx: Tx, max_workers: int) -> TaggedTx:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            actions = executor.map(self._decode_log, tx["logs"])
        actions = [x for x in actions if x is not None]

        # Split actions into transfers and others
        transfers: List[TransferAction] = []
        others: List[Action] = []
        for action in actions:
            if isinstance(action, TransferAction):
                transfers.append(action)
            else:
                others.append(action)

        bal_changed = self._process_erc20_transfer(transfers, tx["block_number"])

        blk_time = datetime.fromtimestamp(tx["block_timestamp"], tz=pytz.utc)
        (tx_from, tx_to) = self.tagger([tx["from"], tx["to"]])

        if len(others) > 0:
            actions = others
        elif len(transfers) > 0:
            actions = transfers
        elif len(tx["input"]) > 0 and tx["input"] != "0x":
            msg = parse_utf8(tx["input"])
            if msg:
                actions = [UTF8Message(tx_from, tx_to, msg)]
        else:
            actions = []

        return {
            "txhash": tx["txhash"],
            "actions": actions,
            "from": tx_from,
            "to": tx_to,
            "block_time": blk_time,
            "value": parse_ether(tx["value"]),
            "gas_used": tx["gas_used"],
            "gas_price": parse_gwei(tx["gas_price"]),
            "input": tx["input"],
            "status": tx["status"],
            "balance_change": bal_changed,
        }
