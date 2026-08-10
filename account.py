from abc import abstractmethod
from typing import List
from transaction import Transaction
from transaction_record import TransactionRecord


class Account(Transaction):
    """Abstract base class for all account types."""

    _id_counter = 1  # static: shared across all Account instances

    def __init__(self, owner_name: str, initial_balance: float = 0.0):
        self._account_id = Account._id_counter
        Account._id_counter += 1
        self._owner_name = owner_name
        self._balance = initial_balance
        self._transactions: List[TransactionRecord] = []

    # --- getters ---
    def get_account_id(self) -> int:
        return self._account_id

    def get_owner_name(self) -> str:
        return self._owner_name

    def get_balance(self) -> float:
        return self._balance

    # --- setters ---
    def set_owner_name(self, name: str) -> None:
        self._owner_name = name

    # --- abstract ---
    @abstractmethod
    def get_account_type(self) -> str:
        pass

    # --- transaction history ---
    def _record_transaction(self, txn_type: str, amount: float) -> None:
        self._transactions.append(TransactionRecord(self._account_id, txn_type, amount))

    def get_transactions(self) -> List[TransactionRecord]:
        return self._transactions

    # --- shared logic ---
    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("  Deposit amount must be positive.")
            return False
        self._balance += amount
        self._record_transaction("DEPOSIT", amount)
        print(f"  Deposited ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True

    def __str__(self) -> str:
        return (
            f"[{self.get_account_type()}] "
            f"Account #{self._account_id} | "
            f"Balance: ${self._balance:,.2f}"
        )
