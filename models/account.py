from abc import abstractmethod
from models.transaction import Transaction


class Account(Transaction):
    """Abstract base class for all account types."""

    def __init__(self, account_id: int, user_id: int, owner_name: str, balance: float = 0.0):
        self._account_id = account_id
        self._user_id = user_id
        self._owner_name = owner_name
        self._balance = balance

    def get_account_id(self) -> int:
        return self._account_id

    def get_user_id(self) -> int:
        return self._user_id

    def get_owner_name(self) -> str:
        return self._owner_name

    def get_balance(self) -> float:
        return self._balance

    def set_owner_name(self, name: str) -> None:
        self._owner_name = name

    @abstractmethod
    def get_account_type(self) -> str:
        pass

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self._balance += amount
        return True

    def to_dict(self) -> dict:
        return {
            "accountId": self._account_id,
            "userId": self._user_id,
            "userName": self._owner_name,
            "accountType": self.get_account_type(),
            "balance": round(self._balance, 2),
        }
