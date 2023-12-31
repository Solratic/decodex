import json
import os
from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Generator
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Union

from decodex.constant import DECODEX_DIR
from decodex.type import ERC20Compatible
from decodex.type import TaggedAddr


class AddrTagger(ABC):
    @abstractmethod
    def lazy_tag(
        self, address: Sequence[Optional[Union[str, Dict]]]
    ) -> Generator[Union[TaggedAddr, ERC20Compatible], None, None]:
        """
        Tag addresses.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(
        self, address: Union[Sequence[Optional[Union[str, Dict]]], Optional[str]]
    ) -> Sequence[Optional[Union[TaggedAddr, ERC20Compatible]]]:
        """
        Tag one or more addresses.
        """
        raise NotImplementedError


class SyncAddrTagger(AddrTagger):
    """
    Tag addresses synchronously, one by one.
    """

    def __call__(
        self, address: Union[Sequence[Optional[Union[str, Dict]]], Optional[str]]
    ) -> Sequence[Optional[Union[TaggedAddr, ERC20Compatible]]]:
        if address is None:
            return [None]
        if isinstance(address, str):
            address = [address]
        return list(self.lazy_tag(address))


class JSONAddrTagger(SyncAddrTagger):
    """
    A class for tagging addresses using data from a JSON file.

    This class extends the functionality of SyncAddrTagger to provide address tagging using information
    stored in a JSON file. The JSON file should contain address-tag pairs, where each address is associated
    with metadata like name and labels.

    Parameters
    ----------
        path (str): The path to the JSON file containing address-tag data. Defaults to `~/.decodex/tags.json`

    Raises
    ------
        AssertionError: If the provided path does not correspond to a valid file or is not a JSON file.


    Example
    -------
    To use the JSONAddrTagger, create an instance with the path to a valid JSON file and then call
    the instance with a single address or a list of addresses to obtain tagging information.

    ```python
    tagger = JSONAddrTagger("address_tags.json")
    tagged_addresses = tagger(["0x22ff777ef6fe0690f1f74c6758126909653ad56a"])
    for addr in tagged_addresses:
        print(addr)
    ```
    """

    def __init__(self, path: str = None, chain: str = "ethereum") -> None:
        if path is None:
            path = str(DECODEX_DIR.joinpath(chain, "tags.json"))
        assert os.path.isfile(path), f"Path {path} is not a file."
        assert path.endswith(".json"), f"Path {path} is not a JSON file."

        with open(path, "r") as file:
            self._addr_tags: Dict[str, Any] = json.load(file)

    def lazy_tag(
        self,
        address: Sequence[Optional[Union[str, Dict]]],
    ) -> Generator[Optional[Union[TaggedAddr, ERC20Compatible]], None, None]:
        for addr in address:
            if addr is None:
                yield None
                continue
            if isinstance(addr, dict):
                _relying_addr: Optional[str] = addr.get("address", None)
                if _relying_addr is None or not isinstance(_relying_addr, str):
                    yield None
                    continue
                tag: Dict[str, Any] = self._addr_tags.get(_relying_addr.lower(), {})
                addr["name"] = addr["name"] or tag.get("name", "")
                addr["labels"] = tag.get("labels", [])
                yield addr
            else:
                tag: Dict[str, Any] = self._addr_tags.get(addr.lower(), {})
                yield {
                    "address": addr,
                    "name": tag.get("name", ""),
                    "labels": tag.get("labels", []),
                }


class BatchAddrTagger(AddrTagger):
    def __init__(self) -> None:
        super().__init__()

    def __call__(
        self, address: Sequence[Optional[str]] | Optional[str]
    ) -> Sequence[Union[TaggedAddr, ERC20Compatible]]:
        raise NotImplementedError


class TaggerFactory:
    @staticmethod
    def create(
        tagger_type: Literal["json", "sql"],
        uri: str = None,
        chain: str = "ethereum",
    ) -> AddrTagger:
        if tagger_type == "json":
            return JSONAddrTagger(path=uri, chain=chain)
        else:
            raise ValueError(f"Unknown tagger type: {tagger_type}")
