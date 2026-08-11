from models.account import Account


class SavingsAccount(Account):
    """Savings account — no overdraft allowed."""

    def get_account_type(self) -> str:
        return "Savings"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if amount > self._balance:
            return False
        self._balance -= amount
        return True
