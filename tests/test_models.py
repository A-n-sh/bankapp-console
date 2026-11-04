from decimal import Decimal

import pytest

from bankapp.errors import InsufficientFundsError, InvalidAmountError
from bankapp.models import CheckingAccount, SavingsAccount


def test_checking_allows_overdraft_up_to_limit():
    acc = CheckingAccount(id=1, customer_id=1, balance=Decimal("50.00"))
    acc.withdraw(Decimal("150.00"))
    assert acc.balance == Decimal("-100.00")
    assert acc.available == Decimal("0.00")
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(Decimal("0.01"))


def test_savings_has_no_overdraft():
    acc = SavingsAccount(id=1, customer_id=1, balance=Decimal("20.00"))
    with pytest.raises(InsufficientFundsError):
        acc.withdraw(Decimal("20.01"))
    acc.withdraw(Decimal("20.00"))
    assert acc.balance == Decimal("0.00")


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-1")])
def test_non_positive_amounts_rejected(amount):
    acc = SavingsAccount(id=1, customer_id=1)
    with pytest.raises(InvalidAmountError):
        acc.deposit(amount)


def test_monthly_interest():
    acc = SavingsAccount(id=1, customer_id=1, balance=Decimal("1200.00"))
    assert acc.monthly_interest() == Decimal("2.00")
    assert SavingsAccount(id=2, customer_id=1).monthly_interest() == Decimal("0.00")


def test_account_number_and_str():
    acc = CheckingAccount(id=7, customer_id=1, balance=Decimal("5"))
    assert acc.number == "000007"
    assert str(acc) == "Checking #000007  $5.00"
