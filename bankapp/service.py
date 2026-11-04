from __future__ import annotations

import re
from collections.abc import Callable
from datetime import datetime, timedelta
from decimal import Decimal

from bankapp.errors import (
    AccountLockedError,
    AuthenticationError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from bankapp.models import (
    ACCOUNT_CLASSES,
    Account,
    AccountType,
    Customer,
    SavingsAccount,
    Transaction,
    TxnType,
    utcnow,
)
from bankapp.money import ZERO, to_money
from bankapp.security import hash_pin, validate_pin, verify_pin
from bankapp.storage import Repository

MAX_PIN_ATTEMPTS = 3
LOCKOUT = timedelta(minutes=5)
_USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


class BankService:
    """All banking operations. The UI layer only talks to this class."""

    def __init__(self, repo: Repository, now: Callable[[], datetime] = utcnow):
        self._repo = repo
        self._now = now

    # ── customers ────────────────────────────────────────────────────────────

    def register(
        self,
        username: str,
        full_name: str,
        pin: str,
        account_type: AccountType = AccountType.CHECKING,
        initial_deposit: Decimal = ZERO,
    ) -> tuple[Customer, Account]:
        username = username.strip()
        full_name = " ".join(full_name.split())
        if not _USERNAME_RE.match(username):
            raise ValidationError(
                "Username must be 3-20 characters: letters, numbers or underscores."
            )
        if not full_name:
            raise ValidationError("Full name cannot be empty.")
        validate_pin(pin)
        if self._repo.find_customer(username):
            raise DuplicateError(f"Username '{username}' is already taken.")

        with self._repo.atomic():
            customer = self._repo.add_customer(
                Customer(
                    id=None,
                    username=username,
                    full_name=full_name,
                    pin_hash=hash_pin(pin),
                    created_at=self._now(),
                )
            )
            account = self._open(customer, account_type, initial_deposit)
        return customer, account

    def authenticate(self, username: str, pin: str) -> Customer:
        customer = self._repo.find_customer(username)
        if customer is None:
            raise AuthenticationError("Invalid username or PIN.")

        now = self._now()
        if customer.locked_until and customer.locked_until > now:
            raise AccountLockedError(_locked_message(customer.locked_until - now))

        if not verify_pin(pin, customer.pin_hash):
            customer.failed_attempts += 1
            locked = customer.failed_attempts >= MAX_PIN_ATTEMPTS
            if locked:
                customer.failed_attempts = 0
                customer.locked_until = now + LOCKOUT
            with self._repo.atomic():
                self._repo.update_customer(customer)
            if locked:
                raise AccountLockedError(_locked_message(LOCKOUT))
            remaining = MAX_PIN_ATTEMPTS - customer.failed_attempts
            raise AuthenticationError(f"Invalid username or PIN. {remaining} attempt(s) remaining.")

        customer.failed_attempts = 0
        customer.locked_until = None
        with self._repo.atomic():
            self._repo.update_customer(customer)
        return customer

    def change_pin(self, customer: Customer, current_pin: str, new_pin: str) -> None:
        if not verify_pin(current_pin, customer.pin_hash):
            raise AuthenticationError("Current PIN is incorrect.")
        validate_pin(new_pin)
        customer.pin_hash = hash_pin(new_pin)
        with self._repo.atomic():
            self._repo.update_customer(customer)

    # ── accounts ─────────────────────────────────────────────────────────────

    def open_account(
        self, customer: Customer, account_type: AccountType, initial_deposit: Decimal = ZERO
    ) -> Account:
        with self._repo.atomic():
            return self._open(customer, account_type, initial_deposit)

    def accounts(self, customer: Customer) -> list[Account]:
        return self._repo.list_accounts(customer.id)

    def get_account(self, customer: Customer, account_id: int) -> Account:
        account = self._repo.get_account(account_id)
        if account is None or account.customer_id != customer.id:
            raise NotFoundError(f"Account #{account_id:06d} not found.")
        return account

    def history(self, customer: Customer, account_id: int, limit: int = 20) -> list[Transaction]:
        self.get_account(customer, account_id)
        return self._repo.list_transactions(account_id, limit)

    # ── money movement ───────────────────────────────────────────────────────

    def deposit(self, customer: Customer, account_id: int, amount: Decimal) -> Transaction:
        account = self.get_account(customer, account_id)
        with self._repo.atomic():
            return self._credit(account, amount, TxnType.DEPOSIT)

    def withdraw(self, customer: Customer, account_id: int, amount: Decimal) -> Transaction:
        account = self.get_account(customer, account_id)
        with self._repo.atomic():
            return self._debit(account, amount, TxnType.WITHDRAWAL)

    def transfer(
        self, customer: Customer, from_id: int, to_id: int, amount: Decimal
    ) -> tuple[Transaction, Transaction]:
        """Move money from one of the customer's accounts to any account."""
        if from_id == to_id:
            raise ValidationError("Cannot transfer to the same account.")
        source = self.get_account(customer, from_id)
        destination = self._repo.get_account(to_id)
        if destination is None:
            raise NotFoundError(f"Destination account #{to_id:06d} not found.")
        with self._repo.atomic():
            out = self._debit(
                source, amount, TxnType.TRANSFER_OUT, memo=f"To #{destination.number}"
            )
            into = self._credit(
                destination, amount, TxnType.TRANSFER_IN, memo=f"From #{source.number}"
            )
        return out, into

    def apply_monthly_interest(self) -> list[Transaction]:
        """Credit one month of interest to every savings account."""
        applied = []
        with self._repo.atomic():
            for account in self._repo.list_accounts():
                if isinstance(account, SavingsAccount):
                    interest = account.monthly_interest()
                    if interest > 0:
                        applied.append(self._credit(account, interest, TxnType.INTEREST))
        return applied

    # ── internals (callers must hold a transaction) ──────────────────────────

    def _open(
        self, customer: Customer, account_type: AccountType, initial_deposit: Decimal
    ) -> Account:
        cls = ACCOUNT_CLASSES[AccountType(account_type)]
        account = self._repo.add_account(
            cls(id=None, customer_id=customer.id, created_at=self._now())
        )
        if to_money(initial_deposit) > 0:
            self._credit(account, initial_deposit, TxnType.DEPOSIT, memo="Opening deposit")
        return account

    def _credit(
        self, account: Account, amount: Decimal, kind: TxnType, memo: str = ""
    ) -> Transaction:
        amount = account.deposit(amount)
        return self._record(account, amount, kind, memo)

    def _debit(
        self, account: Account, amount: Decimal, kind: TxnType, memo: str = ""
    ) -> Transaction:
        amount = account.withdraw(amount)
        return self._record(account, amount, kind, memo)

    def _record(self, account: Account, amount: Decimal, kind: TxnType, memo: str) -> Transaction:
        self._repo.save_balance(account)
        return self._repo.add_transaction(
            Transaction(
                id=None,
                account_id=account.id,
                type=kind,
                amount=amount,
                balance_after=account.balance,
                memo=memo,
                created_at=self._now(),
            )
        )


def _locked_message(remaining: timedelta) -> str:
    minutes = max(1, -(-int(remaining.total_seconds()) // 60))
    return f"Too many failed attempts. Try again in {minutes} minute(s)."


def seed_demo(service: BankService) -> None:
    """Create demo customers (alice / 1234, bob / 5678)."""
    alice, _ = service.register(
        "alice", "Alice Smith", "1234", AccountType.CHECKING, Decimal("500.00")
    )
    service.open_account(alice, AccountType.SAVINGS, Decimal("1200.00"))
    service.register("bob", "Bob Jones", "5678", AccountType.CHECKING, Decimal("250.00"))
