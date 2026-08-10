from models.account import Account

OVERDRAFT_LIMIT: float = 100.0  # final constant


class CheckingAccount(Account):
    """Checking account — withdraw allows overdraft up to OVERDRAFT_LIMIT."""

    def __init__(self, user_id: int, owner_name: str, initial_balance: float = 0.0):
        super().__init__(user_id, owner_name, initial_balance)

    def get_account_type(self) -> str:
        return "Checking"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if self._balance - amount < -OVERDRAFT_LIMIT:
            return False
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)
        return True
