from abc import ABC, abstractmethod
from decodex.type import Tx, Log
from web3 import Web3
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, Union
from web3.types import LogReceipt


class BaseSearcher(ABC):
    @abstractmethod
    def search_tx(self, txhash: str) -> Tx:
        """
        Search a transaction by its hash. Return a TxDict.
        """
        raise NotImplementedError


class Web3Searcher(BaseSearcher):
    def __init__(self, provider: Union[Web3, str] = None) -> None:
        """
        Initialize a Web3Searcher with a Web3 instance or a Web3 http provider URI.
        """
        if provider is None:
            provider = "http://localhost:8545"

        if isinstance(provider, str):
            provider = Web3(Web3.HTTPProvider(provider))

        self.web3 = provider

    def search_tx(self, txhash: str, max_workers: int = 2) -> Tx:
        assert max_workers > 0, "max_workers must be positive"
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tx = executor.submit(self.web3.eth.get_transaction, txhash)
            tx_receipt = executor.submit(self.web3.eth.get_transaction_receipt, txhash)
            tx, tx_receipt = tx.result(), tx_receipt.result()

        blk = self.web3.eth.get_block(tx_receipt["blockNumber"])
        logs: list[Log] = [
            {
                "logpos": log["logIndex"],
                "address": log["address"],
                "topics": [t.hex() for t in log["topics"]],
                "data": log["data"],
            }
            for log in tx_receipt["logs"]
        ]
        return {
            "txhash": tx_receipt["transactionHash"].hex(),
            "from": tx["from"],
            "to": tx["to"],
            "block_timestamp": blk["timestamp"],
            "value": tx["value"],
            "gas_used": tx_receipt["gasUsed"],
            "gas_price": tx["gasPrice"],
            "input": tx["input"],
            "status": tx_receipt["status"],
            "logs": logs,
        }


class SearcherFactory:
    @staticmethod
    def create(
        searcher_type: Literal["web3", "sql"],
        uri: str = None,
    ) -> BaseSearcher:
        if searcher_type == "web3":
            return Web3Searcher(provider=uri)
        elif searcher_type == "sql":
            raise NotImplementedError
        else:
            raise NotImplementedError
