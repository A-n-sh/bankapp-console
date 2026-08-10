from account import Account


class SavingsAccount(Account):
    """Savings account — no overdraft allowed."""

    def __init__(self, owner_name: str, initial_balance: float = 0.0):
        super().__init__(owner_name, initial_balance)

    def get_account_type(self) -> str:
        return "Savings"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("  Withdrawal amount must be positive.")
            return False
        if amount > self._balance:
            print(
                f"  Insufficient funds. "
                f"Available balance: ${self._balance:,.2f}"
            )
            return False
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)
        print(f"  Withdrew ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True
