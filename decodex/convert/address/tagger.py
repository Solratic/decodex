from abc import ABC, abstractmethod
from decodex.type import TaggedAddr
from typing import Union, Sequence, Generator, Dict, Any, Literal
import json
import os
from decodex.constant import DECODEX_DIR
from pathlib import Path


class AddrTagger(ABC):
    @abstractmethod
    def lazy_tag(self, address: Sequence[str]) -> Generator[TaggedAddr, None, None]:
        """
        Tag addresses.
        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, address: Union[Sequence[str], str]) -> Sequence[TaggedAddr]:
        """
        Tag one or more addresses.
        """
        if isinstance(address, str):
            address = [address]
        return list(self.lazy_tag(address))


class SyncAddrTagger(AddrTagger):
    """
    Tag addresses synchronously, one by one.
    """

    def __call__(self, address: Union[Sequence[str], str]) -> Sequence[TaggedAddr]:
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
        address: Sequence[str],
    ) -> Generator[TaggedAddr, None, None]:
        for addr in address:
            tag: Dict[str, Any] = self._addr_tags.get(addr, {})
            yield {
                "address": addr,
                "name": tag.get("name", ""),
                "labels": tag.get("labels", []),
            }


class BatchAddrTagger(AddrTagger):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, address: Sequence[str] | str) -> Sequence[TaggedAddr]:
        raise NotImplementedError


class SQLAddrTagger(BatchAddrTagger):
    def lazy_tag(self, address: Sequence[str]) -> Generator[TaggedAddr, None, None]:
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
        elif tagger_type == "sql":
            raise NotImplementedError
        else:
            raise ValueError(f"Unknown tagger type: {tagger_type}")
