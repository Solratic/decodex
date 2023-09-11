from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional


@dataclass(frozen=True)
class Action:
    @property
    @abstractmethod
    def action(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __str__(self):
        raise NotImplementedError

    def dict(self):
        return vars(self)


EventHandleFunc = Callable[[Dict[str, Any]], Optional[Action]]
