__all__ = [
    "RPCException",
]


class RPCException(Exception):
    """Base class for all RPC exceptions."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code

    def __str__(self):
        return f"RPC request error with code {self.code}: {self.args[0]}"
