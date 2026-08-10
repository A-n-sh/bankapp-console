from typing import List
from account import Account


class Customer:
    """A bank customer who owns one or more accounts."""

    def __init__(self, name: str, pin: str):
        self._name = name
        self._pin = pin
        self._accounts: List[Account] = []

    # --- getters ---
    def get_name(self) -> str:
        return self._name

    def verify_pin(self, pin: str) -> bool:
        return self._pin == pin

    def get_accounts(self) -> List[Account]:
        return self._accounts

    # --- setters ---
    def set_name(self, name: str) -> None:
        self._name = name

    def set_pin(self, pin: str) -> None:
        self._pin = pin

    # --- account management ---
    def add_account(self, account: Account) -> None:
        self._accounts.append(account)

    def get_account_by_id(self, account_id: int) -> Account | None:
        for acc in self._accounts:
            if acc.get_account_id() == account_id:
                return acc
        return None

    def __str__(self) -> str:
        return f"Customer: {self._name} ({len(self._accounts)} account(s))"
