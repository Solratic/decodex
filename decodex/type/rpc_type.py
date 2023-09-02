from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import TypedDict

from .tx_type import Log

CallType = Literal["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"]

RawCall = TypedDict(
    "Call",
    {
        "type": CallType,  # Four possible values: CALL, CALLCODE, DELEGATECALL, STATICCALL
        "from": str,  # Address of the account that initiated the call, 0x prefixed
        "to": str,  # Address of the account that will be called, 0x prefixed
        "value": str,  # Value transferred in wei, 0x prefixed
        "gas": str,  # Gas provided by the caller, 0x prefixed
        "gasUsed": str,  # Gas used by the call, 0x prefixed
        "input": str,  # Input data, 0x prefixed
        "output": Optional[str],  # Output data, 0x prefixed. Might be null if the call do not return anything
        "logs": List[Log],  # Array of log objects, which this call generated
    },
)

Call = TypedDict(
    "Call",
    {
        "type": CallType,  # Four possible values: CALL, CALLCODE, DELEGATECALL, STATICCALL
        "from": str,  # Address of the account that initiated the call, 0x prefixed
        "to": str,  # Address of the account that will be called, 0x prefixed
        "value": int,  # Value transferred in wei, 0x prefixed
        "gas": int,  # Gas provided by the caller, 0x prefixed
        "gasUsed": int,  # Gas used by the call, 0x prefixed
        "input": str,  # Input data, 0x prefixed
        "output": Optional[str],  # Output data, 0x prefixed. Might be null if the call do not return anything
        "logs": List[Log],  # Array of log objects, which this call generated
    },
)


RpcError = TypedDict(
    "RpcError",
    {
        "code": int,
        "message": str,
        "gasFeeCap": int,
        "baseFee": int,
    },
)

RawTraceCallResult = TypedDict(
    "RawTraceCallResult",
    {
        "calls": List[RawCall],
    },
)

RawTraceCallResponse = TypedDict(
    "RawTraceCallResponse",
    {
        "id": int,
        "jsonrpc": str,
        "result": Optional[RawTraceCallResult],
        "error": Optional[RpcError],
    },
)

TraceCallResponse = TypedDict(
    "TraceCallResponse",
    {
        "id": int,
        "jsonrpc": str,
        "result": List[Call],
        "error": RpcError,
    },
)
