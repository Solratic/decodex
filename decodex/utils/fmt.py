from datetime import datetime
from decodex.utils import trunc_addr
from typing import Dict


def fmt_blktime(blktime: datetime) -> str:
    return blktime.strftime("%Y-%m-%d %H:%M:%S") + " UTC"


def fmt_addr(ta: Dict) -> str:
    addr = ta["address"]
    name = ta["name"]
    labels = ", ".join(l for l in ta["labels"] if l)

    rtn = name if name else trunc_addr(addr)
    if labels:
        rtn += f" [{labels}]"
    return rtn


def fmt_gas(gas_price: int) -> str:
    return f"{gas_price} Gwei"


def fmt_value(value: int) -> str:
    return f"{value} Ether"


def fmt_status(status: int) -> str:
    return "Success" if status == 1 else "Failed"
