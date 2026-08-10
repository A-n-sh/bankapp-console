from account import Account

OVERDRAFT_LIMIT: float = 100.0  # final constant


class CheckingAccount(Account):
    """Checking account — withdraw allows overdraft up to OVERDRAFT_LIMIT."""

    def __init__(self, owner_name: str, initial_balance: float = 0.0):
        super().__init__(owner_name, initial_balance)

    def get_account_type(self) -> str:
        return "Checking"

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("  Withdrawal amount must be positive.")
            return False
        if self._balance - amount < -OVERDRAFT_LIMIT:
            print(
                f"  Insufficient funds. "
                f"Max you can withdraw (with ${OVERDRAFT_LIMIT:.2f} overdraft): "
                f"${self._balance + OVERDRAFT_LIMIT:,.2f}"
            )
            return False
        self._balance -= amount
        self._record_transaction("WITHDRAWAL", amount)
        if self._balance < 0:
            print(
                f"  Withdrew ${amount:,.2f}. "
                f"Balance: ${self._balance:,.2f} (overdraft)"
            )
        else:
            print(f"  Withdrew ${amount:,.2f}. New balance: ${self._balance:,.2f}")
        return True
