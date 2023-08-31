from typing import Tuple

from multicall import Multicall

from .dex import Events
from decodex.convert.address import AddrTagger
from decodex.type import Action
from decodex.type import EventHandleFunc
from decodex.type import EventPayload


class ERC20(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def transfer(self) -> Tuple[str, EventHandleFunc]:
        pass


class ERC721(Events):
    def transfer(self):
        pass
