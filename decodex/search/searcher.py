import os
from abc import ABC
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

from web3 import Web3
from web3.types import Wei

from decodex.exceptions import RPCException
from decodex.type import Log
from decodex.type import RawTraceCallResponse
from decodex.type import Tx


class BaseSearcher(ABC):
    @abstractmethod
    def get_tx(self, txhash: str) -> Tx:
        """
        Search a transaction by its hash. Return a TxDict.
        """
        raise NotImplementedError

    @abstractmethod
    def simluate_tx(
        self,
        from_address: str,
        to_address: str,
        value: Wei,
        data: str,
        gas: Union[Wei, Literal["auto"]] = "auto",
        gas_price: Union[Wei, Literal["auto"]] = "auto",
        timeout: int = 120,
    ) -> Tx:
        """
        Simluates a transaction and returns the trace result.

        Params
        ------
        from_address: str
            The address of the sender.
        to_address: str
            The address of the receiver.
        value: Wei
            The value of the transaction. In wei (int).
        data: str
            The data of the transaction. 0x prefixed.
        gas: Union[Wei, Literal["auto"]]
            The gas limit of the transaction. In wei (int). If "auto", the gas limit will be estimated.
        gas_price: Union[Wei, Literal["auto"]]
            The gas price of the transaction. In wei (int). If "auto", the gas price will be estimated.
        timeout: str
            The timeout of the transaction. In seconds (int).
        """
        raise NotImplementedError


class Web3Searcher(BaseSearcher):
    def __init__(self, provider: str = None) -> None:
        """
        Initialize a Web3Searcher with a Web3 instance or a Web3 http provider URI.

        Params
        ------
        provider: str
            The Web3 http provider URI. If None, the environment variable WEB3_PROVIDER_URI will be used. Otherwise, the default value is "http://localhost:8545".
        """
        if provider is None:
            provider = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")

        if isinstance(provider, str):
            w3 = Web3(Web3.HTTPProvider(provider))
            self.web3 = w3
        else:
            raise TypeError("provider must be a Web3 http provider URI")

    def get_tx(self, txhash: str, max_workers: int = 2) -> Tx:
        assert max_workers > 0, "max_workers must be positive"
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tx = executor.submit(self.web3.eth.get_transaction, txhash)
            tx_receipt = executor.submit(self.web3.eth.get_transaction_receipt, txhash)
            tx, tx_receipt = tx.result(), tx_receipt.result()

        blk = self.web3.eth.get_block(tx_receipt["blockNumber"])
        logs: list[Log] = [
            {
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
            "block_number": tx_receipt["blockNumber"],
            "block_timestamp": blk["timestamp"],
            "value": tx["value"],
            "gas_used": tx_receipt["gasUsed"],
            "gas_price": tx["gasPrice"],
            "input": tx["input"],
            "status": tx_receipt["status"],
            "logs": logs,
        }

    def simluate_tx(
        self,
        from_address: str,
        to_address: str,
        value: Wei,
        data: str,
        gas: Union[Wei, Literal["auto"]] = "auto",
        gas_price: Union[Wei, Literal["auto"]] = "auto",
        timeout: int = 120,
    ) -> Tx:
        """
        Simluates a transaction and returns the trace result.
        """
        blk = self.web3.eth.get_block("latest")
        if gas == "auto":
            gas = self.web3.eth.estimate_gas(
                {
                    "from": from_address,
                    "to": to_address,
                    "value": value,
                    "data": data,
                }
            )
            gas = int(gas * 1.5)
        if gas_price == "auto":
            gas_price = self.web3.eth.gas_price
        params = [
            {
                "from": from_address,
                "to": to_address,
                "value": hex(value),
                "data": data,
                "gas": hex(gas),
                "gasPrice": hex(gas_price),
            },
            "latest",
            {
                "timeout": f"{timeout}s",
                "tracer": "callTracer",
                "tracerConfig": {"withLog": True},
            },
        ]
        resp: RawTraceCallResponse = self.web3.provider.make_request("debug_traceCall", params)
        if resp.get("error", {}):
            raise RPCException(resp["error"]["code"], resp["error"]["message"])

        result = resp.get("result", {})
        tx: Tx = {
            "txhash": "Simulation result",
            "from": from_address,
            "to": to_address,
            "block_number": blk["number"],
            "block_timestamp": blk["timestamp"],
            "value": value,
            "gas_used": int(result["gasUsed"], 16),
            "gas_price": gas_price,
            "input": data,
            "status": 1,
            "logs": result.get("logs", []),
        }
        return tx


class SearcherFactory:
    @staticmethod
    def create(
        searcher_type: Literal["web3"],
        uri: str = None,
    ) -> BaseSearcher:
        if searcher_type == "web3":
            return Web3Searcher(provider=uri)
        else:
            raise NotImplementedError
