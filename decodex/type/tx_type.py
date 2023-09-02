from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import TypedDict

Log = TypedDict(
    "Log",
    {
        "address": str,  # contract address, hex string. 0x prefixed.
        "topics": List[str],  # topics of the log, each is a hex string of 0x prefixed.
        "data": str,  # data of the log, hex string. 0x prefixed.
    },
)


Tx = TypedDict(
    "Tx",
    {
        "txhash": str,  # transaction hash, hex string. 0x prefixed.
        "from": str,  # from address, hex string. 0x prefixed.
        "to": str,  # to address, hex string. 0x prefixed.
        "block_timestamp": int,  # timestamp of the block, in seconds.
        "value": int,  # value of the transaction, in wei.
        "gas_used": int,  # gas used by the transaction, in wei.
        "gas_price": int,  # gas price of the transaction, in wei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "logs": List[Log],  # logs of the transaction
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

TaggedTx = TypedDict(
    "TaggedTx",
    {
        "txhash": str,  # transaction hash, hex string. 0x prefixed.
        "from": TaggedAddr,  # from address, hex string. 0x prefixed.
        "to": TaggedAddr,  # to address, hex string. 0x prefixed.
        "block_time": datetime,  # datetime of the block
        "value": int,  # value of the transaction, in Ether.
        "gas_used": int,  # gas used by the transaction, in Gwei.
        "gas_price": int,  # gas price of the transaction, in Gwei.
        "input": str,  # input data of the transaction, hex string. 0x prefixed.
        "status": int,  # status of the transaction
        "actions": List[str],  # actions of the transaction
    },
)

EventPayload = TypedDict(
    "EventPayload",
    {
        "address": str,  # contract address, hex string. 0x prefixed.
        "params": Dict[str, Any],  # event parameters, the output from decoder
    },
)
