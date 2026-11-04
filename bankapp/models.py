from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import ClassVar

from bankapp.errors import InsufficientFundsError, InvalidAmountError
from bankapp.money import ZERO, fmt, to_money

OVERDRAFT_LIMIT = Decimal("100.00")
SAVINGS_ANNUAL_RATE = Decimal("0.02")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"

    @property
    def label(self) -> str:
        return self.value.capitalize()


class TxnType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    INTEREST = "interest"

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").title()

    @property
    def is_credit(self) -> bool:
        return self in (TxnType.DEPOSIT, TxnType.TRANSFER_IN, TxnType.INTEREST)


@dataclass
class Customer:
    id: int | None
    username: str
    full_name: str
    pin_hash: str
    failed_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime = field(default_factory=utcnow)


@dataclass(frozen=True)
class Transaction:
    id: int | None
    account_id: int
    type: TxnType
    amount: Decimal
    balance_after: Decimal
    memo: str = ""
    created_at: datetime = field(default_factory=utcnow)


def _require_positive(amount: Decimal) -> Decimal:
    amount = to_money(amount)
    if amount <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")
    return amount


@dataclass
class Account(ABC):
    """Base class for all account types. Balances are always whole cents."""

    id: int | None
    customer_id: int
    balance: Decimal = ZERO
    created_at: datetime = field(default_factory=utcnow)

    type: ClassVar[AccountType]

    @property
    def number(self) -> str:
        return f"{self.id:06d}" if self.id is not None else "------"

    @property
    @abstractmethod
    def available(self) -> Decimal:
        """The most that can currently be withdrawn."""

    def deposit(self, amount: Decimal) -> Decimal:
        amount = _require_positive(amount)
        self.balance += amount
        return amount

    def withdraw(self, amount: Decimal) -> Decimal:
        amount = _require_positive(amount)
        if amount > self.available:
            raise InsufficientFundsError(
                f"Insufficient funds. You can withdraw up to {fmt(self.available)}."
            )
        self.balance -= amount
        return amount

    def __str__(self) -> str:
        return f"{self.type.label} #{self.number}  {fmt(self.balance)}"


@dataclass
class CheckingAccount(Account):
    """Checking account with a fixed overdraft allowance."""

    type: ClassVar[AccountType] = AccountType.CHECKING
    overdraft_limit: ClassVar[Decimal] = OVERDRAFT_LIMIT

    @property
    def available(self) -> Decimal:
        return max(self.balance + self.overdraft_limit, ZERO)


@dataclass
class SavingsAccount(Account):
    """Savings account: no overdraft, earns monthly interest."""

    type: ClassVar[AccountType] = AccountType.SAVINGS
    annual_rate: ClassVar[Decimal] = SAVINGS_ANNUAL_RATE

    @property
    def available(self) -> Decimal:
        return max(self.balance, ZERO)

    def monthly_interest(self) -> Decimal:
        if self.balance <= 0:
            return ZERO
        return to_money(self.balance * self.annual_rate / 12)


ACCOUNT_CLASSES: dict[AccountType, type[Account]] = {
    AccountType.CHECKING: CheckingAccount,
    AccountType.SAVINGS: SavingsAccount,
}
