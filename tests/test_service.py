from decimal import Decimal

import pytest

from bankapp.errors import (
    AccountLockedError,
    AuthenticationError,
    DuplicateError,
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)
from bankapp.models import AccountType, TxnType
from bankapp.service import BankService, seed_demo
from bankapp.storage import Repository

D = Decimal


@pytest.fixture
def alice(service):
    customer, _ = service.register("alice", "Alice Smith", "1234", initial_deposit=D("100"))
    return customer


def test_register_creates_customer_and_account(service, alice):
    (account,) = service.accounts(alice)
    assert account.type is AccountType.CHECKING
    assert account.balance == D("100.00")
    (txn,) = service.history(alice, account.id)
    assert txn.type is TxnType.DEPOSIT and txn.memo == "Opening deposit"


def test_register_validation(service, alice):
    with pytest.raises(DuplicateError):
        service.register("ALICE", "Someone", "9999")
    with pytest.raises(ValidationError):
        service.register("a b", "Someone", "9999")
    with pytest.raises(ValidationError):
        service.register("carol", "   ", "9999")
    with pytest.raises(ValidationError):
        service.register("carol", "Carol", "12")


def test_authenticate_is_case_insensitive(service, alice):
    assert service.authenticate("Alice", "1234").id == alice.id


def test_lockout_after_three_failures(service, alice, clock):
    for _ in range(2):
        with pytest.raises(AuthenticationError) as exc:
            service.authenticate("alice", "0000")
        assert not isinstance(exc.value, AccountLockedError)
    with pytest.raises(AccountLockedError):
        service.authenticate("alice", "0000")
    with pytest.raises(AccountLockedError):
        service.authenticate("alice", "1234")
    clock.advance(minutes=6)
    assert service.authenticate("alice", "1234").id == alice.id


def test_unknown_user(service):
    with pytest.raises(AuthenticationError):
        service.authenticate("nobody", "1234")


def test_change_pin(service, alice):
    with pytest.raises(AuthenticationError):
        service.change_pin(alice, "9999", "5555")
    service.change_pin(alice, "1234", "5555")
    service.authenticate("alice", "5555")


def test_deposit_and_withdraw_persist(service, repo, alice):
    (account,) = service.accounts(alice)
    service.deposit(alice, account.id, D("25.50"))
    txn = service.withdraw(alice, account.id, D("200"))
    assert txn.balance_after == D("-74.50")
    assert repo.get_account(account.id).balance == D("-74.50")
    with pytest.raises(InsufficientFundsError):
        service.withdraw(alice, account.id, D("30"))
    assert repo.get_account(account.id).balance == D("-74.50")


def test_cannot_touch_other_customers_accounts(service, alice):
    bob, bob_acc = service.register("bob", "Bob", "5678")
    with pytest.raises(NotFoundError):
        service.deposit(alice, bob_acc.id, D("1"))
    with pytest.raises(NotFoundError):
        service.history(alice, bob_acc.id)


def test_transfer_between_customers(service, repo, alice):
    _, bob_acc = service.register("bob", "Bob", "5678")
    (src,) = service.accounts(alice)
    out, into = service.transfer(alice, src.id, bob_acc.id, D("40"))
    assert out.type is TxnType.TRANSFER_OUT and out.memo == f"To #{bob_acc.number}"
    assert into.type is TxnType.TRANSFER_IN and into.memo == f"From #{src.number}"
    assert repo.get_account(src.id).balance == D("60.00")
    assert repo.get_account(bob_acc.id).balance == D("40.00")


def test_failed_transfer_changes_nothing(service, repo, alice):
    savings = service.open_account(alice, AccountType.SAVINGS, D("10"))
    (checking, _) = service.accounts(alice)
    with pytest.raises(InsufficientFundsError):
        service.transfer(alice, savings.id, checking.id, D("10.01"))
    with pytest.raises(NotFoundError):
        service.transfer(alice, savings.id, 9999, D("1"))
    with pytest.raises(ValidationError):
        service.transfer(alice, savings.id, savings.id, D("1"))
    assert repo.get_account(savings.id).balance == D("10.00")
    assert len(service.history(alice, savings.id)) == 1


def test_apply_monthly_interest(service, alice):
    savings = service.open_account(alice, AccountType.SAVINGS, D("1200"))
    (txn,) = service.apply_monthly_interest()
    assert txn.account_id == savings.id
    assert txn.type is TxnType.INTEREST
    assert txn.balance_after == D("1202.00")


def test_data_survives_restart(tmp_path):
    db = tmp_path / "bank.db"
    repo = Repository(db)
    seed_demo(BankService(repo))
    repo.close()

    repo = Repository(db)
    service = BankService(repo)
    alice = service.authenticate("alice", "1234")
    balances = sorted(a.balance for a in service.accounts(alice))
    assert balances == [D("500.00"), D("1200.00")]
    repo.close()
