from repositories.user_repository import UserRepository


class UserService:

    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo

    def create_user(self, name: str, email: str):
        name = name.strip()
        email = email.strip()
        if not name or not email:
            return None, "name and email are required"
        user = self._user_repo.save(name, email)
        return user, None

    def get_user(self, user_id: int):
        user = self._user_repo.find_by_id(user_id)
        if not user:
            return None, "User not found"
        return user, None
