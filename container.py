from repositories.user_repository import UserRepository
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository
from services.user_service import UserService
from services.account_service import AccountService

user_repo = UserRepository()
account_repo = AccountRepository()
txn_repo = TransactionRepository()

user_service = UserService(user_repo)
account_service = AccountService(user_repo, account_repo, txn_repo)
