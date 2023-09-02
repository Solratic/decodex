from typing import Optional
from typing import Tuple

from multicall import Multicall

from .dex import Events
from decodex.convert.address import AddrTagger
from decodex.type import Action
from decodex.type import EventHandleFunc
from decodex.type import EventPayload
from decodex.type import TransferAction


class ERC20(Events):
    """
    Standard ERC20 token events.
    """

    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def transfer(self) -> Tuple[str, EventHandleFunc]:
        # Transfer (index_topic_1 address from, index_topic_2 address to, uint256 value)
        text_sig = "Transfer(address,address,value)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["address"]
            (token_decimals,) = self._get_token_decimals(token_addr)
            amount = payload["value"] / 10**token_decimals
            token, sender, receiver = self._tagger([token_addr, payload["from"], payload["to"]])
            return TransferAction(
                sender=sender,
                receiver=receiver,
                token=token,
                amount=amount,
            )

        return text_sig, decoder


class ERC721(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)
