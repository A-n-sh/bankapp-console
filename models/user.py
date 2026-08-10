class User:
    """A bank user (name + email)."""

    _id_counter = 1  # static

    def __init__(self, name: str, email: str):
        self._user_id = User._id_counter
        User._id_counter += 1
        self._name = name
        self._email = email

    # --- getters ---
    def get_user_id(self) -> int:
        return self._user_id

    def get_name(self) -> str:
        return self._name

    def get_email(self) -> str:
        return self._email

    # --- setters ---
    def set_name(self, name: str) -> None:
        self._name = name

    def set_email(self, email: str) -> None:
        self._email = email

    def to_dict(self) -> dict:
        return {
            "userId": self._user_id,
            "name": self._name,
            "email": self._email,
        }
