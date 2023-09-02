from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import TypedDict
from typing import Union

from .tx_type import Log


RawTraceCall = TypedDict(
    "RawTraceCall",
    {
        "from": str,
        "gas": str,
        "gasUsed": str,
        "input": str,
        "logs": List[Log],
        "output": str,
        "to": str,
        "type": Literal["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"],
        "value": str,
        "calls": List["RawTraceCall"],
    },
    total=False,
)

RawTraceCallResult = TypedDict(
    "RawTraceCallResult",
    {
        "from": str,
        "gas": str,
        "gasUsed": str,
        "input": str,
        "to": str,
        "type": Literal["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"],
        "calls": List[RawTraceCall],
    },
    total=False,
)


class RPCError(TypedDict, total=False):
    code: int
    message: str
    gasFeeCap: int
    baseFee: int


class RawTraceCallResponse(TypedDict, total=False):
    id: Union[str, int]
    jsonrpc: str
    result: RawTraceCallResult
    error: Optional[RPCError]
