from typing import Dict, List, Set
from customer import Customer


class Bank:
    """The bank — holds all customers in a map and provides lookup."""

    def __init__(self, name: str):
        self._name = name
        self._customers: Dict[str, Customer] = {}  # map: lowercase name -> Customer

    def get_name(self) -> str:
        return self._name

    def add_customer(self, customer: Customer) -> None:
        self._customers[customer.get_name().lower()] = customer

    def find_customer(self, name: str) -> Customer | None:
        return self._customers.get(name.strip().lower())

    def get_all_customers(self) -> List[Customer]:
        return list(self._customers.values())

    def get_account_types(self) -> Set[str]:
        """Return unique account types registered across all customers."""
        types: Set[str] = set()
        for customer in self._customers.values():
            for account in customer.get_accounts():
                types.add(account.get_account_type())
        return types
