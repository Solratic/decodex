from typing import Optional
from typing import Tuple

from multicall import Multicall

from .dex import Events
from decodex.convert.address import AddrTagger
from decodex.type import Action
from decodex.type import BorrowAction
from decodex.type import DepositAction
from decodex.type import DisableCollateralAction
from decodex.type import EnableCollateralAction
from decodex.type import EventHandleFunc
from decodex.type import EventPayload
from decodex.type import FlashloanAction
from decodex.type import RepayAction
from decodex.type import SupplyAction
from decodex.type import WithdrawAction


class AAVEV2Events(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def deposit(self) -> Tuple[str, EventHandleFunc]:
        # Deposit (index_topic_1 address reserve, address user, index_topic_2 address onBehalfOf, uint256 amount, index_topic_3 uint16 referral)
        text_sign = "Deposit(address,address,address,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return DepositAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sign, decoder

    def borrow(self) -> Tuple[str, EventHandleFunc]:
        # Borrow (index_topic_1 address reserve, address user, index_topic_2 address onBehalfOf, uint256 amount, uint256 borrowRateMode, uint256 borrowRate, index_topic_3 uint16 referral)
        text_sign = "Borrow(address,address,address,uint256,uint256,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return BorrowAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sign, decoder

    def withdraw(self) -> Tuple[str, EventHandleFunc]:
        # Withdraw (index_topic_1 address reserve, index_topic_2 address user, index_topic_3 address to, uint256 amount)
        text_sign = "Withdraw(address,address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return WithdrawAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sign, decoder

    def repay(self) -> Tuple[str, EventHandleFunc]:
        # Repay (index_topic_1 address reserve, index_topic_2 address user, index_topic_3 address repayer, uint256 amount)
        text_sign = "Repay(address,address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return RepayAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sign, decoder

    def flashloan(self) -> Tuple[str, EventHandleFunc]:
        # FlashLoan (index_topic_1 address target, index_topic_2 address initiator, index_topic_3 address asset, uint256 amount, uint256 premium, uint16 referralCode)
        text_sign = "FlashLoan(address,address,address,uint256,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["asset"]
            token = self._erc20_svc.get_erc20(token_addr)
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return FlashloanAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sign, decoder


class AAVEV3Events(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def supply(self) -> Tuple[str, EventHandleFunc]:
        # Supply (index_topic_1 address reserve, address user, index_topic_2 address onBehalfOf, uint256 amount, index_topic_3 uint16 referralCode)
        text_sig = "Supply(address,address,address,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return SupplyAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sig, decoder

    def borrow(self) -> Tuple[str, EventHandleFunc]:
        # Borrow (index_topic_1 address reserve, address user, index_topic_2 address onBehalfOf, uint256 amount, uint8 interestRateMode, uint256 borrowRate, index_topic_3 uint16 referralCode)
        text_sig = "Borrow(address,address,address,uint256,uint8,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            # (token_decimals,) = self._get_token_decimals(token_addr)
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return BorrowAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sig, decoder

    # def withdraw(self) -> Tuple[str, EventHandleFunc]:
    # pass (Duplicate with AAVEV2Events)

    def flashloan(self) -> Tuple[str, EventHandleFunc]:
        # FlashLoan(address indexed target, address initiator, address indexed asset, uint256 amount, DataTypes.InterestRateMode interestRateMode, uint256 premium, uint16 indexed referralCode);
        text_sig = "FlashLoan(address,address,address,uint256,uint8,uint256,uint16)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["asset"]
            token = self._erc20_svc.get_erc20(token_addr)
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return FlashloanAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sig, decoder

    def repay(self) -> Tuple[str, EventHandleFunc]:
        # event Repay(address indexed reserve, address indexed user, address indexed repayer, uint256 amount, bool useATokens);
        text_sig = "Repay(address,address,address,uint256,bool)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            pool, token = self._tagger([payload["address"], token])
            return RepayAction(
                pool=pool,
                token=token,
                amount=amount,
            )

        return text_sig, decoder

    def reserve_used_as_collateral_enabled(self) -> Tuple[str, EventHandleFunc]:
        # ReserveUsedAsCollateralEnabled (index_topic_1 address reserve, index_topic_2 address user)
        text_sig = "ReserveUsedAsCollateralEnabled(address,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            pool, token = self._tagger([payload["address"], token])
            return EnableCollateralAction(
                pool=pool,
                token=token,
            )

        return text_sig, decoder

    def reserve_used_as_collateral_disabled(self) -> Tuple[str, EventHandleFunc]:
        # ReserveUsedAsCollateralDisabled (index_topic_1 address reserve, index_topic_2 address user)
        text_sig = "ReserveUsedAsCollateralDisabled(address,address)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["reserve"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            pool, token = self._tagger([payload["address"], token])
            return DisableCollateralAction(
                pool=pool,
                token=token,
            )

        return text_sig, decoder


class CompoundV3Events(Events):
    def __init__(
        self,
        mc: Multicall,
        tagger: AddrTagger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(mc, tagger, *args, **kwargs)

    def supply_collateral(self) -> Tuple[str, EventHandleFunc]:
        # SupplyCollateral (index_topic_1 address from, index_topic_2 address dst, index_topic_3 address asset, uint256 amount)
        text_sig = "SupplyCollateral(address,address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["params"]["asset"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            amount = payload["params"]["amount"] / 10 ** token["decimals"]
            dst = payload["params"]["dst"]
            return SupplyAction(
                pool=dst,
                token=token,
                amount=amount,
            )

        return text_sig, decoder

    def withdraw(self) -> Tuple[str, EventHandleFunc]:
        # Withdraw (index_topic_1 address src, index_topic_2 address to, uint256 amount)
        text_sig = "Withdraw(address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["address"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            params = payload["params"]
            amount = params["__idx_2"] / 10 ** token["decimals"]
            src = params["__idx_0"]
            dst = params["__idx_1"]
            return WithdrawAction(
                pool=src,
                token=token,
                amount=amount,
                receiver=dst,
            )

        return text_sig, decoder

    def supply(self) -> Tuple[str, EventHandleFunc]:
        # Supply (index_topic_1 address from, index_topic_2 address dst, uint256 amount)
        text_sig = "Supply(address,address,uint256)"

        def decoder(payload: EventPayload) -> Optional[Action]:
            token_addr = payload["address"]
            token = self._erc20_svc.get_erc20(token_addr)
            if token is None:
                return None
            params = payload["params"]
            amount = params["__idx_2"] / 10 ** token["decimals"]
            dst = params["__idx_1"]
            return SupplyAction(
                pool=dst,
                token=token,
                amount=amount,
            )

        return text_sig, decoder
