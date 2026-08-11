from datetime import datetime


class TransactionRecord:
    """A single logged transaction (deposit or withdrawal)."""

    def __init__(self, txn_id: int, account_id: int, txn_type: str, amount: float, created_at: datetime):
        self._txn_id = txn_id
        self._account_id = account_id
        self._txn_type = txn_type
        self._amount = amount
        self._created_at = created_at

    def get_txn_id(self) -> int:
        return self._txn_id

    def get_txn_type(self) -> str:
        return self._txn_type

    def get_amount(self) -> float:
        return self._amount

    def get_created_at(self) -> datetime:
        return self._created_at

    def to_dict(self) -> dict:
        return {
            "txnId": self._txn_id,
            "type": self._txn_type,
            "amount": self._amount,
            "date": self._created_at.strftime("%Y-%m-%d"),
        }
