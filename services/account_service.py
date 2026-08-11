from repositories.user_repository import UserRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository

VALID_TYPES = {"CHECKING", "SAVINGS"}


class AccountService:

    def __init__(
        self,
        user_repo: UserRepository,
        account_repo: AccountRepository,
        txn_repo: TransactionRepository,
    ):
        self._user_repo = user_repo
        self._account_repo = account_repo
        self._txn_repo = txn_repo

    def createAccount(self, user_id: int, account_type: str):
        user = self._user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        account_type = str(account_type).upper()
        if account_type not in VALID_TYPES:
            return None, "accountType must be CHECKING or SAVINGS"
        db_type = "Checking" if account_type == "CHECKING" else "Savings"
        account = self._account_repo.save(user_id, user.get_name(), db_type)
        return account, None

    def getAccount(self, account_id: int):
        account = self._account_repo.find_by_id(account_id)
        if not account:
            return None, "Account not found"
        return account, None

    def deposit(self, account_id: int, amount):
        account = self._account_repo.find_by_id(account_id)
        if not account:
            return None, "Account not found"
        if not isinstance(amount, (int, float)) or amount <= 0:
            return None, "amount must be a positive number"
        account.deposit(amount)
        self._account_repo.update_balance(account_id, account.get_balance())
        self._txn_repo.save(account_id, "DEPOSIT", amount)
        return account, None

    def withdraw(self, account_id: int, amount):
        account = self._account_repo.find_by_id(account_id)
        if not account:
            return None, "Account not found"
        if not isinstance(amount, (int, float)) or amount <= 0:
            return None, "amount must be a positive number"
        if not account.withdraw(amount):
            return None, "Insufficient funds"
        self._account_repo.update_balance(account_id, account.get_balance())
        self._txn_repo.save(account_id, "WITHDRAWAL", amount)
        return account, None

    def getTransactions(self, account_id: int):
        account = self._account_repo.find_by_id(account_id)
        if not account:
            return None, "Account not found"
        return self._txn_repo.find_by_account_id(account_id), None
