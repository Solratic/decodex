import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from logging import Logger
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import pytz
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
from decodex.translate.events import UniswapV2Events
from decodex.translate.events import UniswapV3Events
from decodex.type import Action
from decodex.type import EventHandleFunc
from decodex.type import TaggedTx
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
        if logger is None:
            self.logger = Logger(name=self.__class__.__name__)

    def __register__(self, defis: Iterable[str]) -> None:
        for defi in defis:
            assert defi in self.evt_opts, f"defi protocol {defi} is not yet supported"
            cls = self.evt_opts.get(defi)(self.mc, self.tagger, self.sig_lookup)
            for attr in dir(cls):
                if attr.startswith("_"):
                    continue
                handle_func = getattr(cls, attr)
                if not callable(handle_func):
                    continue
                text_sig, decoder = handle_func()
                byte_sig = Web3.keccak(text=text_sig).hex()
                self.hdlrs[byte_sig] = decoder

    def translate(self, txhash: str, *, max_workers: int = 10) -> TaggedTx:
        tx: Tx = self.searcher.get_tx(txhash)
        return self._process_tx(tx, max_workers=max_workers)

    def simulate(self, from_address: str, to_address: str, value: int, data: str, *, max_workers: int = 10) -> TaggedTx:
        tx: Tx = self.searcher.simluate_tx(from_address=from_address, to_address=to_address, value=value, data=data)
        return self._process_tx(tx, max_workers=max_workers)

    @classmethod
    def supported_defis(cls) -> List[str]:
        return list(cls.evt_opts.keys())

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

    def _process_tx(self, tx: Tx, max_workers: int) -> TaggedTx:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            actions = executor.map(self._decode_log, tx["logs"])
        actions = [x for x in actions if x is not None]
        blk_time = datetime.fromtimestamp(tx["block_timestamp"], tz=pytz.utc)
        (tx_from, tx_to) = self.tagger([tx["from"], tx["to"]])
        if len(actions) == 0 and len(tx["input"]) > 0 and tx["input"] != "0x":
            msg = parse_utf8(tx["input"])
            if msg:
                actions = [UTF8Message(tx_from, tx_to, msg)]
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
        }
