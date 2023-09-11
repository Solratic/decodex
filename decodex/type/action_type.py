from abc import abstractmethod
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

from .base import Action
from .tx_type import ERC20Compatible
from .tx_type import TaggedAddr
from decodex.utils import fmt_addr


@dataclass(frozen=True)
class ContractCreation(Action):
    deployer: TaggedAddr
    contract: TaggedAddr

    action: str = "contract_creation"

    def __str__(self):
        return f"{fmt_addr(self.deployer)} deployed {fmt_addr(self.contract)}"


@dataclass(frozen=True)
class UTF8Message(Action):
    """
    Represents a UTF8 message send from one address to another.
    """

    sender: TaggedAddr
    receiver: TaggedAddr
    message: str

    action: str = "utf8_message"

    def __str__(self):
        return f"{fmt_addr(self.sender)} sent message to {fmt_addr(self.receiver)}: {self.message}"


@dataclass(frozen=True)
class TransferAction(Action):
    """
    Represents a transfer of tokens from one address to another.
    """

    sender: TaggedAddr
    receiver: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "transfer"

    def __str__(self):
        return f"{fmt_addr(self.sender)} transferred {self.amount} {fmt_addr(self.token)} to {fmt_addr(self.receiver)}"


@dataclass(frozen=True)
class SwapAction(Action):
    """
    Represents a swap action between two tokens.
    """

    pool: TaggedAddr
    pay_token: ERC20Compatible
    recv_token: ERC20Compatible
    pay_amount: float
    recv_amount: float

    action: str = "swap"

    def __str__(self) -> str:
        tmpl = "Swap {pay_amount} {pay_token} for {recv_amount} {recv_token} on {pool}"
        return tmpl.format(
            pool=fmt_addr(self.pool),
            pay_amount=self.pay_amount,
            pay_token=fmt_addr(self.pay_token),
            recv_amount=self.recv_amount,
            recv_token=fmt_addr(self.recv_token),
        )


@dataclass(frozen=True)
class AddLiquidityAction(Action):
    """
    Represents an action to add liquidity to a pool.
    """

    pool: TaggedAddr
    token_0: ERC20Compatible
    token_1: ERC20Compatible
    amount_0: float
    amount_1: float

    action: str = "add_liquidity"

    def __str__(self) -> str:
        tmpl = "Add {amount_0} {token_0} and {amount_1} {token_1} liquidity to {pool}"
        return tmpl.format(
            amount_1=fmt_addr(self.amount_1),
            token_1=fmt_addr(self.token_1),
            pool=fmt_addr(self.pool),
            amount_0=self.amount_0,
            token_0=self.token_0,
        )


@dataclass(frozen=True)
class RemoveLiquidityAction(Action):
    """
    Represents an action to remove liquidity from a pool.
    """

    pool: TaggedAddr
    token_0: ERC20Compatible
    token_1: ERC20Compatible
    amount_0: float
    amount_1: float

    action: str = "remove_liquidity"

    def __str__(self) -> str:
        tmpl = "Remove {amount_0} {token_0} and {amount_1} {token_1} liquidity from {pool}"
        return tmpl.format(
            token_0=fmt_addr(self.token_0),
            token_1=fmt_addr(self.token_1),
            pool=fmt_addr(self.pool),
            amount_0=self.amount_0,
            amount_1=self.amount_1,
        )


@dataclass(frozen=True)
class PoolCreatedAction(Action):
    """
    Represents an action to create a pair.
    """

    token_0: ERC20Compatible
    token_1: ERC20Compatible
    fee: float = None

    action: str = "pool_created"

    def __str__(self) -> str:
        tmpl = "Create {token_0} / {token_1} pool"
        if not self.fee:
            return tmpl.format(
                token_0=fmt_addr(self.token_0),
                token_1=fmt_addr(self.token_1),
            )
        else:
            return tmpl + " with fee {fee}".format(
                token_0=fmt_addr(self.token_0),
                token_1=fmt_addr(self.token_1),
                fee=self.fee,
            )


@dataclass(frozen=True)
class CollectAction(Action):
    """
    Represents an action to collect tokens from a pool.
    """

    pool: TaggedAddr
    token_0: ERC20Compatible
    token_1: ERC20Compatible
    amount_0: float
    amount_1: float

    action: str = "collect"

    def __str__(self) -> str:
        tmpl = "Collect {amount_0} {token_0} and {amount_1} {token_1} from {pool}"
        return tmpl.format(
            token_0=fmt_addr(self.token_0),
            token_1=fmt_addr(self.token_1),
            pool=fmt_addr(self.pool),
            amount_0=self.amount_0,
            amount_1=self.amount_1,
        )


@dataclass(frozen=True)
class OwnerChangedAction(Action):
    """
    Represents an action to change the owner of a pool.
    """

    pool: TaggedAddr
    new_owner: TaggedAddr
    old_owner: TaggedAddr

    action: str = "owner_changed"

    def __str__(self) -> str:
        tmpl = "Change owner of {pool} from {old_owner} to {new_owner}"
        return tmpl.format(
            pool=fmt_addr(self.pool),
            old_owner=fmt_addr(self.old_owner),
            new_owner=fmt_addr(self.new_owner),
        )


@dataclass(frozen=True)
class BorrowAction(Action):
    """
    Represents an action to borrow tokens from a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "borrow"

    def __str__(self) -> str:
        tmpl = "Borrow {amount} {token} from {pool}"
        return tmpl.format(
            amount=self.amount,
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class RepayAction(Action):
    """
    Represents an action to repay tokens to a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "repay"

    def __str__(self) -> str:
        tmpl = "Repay {amount} {token} to {pool}"
        return tmpl.format(
            amount=self.amount,
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class DepositAction(Action):
    """
    Deposit tokens to a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "deposit"

    def __str__(self) -> str:
        tmpl = "Deposit {amount} {token} to {pool}"
        return tmpl.format(
            amount=self.amount,
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class WithdrawAction(Action):
    """
    Withdraw tokens from a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float
    receiver: TaggedAddr = None

    action: str = "withdraw"

    def __str__(self) -> str:
        if not self.receiver:
            tmpl = "Withdraw {amount} {token} from {pool}"
            return tmpl.format(
                amount=self.amount,
                token=fmt_addr(self.token),
                pool=fmt_addr(self.pool),
            )
        else:
            tmpl = "Withdraw {amount} {token} from {pool} to {receiver}"
            return tmpl.format(
                amount=self.amount,
                token=fmt_addr(self.token),
                pool=fmt_addr(self.pool),
            )


@dataclass(frozen=True)
class FlashloanAction(Action):
    """
    Represents an action to flashloan tokens from a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "flashloan"

    def __str__(self) -> str:
        tmpl = "Flashloan {amount} {token} from {pool}"
        return tmpl.format(
            amount=self.amount,
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class EnableCollateralAction(Action):
    """
    Enable a token as collateral in a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible

    action: str = "enable_collateral"

    def __str__(self) -> str:
        tmpl = "Enable {token} as collateral in {pool}"
        return tmpl.format(
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class DisableCollateralAction(Action):
    """
    Disable a token as collateral in a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible

    action: str = "disable_collateral"

    def __str__(self) -> str:
        tmpl = "Disable {token} as collateral in {pool}"
        return tmpl.format(
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
        )


@dataclass(frozen=True)
class SupplyAction(Action):
    """
    Supply tokens to a lending pool.
    """

    pool: TaggedAddr
    token: ERC20Compatible
    amount: float

    action: str = "supply"

    def __str__(self) -> str:
        tmpl = "Supply {amount} {token} to {pool}"
        return tmpl.format(
            token=fmt_addr(self.token),
            pool=fmt_addr(self.pool),
            amount=self.amount,
        )
