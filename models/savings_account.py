from models.account import Account


class SavingsAccount(Account):
    """Savings account — no overdraft allowed."""

    def __init__(self, user_id: int, owner_name: str, initial_balance: float = 0.0):
        super().__init__(user_id, owner_name, initial_balance)

    def get_account_type(self) -> str:
        return "Savings"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            return False
        if amount > self._balance:
            return False
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)
        return True
