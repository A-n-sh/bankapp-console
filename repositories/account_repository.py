from typing import List, Optional
from db import db, next_id
from models.account import Account
from models.checking_account import CheckingAccount
from models.savings_account import SavingsAccount


class AccountRepository:

    def __init__(self):
        self._col = db.accounts

    def save(self, user_id: int, owner_name: str, account_type: str) -> Account:
        account_id = next_id("accounts")
        self._col.insert_one({
            "_id": account_id,
            "user_id": user_id,
            "owner_name": owner_name,
            "balance": 0.0,
            "account_type": account_type,
        })
        return self._hydrate({
            "_id": account_id,
            "user_id": user_id,
            "owner_name": owner_name,
            "balance": 0.0,
            "account_type": account_type,
        })

    def find_by_id(self, account_id: int) -> Optional[Account]:
        doc = self._col.find_one({"_id": account_id})
        if not doc:
            return None
        return self._hydrate(doc)

    def update_balance(self, account_id: int, new_balance: float) -> None:
        self._col.update_one({"_id": account_id}, {"$set": {"balance": new_balance}})

    def find_all(self) -> List[Account]:
        return [self._hydrate(d) for d in self._col.find()]

    def _hydrate(self, doc) -> Account:
        if doc["account_type"] == "Checking":
            return CheckingAccount(doc["_id"], doc["user_id"], doc["owner_name"], float(doc["balance"]))
        return SavingsAccount(doc["_id"], doc["user_id"], doc["owner_name"], float(doc["balance"]))
