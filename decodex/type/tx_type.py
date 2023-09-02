from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import TypedDict

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
        "name": str,  # name of the contract (e.g., USD Coin (USDC))
        "label": List[str],  # label of the address (e.g., ["centre", "stablecoin"])
    },
)

AssetBalanceChanged = TypedDict(
    "BalanceChange",
    {
        "asset": TaggedAddr,  # address of the asset
        "balance_before": float,  # balance before the transaction
        "balance_change": float,  # balance change of the asset
        "balance_after": float,  # balance after the transaction
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
        "to": str,  # to address, hex string. 0x prefixed.
        "block_number": int,  # block number of the transaction
        "block_timestamp": int,  # timestamp of the block, in seconds.
        "value": int,  # value of the transaction, in wei.
        "gas_used": int,  # gas used by the transaction, in wei.
        "gas_price": int,  # gas price of the transaction, in wei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "logs": List[Log],  # logs of the transaction
        "eth_balance_changes": Dict[str, Dict[Literal["ETH"], int]],  # ETH balance change of the transaction
    },
)


TaggedTx = TypedDict(
    "TaggedTx",
    {
        "txhash": str,  # transaction hash, hex string. 0x prefixed.
        "from": TaggedAddr,  # from address, hex string. 0x prefixed.
        "to": TaggedAddr,  # to address, hex string. 0x prefixed.
        "block_number": int,  # block number of the transaction
        "block_time": datetime,  # datetime of the block
        "value": int,  # value of the transaction, in Ether.
        "gas_used": int,  # gas used by the transaction, in Gwei.
        "gas_price": int,  # gas price of the transaction, in Gwei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "actions": List[str],  # actions of the transaction
        "balance_change": AccountBalanceChanged,  # balance change of the transaction
    },
)


EventPayload = TypedDict(
    "EventPayload",
    {
        "address": str,  # contract address, hex string. 0x prefixed.
        "params": Dict[str, Any],  # event parameters, the output from decoder
    },
)
