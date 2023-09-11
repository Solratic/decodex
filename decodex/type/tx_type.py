from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import TypedDict

from .base import Action


Log = TypedDict(
    "Log",
    {
        "address": str,  # contract address, hex string. 0x prefixed.
        "topics": List[str],  # topics of the log, each is a hex string of 0x prefixed.
        "data": str,  # data of the log, hex string. 0x prefixed.
    },
)


TaggedAddr = TypedDict(
    "TaggedAddr",
    {
        "address": str,  # address or ens name
        "name": str,  # name of the address in our label dataset (e.g., USD Coin (USDC))
        "labels": List[str],  # label of the address (e.g., ["centre", "stablecoin"])
    },
)


class ERC20Compatible(TaggedAddr):
    contract_name: Optional[str]  # name of the contract, different from 'name' (e.g., USD Coin)
    decimals: Optional[int]  # decimals of the token (e.g., 6)
    symbol: Optional[str]  # symbol of the token (e.g., USDC)


AssetBalanceChanged = TypedDict(
    "BalanceChange",
    {
        "asset": ERC20Compatible,  # address of the asset
        "balance_change": float,  # balance change of the asset
    },
)


AccountBalanceChanged = TypedDict(
    "AccountBalanceChanged",
    {
        "address": TaggedAddr,  # address of the account
        "assets": List[AssetBalanceChanged],  # balance change of each asset
    },
)


Tx = TypedDict(
    "Tx",
    {
        "txhash": str,  # transaction hash, hex string. 0x prefixed.
        "from": str,  # from address, hex string. 0x prefixed.
        "to": Optional[str],  # to address, hex string. 0x prefixed.
        "contract_created": Optional[TaggedAddr],  # contract created by the transaction, hex string. 0x prefixed.
        "block_number": int,  # block number of the transaction
        "block_timestamp": int,  # timestamp of the block, in seconds.
        "value": int,  # value of the transaction, in wei.
        "gas_used": int,  # gas used by the transaction, in wei.
        "gas_price": int,  # gas price of the transaction, in wei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "reason": str,  # reason of the transaction if failed
        "logs": List[Log],  # logs of the transaction
        "eth_balance_changes": Dict[str, Dict[Literal["ETH", "Gas Fee"], int]],  # ETH balance change of the transaction
    },
    total=False,
)


TaggedTx = TypedDict(
    "TaggedTx",
    {
        "txhash": str,  # transaction hash, hex string. 0x prefixed.
        "from": TaggedAddr,  # from address, hex string. 0x prefixed.
        "to": Optional[TaggedAddr],  # to address, hex string. 0x prefixed.
        "contract_created": Optional[TaggedAddr],  # contract created by the transaction, hex string. 0x prefixed.
        "block_number": int,  # block number of the transaction
        "block_time": datetime,  # datetime of the block
        "value": float,  # value of the transaction, in Ether.
        "gas_used": int,  # gas used by the transaction, in Gwei.
        "gas_price": float,  # gas price of the transaction, in Gwei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "reason": str,  # reason of the transaction if failed
        "method": str,  # calling method of the transaction
        "actions": List[Action],  # actions of the transaction
        "balance_change": List[AccountBalanceChanged],  # balance change of the transaction
    },
    total=False,
)


EventPayload = TypedDict(
    "EventPayload",
    {
        "address": str,  # contract address, hex string. 0x prefixed.
        "params": Dict[str, Any],  # event parameters, the output from decoder
    },
)
