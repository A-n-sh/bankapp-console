from abc import ABC, abstractmethod


class Transaction(ABC):
    """Interface: any account that supports withdraw and deposit."""

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        pass

    @abstractmethod
    def deposit(self, amount: float) -> bool:
        pass
