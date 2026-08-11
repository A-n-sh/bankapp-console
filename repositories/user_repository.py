from typing import List, Optional
from db import db, next_id
from models.user import User


class UserRepository:

    def __init__(self):
        self._col = db.users

    def save(self, name: str, email: str) -> User:
        user_id = next_id("users")
        self._col.insert_one({"_id": user_id, "name": name, "email": email})
        return User(user_id, name, email)

    def find_by_id(self, user_id: int) -> Optional[User]:
        doc = self._col.find_one({"_id": user_id})
        if not doc:
            return None
        return User(doc["_id"], doc["name"], doc["email"])

    def find_all(self) -> List[User]:
        return [User(d["_id"], d["name"], d["email"]) for d in self._col.find()]
