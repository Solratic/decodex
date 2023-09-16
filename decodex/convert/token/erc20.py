from threading import Lock
from typing import Any
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import diskcache
from cachetools import cached
from cachetools import LRUCache
from multicall import Call
from multicall import Multicall

from decodex.constant import DECODEX_DIR
from decodex.constant import NULL_ADDRESS_0x0
from decodex.constant import NULL_ADDRESS_0xF
from decodex.type import ERC20Compatible


class ERC20TokenService:
    _instance = None
    _initialize = False
    _singleton_lock = Lock()

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ERC20TokenService, cls).__new__(cls)
        return cls._instance

    def __init__(self, mc: Multicall, *, cache_path: Optional[str] = None) -> None:
        with self._singleton_lock:
            if not self._initialize:
                self._mc = mc
                self._cache = diskcache.Cache(cache_path or DECODEX_DIR.joinpath("erc20"))
                self._initialize = True

    @cached(cache=LRUCache(maxsize=131072), lock=Lock())
    def get_erc20(
        self,
        address: str,
        block_number: Union[int, Literal["latest"]] = "latest",
        *,
        strict: bool = True,
    ) -> Optional[ERC20Compatible]:
        """
        Get ERC20 token information from address.

        Parameters
        ----------
        address : str
            Token address.
        block_number : int or "latest", optional
            Block number to query, by default "latest".
        strict : bool, optional
            if True, return None when token is not found or not ERC20 compatible, by default True.
        """
        token = self._cache.get(address)
        if token is not None:
            return token

        if address in {NULL_ADDRESS_0x0, NULL_ADDRESS_0xF}:
            suffix = "ETH Transfer" if address == NULL_ADDRESS_0x0 else "Gas Fee"
            return {
                "name": f"Platform Token ({suffix})",
                "address": address,
                "contract_name": None,
                "symbol": "ETH",
                "decimals": 18,
                "labels": [],
            }

        response: Dict[str, Any] = self._mc.agg(
            [
                Call(
                    target=address,
                    function="name()(string)",
                    request_id=f"{address}-name",
                ),
                Call(
                    target=address,
                    function="symbol()(string)",
                    request_id=f"{address}-symbol",
                ),
                Call(
                    target=address,
                    function="decimals()(uint8)",
                    request_id=f"{address}-decimals",
                ),
            ],
            block_id=block_number,
            as_dict=True,
        )

        name = response.get(f"{address}-name", None)
        symbol = response.get(f"{address}-symbol", None)
        decimals = response.get(f"{address}-decimals", None)

        if strict and (name is None or symbol is None or decimals is None):
            return None

        rtn = {
            "name": None,
            "address": address.lower(),
            "contract_name": name,
            "decimals": decimals,
            "symbol": symbol,
            "labels": [],
        }

        self._cache.set(address, rtn)

        return rtn

    def batch_get_erc20(
        self,
        addresses: List[str],
        block_number: Union[int, Literal["latest"]] = "latest",
    ) -> List[Optional[ERC20Compatible]]:
        return [self.get_erc20(address, block_number=block_number) for address in addresses]
