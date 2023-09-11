from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from multicall import Call
from multicall import Multicall

from decodex.convert.address import AddrTagger
from decodex.convert.signature import SignatureLookUp
from decodex.convert.token import ERC20TokenService
from decodex.type import Action
from decodex.type import AddLiquidityAction
from decodex.type import CollectAction
from decodex.type import EventHandleFunc
from decodex.type import EventPayload
from decodex.type import OwnerChangedAction
from decodex.type import PoolCreatedAction
from decodex.type import RemoveLiquidityAction
from decodex.type import SwapAction


class Events:
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        self._mc = mc
        self._tagger = tagger
        self._erc20_svc = ERC20TokenService(mc)


class UniswapEvents(Events):
    def _get_token_pair(self, pool_addr: str) -> Tuple[str, str]:
        result = self._mc.agg(
            [
                Call(
                    target=pool_addr,
                    function="token0()(address)",
                    request_id="token0",
                ),
                Call(
                    target=pool_addr,
                    function="token1()(address)",
                    request_id="token1",
                ),
            ]
        )
        token_map = {item["request_id"]: item["result"] for item in result}
        return token_map["token0"], token_map["token1"]


class UniswapV2Events(UniswapEvents):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def swap(self) -> Tuple[str, EventHandleFunc]:
        # Swap(address indexed sender,uint amount0In, uint amount1In, uint amount0Out, uint amount1Out, address indexed to);
        text_sig = "Swap(address,uint256,uint256,uint256,uint256,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token0_addr, token1_addr = self._get_token_pair(payload["address"])
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            params = payload["params"]
            amount0_diff = int(params["amount0Out"]) - int(params["amount0In"])
            amount1_diff = int(params["amount1Out"]) - int(params["amount1In"])
            if amount0_diff > 0:
                # pay token0, get token1
                pool, token0, token1 = self._tagger([payload["address"], token0, token1])
                return SwapAction(
                    pool=pool,
                    pay_token=token0,
                    pay_amount=abs(amount0_diff / 10 ** token0["decimals"]),
                    recv_token=token1,
                    recv_amount=abs(amount1_diff / 10 ** token1["decimals"]),
                )
            elif amount1_diff > 0:
                # pay token1, get token0
                pool, token0, token1 = self._tagger([payload["address"], token0, token1])
                return SwapAction(
                    pool=pool,
                    pay_token=token1,
                    pay_amount=abs(amount1_diff / 10 ** token1["decimals"]),
                    recv_token=token0,
                    recv_amount=abs(amount0_diff / 10 ** token0["decimals"]),
                )
            else:
                return None

        return text_sig, decoder

    def mint(self) -> Tuple[str, EventHandleFunc]:
        # Mint(address indexed sender, uint amount0, uint amount1);
        text_sig = "Mint(address,uint256,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token0_addr, token1_addr = self._get_token_pair(payload["address"])
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            params = payload["params"]
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            return AddLiquidityAction(
                pool=pool,
                token_0=token0,
                token_1=token1,
                amount_0=int(params["amount0"]) / 10 ** token0["decimals"],
                amount_1=int(params["amount1"]) / 10 ** token1["decimals"],
            )

        return text_sig, decoder

    def burn(self) -> Tuple[str, EventHandleFunc]:
        # Burn(address indexed sender, uint amount0, uint amount1, address indexed to);
        text_sig = "Burn(address,uint256,uint256,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token0_addr, token1_addr = self._get_token_pair(payload["address"])
            params = payload["params"]
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            return RemoveLiquidityAction(
                pool=pool,
                token_0=token0,
                token_1=token1,
                amount_0=int(params["amount0"]) / 10 ** token0["decimals"],
                amount_1=int(params["amount1"]) / 10 ** token1["decimals"],
            )

        return text_sig, decoder

    def pair_created(self) -> Tuple[str, EventHandleFunc]:
        # PairCreated(address indexed token0, address indexed token1, address pair, uint);
        text_sig = "PairCreated(address,address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0, token1 = self._erc20_svc.batch_get_erc20([params["token0"], params["token1"]])
            if token0 is None or token1 is None:
                return None
            token0, token1 = self._tagger([token0, token1])
            return PoolCreatedAction(
                token_0=token0,
                token_1=token1,
            )

        return text_sig, decoder


class UniswapV3Events(UniswapEvents):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def _get_tokens_by_position(self, pool_addr: str, pos_id: int) -> Tuple[str, str]:
        result = self._mc.agg(
            [
                Call(
                    target=pool_addr,
                    function="positions(uint256)(uint96,address,address,address,uint24,int24,int24,uint128,uint256,uint256,uint128,uint128)",
                    args=[pos_id],
                    request_id="positions",
                ),
            ]
        )
        if len(result) != 1:
            raise ValueError(f"Cannot find position {pos_id} in {pool_addr}")
        result = result[0]["result"]
        token0_addr, token1_addr = result[2], result[3]
        return token0_addr, token1_addr

    def pool_created(self) -> Tuple[str, EventHandleFunc]:
        # PoolCreated(address token0,address token1,uint24 fee,int24 tickSpacing,address pool)
        text_sig = "PoolCreated(address,address,uint24,int24,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0, token1 = self._erc20_svc.batch_get_erc20([params["token0"], params["token1"]])
            if token0 is None or token1 is None:
                return None
            token0, token1 = self._tagger([token0, token1])
            return PoolCreatedAction(
                token_0=token0,
                token_1=token1,
                fee=int(params["fee"]),
            )

        return text_sig, decoder

    def increase_liquidity(self) -> Tuple[str, EventHandleFunc]:
        # IncreaseLiquidity(uint256 indexed tokenId, uint128 liquidity, uint256 amount0, uint256 amount1);
        text_sig = "IncreaseLiquidity(uint256,uint128,uint256,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0_addr, token1_addr = self._get_tokens_by_position(payload["address"], int(params["tokenId"]))
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            return AddLiquidityAction(
                pool=pool,
                token_0=token0,
                token_1=token1,
                amount_0=int(params["amount0"]) / 10 ** token0["decimals"],
                amount_1=int(params["amount1"]) / 10 ** token1["decimals"],
            )

        return text_sig, decoder

    def decrease_liquidity(self) -> Tuple[str, EventHandleFunc]:
        # DecreaseLiquidity(uint256 indexed tokenId, uint128 liquidity, uint256 amount0, uint256 amount1);
        text_sig = "DecreaseLiquidity(uint256,uint128,uint256,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0_addr, token1_addr = self._get_tokens_by_position(payload["address"], int(params["tokenId"]))
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            return RemoveLiquidityAction(
                pool=pool,
                token_0=token0,
                token_1=token1,
                amount_0=abs(int(params["amount0"]) / 10 ** token0["decimals"]),
                amount_1=abs(int(params["amount1"]) / 10 ** token1["decimals"]),
            )

        return text_sig, decoder

    def swap(self) -> Tuple[str, EventHandleFunc]:
        # Swap(address sender,address recipient,int256 amount0,int256 amount1,uint160 sqrtPriceX96,uint128 liquidity,int24 tick)
        text_sig = "Swap(address,address,int256,int256,uint160,uint128,int24)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0_addr, token1_addr = self._get_token_pair(payload["address"])
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            amount0, amount1 = int(params["amount0"]), int(params["amount1"])

            if amount0 > 0 and amount1 < 0:
                # pay token0, get token1
                pool, token0, token1 = self._tagger([payload["address"], token0, token1])
                return SwapAction(
                    pool=pool,
                    pay_token=token0,
                    pay_amount=abs(amount0 / 10 ** token0["decimals"]),
                    recv_token=token1,
                    recv_amount=abs(amount1 / 10 ** token1["decimals"]),
                )
            elif amount1 > 0 and amount0 < 0:
                # pay token1, get token0
                pool, token0, token1 = self._tagger([payload["address"], token0, token1])
                return SwapAction(
                    pool=pool,
                    pay_token=token1,
                    pay_amount=abs(amount1 / 10 ** token1["decimals"]),
                    recv_token=token0,
                    recv_amount=abs(amount0 / 10 ** token0["decimals"]),
                )
            else:
                return None

        return text_sig, decoder

    def collect(self) -> Tuple[str, EventHandleFunc]:
        # Collect(address owner,int24 tickLower,int24 tickUpper,uint128 amount0,uint128 amount1)
        text_sig = "Collect(address,int24,int24,uint128,uint128)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0_addr, token1_addr = self._get_token_pair(
                payload["address"],
            )
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            amount0, amount1 = int(params["amount0"]), int(params["amount1"])
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            return CollectAction(
                pool=pool,
                token_0=token0,
                token_1=token1,
                amount_0=abs(amount0 / 10 ** token0["decimals"]),
                amount_1=abs(amount1 / 10 ** token1["decimals"]),
            )

        return text_sig, decoder

    def owner_changed(self) -> Tuple[str, EventHandleFunc]:
        # OwnerChanged(address oldOwner, address newOwner)
        text_sig = "OwnerChanged(address,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            pool, new_owner, old_owner = self._tagger([payload["address"], params["newOwner"], params["oldOwner"]])
            return OwnerChangedAction(
                pool=pool,
                new_owner=new_owner,
                old_owner=old_owner,
            )

        return text_sig, decoder


class BancorEV3Events(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def tokens_traded(self) -> Tuple[str, EventHandleFunc]:
        # TokensTraded (index_topic_1 bytes32 contextId, index_topic_2 address sourceToken, index_topic_3 address targetToken, uint256 sourceAmount, uint256 targetAmount, uint256 bntAmount, uint256 targetFeeAmount, uint256 bntFeeAmount, address trader)
        text_sig = "TokensTraded(bytes32,address,address,uint256,uint256,uint256,uint256,uint256,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token0_addr, token1_addr = params["sourceToken"], params["targetToken"]
            token0, token1 = self._erc20_svc.batch_get_erc20([token0_addr, token1_addr])
            if token0 is None or token1 is None:
                return None
            amount0, amount1 = int(params["sourceAmount"]), int(params["targetAmount"])
            pool, token0, token1 = self._tagger([payload["address"], token0, token1])
            if amount0 > 0 and amount1 < 0:
                # pay token0, get token1
                return SwapAction(
                    pool=pool,
                    pay_token=token0,
                    pay_amount=abs(amount0 / 10 ** token0["decimals"]),
                    recv_token=token1,
                    recv_amount=abs(amount1 / 10 ** token1["decimals"]),
                )
            elif amount1 > 0 and amount0 < 0:
                # pay token1, get token0
                return SwapAction(
                    pool=pool,
                    pay_token=token1,
                    pay_amount=abs(amount1 / 10 ** token1["decimals"]),
                    recv_token=token0,
                    recv_amount=abs(amount0 / 10 ** token0["decimals"]),
                )
            else:
                return None

        return text_sig, decoder


class CurveV2Events(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def token_exchange(self) -> Tuple[str, EventHandleFunc]:
        # TokenExchange (index_topic_1 address buyer, index_topic_2 address receiver, index_topic_3 address pool, address token_sold, address token_bought, uint256 amount_sold, uint256 amount_bought)
        text_sig = "TokenExchange(address,address,address,address,address,uint256,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            params = payload["params"]
            token_sold, token_bought = self._erc20_svc.batch_get_erc20([params["token_sold"], params["token_bought"]])
            if token_sold is None or token_bought is None:
                return None
            pool, token_sold, token_bought = self._tagger([params["pool"], token_sold, token_bought])
            amout_sold, amout_bought = int(params["amount_sold"]), int(params["amount_bought"])
            return SwapAction(
                pool=pool,
                pay_token=token_sold,
                pay_amount=amout_sold / 10 ** token_sold["decimals"],
                recv_token=token_bought,
                recv_amount=abs(amout_bought) / 10 ** token_bought["decimals"],
            )

        return text_sig, decoder
