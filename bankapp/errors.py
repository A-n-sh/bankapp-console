class BankError(Exception):
    """Base class for all user-facing banking errors."""


class ValidationError(BankError):
    pass


class InvalidAmountError(ValidationError):
    pass


class InsufficientFundsError(BankError):
    pass


class NotFoundError(BankError):
    pass


class DuplicateError(BankError):
    pass


class AuthenticationError(BankError):
    pass


class AccountLockedError(AuthenticationError):
    pass
