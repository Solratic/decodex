from datetime import datetime
from typing import Dict

from .utils import trunc_addr


def fmt_blktime(blktime: datetime) -> str:
    return blktime.strftime("%Y-%m-%d %H:%M:%S") + " UTC"


def fmt_addr(ta: Dict, truncate: bool = True) -> str:
    addr = ta["address"]
    name = ta["name"]
    labels = ", ".join(lbl for lbl in ta["labels"] if lbl)

    if truncate:
        rtn = name if name else trunc_addr(addr)
    else:
        rtn = f"{addr} ({name})" if name else addr
    if labels:
        rtn += f" [{labels}]"
    return rtn


def fmt_gas(gas_price: int) -> str:
    return f"{gas_price} Gwei"


def fmt_value(value: int) -> str:
    return f"{value} Ether"


def fmt_status(status: int) -> str:
    return "Success" if status == 1 else "Failed"
