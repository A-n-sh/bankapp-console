from models.account import Account

OVERDRAFT_LIMIT: float = 100.0  # final constant


class CheckingAccount(Account):
    """Checking account — withdraw allows overdraft up to OVERDRAFT_LIMIT."""

    def get_account_type(self) -> str:
        return "Checking"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if self._balance - amount < -OVERDRAFT_LIMIT:
            return False
        self._balance -= amount
        return True
