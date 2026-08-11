from datetime import datetime
from typing import List
from db import db, next_id
from models.transaction_record import TransactionRecord


class TransactionRepository:

    def __init__(self):
        self._col = db.transactions

    def save(self, account_id: int, txn_type: str, amount: float) -> TransactionRecord:
        txn_id = next_id("transactions")
        now = datetime.now()
        self._col.insert_one({
            "_id": txn_id,
            "account_id": account_id,
            "txn_type": txn_type,
            "amount": amount,
            "created_at": now,
        })
        return TransactionRecord(txn_id, account_id, txn_type, amount, now)

    def find_by_account_id(self, account_id: int) -> List[TransactionRecord]:
        docs = self._col.find({"account_id": account_id}).sort("created_at", 1)
        return [
            TransactionRecord(d["_id"], d["account_id"], d["txn_type"], float(d["amount"]), d["created_at"])
            for d in docs
        ]
