from typing import Dict
from models.user import User
from models.account import Account

# In-memory data store — replaces database
users: Dict[int, User] = {}
accounts: Dict[int, Account] = {}
