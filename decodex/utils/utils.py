from decimal import Decimal
from typing import Union


def trunc_addr(addr: str, offset: int = 4) -> str:
    return addr[: offset + 2] + "..." + addr[-offset:]


def parse_ether(wei: int) -> float:
    return Decimal(wei) / 10**18


def parse_gwei(wei: int) -> float:
    return Decimal(wei) / 10**9


def parse_unit(wei: Union[int, str], unit: str) -> str:
    if unit == "eth":
        return parse_ether(wei)
    elif unit == "gwei":
        return parse_gwei(wei)
    else:
        return f"{wei} {unit}"
