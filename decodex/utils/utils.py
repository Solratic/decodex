from decimal import Decimal
from typing import Optional
from typing import Union


def trunc_addr(addr: str, offset: int = 4) -> str:
    return addr[: offset + 2] + "..." + addr[-offset:]


def parse_ether(wei: int) -> float:
    return Decimal(wei) / 10**18


def parse_utf8(hex: str) -> Optional[str]:
    try:
        byte_data = bytes.fromhex(hex)
        utf8_str = byte_data.decode("utf-8")
        return utf8_str
    except (ValueError, UnicodeDecodeError):
        return None


def parse_gwei(wei: int) -> float:
    return Decimal(wei) / 10**9


def parse_unit(wei: Union[int, str], unit: str) -> str:
    if unit == "eth":
        return parse_ether(wei)
    elif unit == "gwei":
        return parse_gwei(wei)
    else:
        return f"{wei} {unit}"
