from datetime import datetime


class TransactionRecord:
    """A single logged transaction (deposit or withdrawal)."""

    _id_counter = 1  # static: shared across all TransactionRecord instances

    def __init__(self, account_id: int, txn_type: str, amount: float):
        self._txn_id = TransactionRecord._id_counter
        TransactionRecord._id_counter += 1
        self._account_id = account_id
        self._txn_type = txn_type  # "DEPOSIT" or "WITHDRAWAL"
        self._amount = amount
        self._created_at = datetime.now()

    # --- getters ---
    def get_txn_id(self) -> int:
        return self._txn_id

    def get_account_id(self) -> int:
        return self._account_id

    def get_txn_type(self) -> str:
        return self._txn_type

    def get_amount(self) -> float:
        return self._amount

    def get_created_at(self) -> datetime:
        return self._created_at

    def __str__(self) -> str:
        return (
            f"Txn #{self._txn_id:<4} | "
            f"{self._txn_type:<10} | "
            f"${self._amount:>10,.2f} | "
            f"{self._created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
