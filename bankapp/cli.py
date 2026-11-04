from __future__ import annotations

import getpass
from collections.abc import Callable
from decimal import Decimal

from bankapp.errors import BankError
from bankapp.models import Account, AccountType, Customer
from bankapp.money import ZERO, fmt, parse_amount
from bankapp.service import BankService

RULE = "─" * 52


class ConsoleApp:
    """Interactive menu-driven front end for BankService."""

    def __init__(
        self,
        service: BankService,
        bank_name: str = "Citi Bank",
        input_fn: Callable[[str], str] = input,
        secret_fn: Callable[[str], str] = getpass.getpass,
        output: Callable[[str], None] = print,
    ):
        self.service = service
        self.bank_name = bank_name
        self._input = input_fn
        self._secret = secret_fn
        self._out = output

    # ── io helpers ───────────────────────────────────────────────────────────

    def say(self, text: str = "") -> None:
        self._out(f"  {text}" if text else "")

    def ask(self, prompt: str) -> str:
        return self._input(f"  {prompt}").strip()

    def ask_secret(self, prompt: str) -> str:
        return self._secret(f"  {prompt}").strip()

    def heading(self, title: str) -> None:
        self._out("")
        self.say(RULE)
        self.say(title)
        self.say(RULE)

    def menu(self, title: str, options: list[str]) -> str:
        self.heading(title)
        for i, option in enumerate(options, start=1):
            self.say(f"{i}. {option}")
        self._out("")
        return self.ask("Choose an option: ")

    def ask_amount(self, prompt: str, allow_zero: bool = False) -> Decimal:
        raw = self.ask(prompt)
        if allow_zero and raw in ("", "0"):
            return ZERO
        return parse_amount(raw)

    def ask_account_type(self) -> AccountType:
        types = list(AccountType)
        for i, kind in enumerate(types, start=1):
            self.say(f"{i}. {kind.label}")
        choice = self.ask("Account type: ")
        if choice.isdigit() and 1 <= int(choice) <= len(types):
            return types[int(choice) - 1]
        raise BankError("Invalid account type.")

    def pick_account(self, customer: Customer, prompt: str = "Select account: ") -> Account:
        accounts = self.service.accounts(customer)
        if not accounts:
            raise BankError("You have no accounts.")
        if len(accounts) == 1:
            return accounts[0]
        for i, account in enumerate(accounts, start=1):
            self.say(f"{i}. {account}")
        choice = self.ask(prompt)
        if choice.isdigit() and 1 <= int(choice) <= len(accounts):
            return accounts[int(choice) - 1]
        raise BankError("Invalid selection.")

    # ── entry point ──────────────────────────────────────────────────────────

    def run(self) -> None:
        self._out("")
        self.say("═" * 52)
        self.say(f"Welcome to {self.bank_name}".center(52))
        self.say("═" * 52)
        try:
            self._main_menu()
        except (EOFError, KeyboardInterrupt):
            self._out("")
        self.say(f"Thank you for banking with {self.bank_name}. Goodbye!")
        self._out("")

    def _main_menu(self) -> None:
        actions = {"1": self.register, "2": self.login}
        while True:
            choice = self.menu("Main menu", ["Open an account", "Log in", "Exit"])
            if choice == "3":
                return
            action = actions.get(choice)
            if action is None:
                self.say("Invalid option.")
                continue
            self._guard(action)

    def _guard(self, action: Callable[..., object], *args: object) -> None:
        try:
            action(*args)
        except BankError as exc:
            self.say(str(exc))

    # ── signed-out actions ───────────────────────────────────────────────────

    def register(self) -> None:
        self.heading("Open an account")
        full_name = self.ask("Full name: ")
        username = self.ask("Choose a username: ")
        pin = self.ask_secret("Choose a 4-6 digit PIN: ")
        if self.ask_secret("Confirm PIN: ") != pin:
            raise BankError("PINs do not match.")
        account_type = self.ask_account_type()
        deposit = self.ask_amount("Opening deposit (optional): $", allow_zero=True)
        customer, account = self.service.register(username, full_name, pin, account_type, deposit)
        self._out("")
        self.say(f"Welcome, {customer.full_name}! Your account number is #{account.number}.")
        self.say("You can now log in.")

    def login(self) -> None:
        self.heading("Log in")
        username = self.ask("Username: ")
        pin = self.ask_secret("PIN: ")
        customer = self.service.authenticate(username, pin)
        self.say(f"Welcome back, {customer.full_name}!")
        self.session(customer)

    # ── signed-in session ────────────────────────────────────────────────────

    def session(self, customer: Customer) -> None:
        actions = {
            "1": self.show_accounts,
            "2": self.deposit,
            "3": self.withdraw,
            "4": self.transfer,
            "5": self.show_history,
            "6": self.open_account,
            "7": self.change_pin,
        }
        options = [
            "Account overview",
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transaction history",
            "Open another account",
            "Change PIN",
            "Log out",
        ]
        while True:
            choice = self.menu(f"Signed in as {customer.username}", options)
            if choice == "8":
                self.say(f"Goodbye, {customer.full_name}!")
                return
            action = actions.get(choice)
            if action is None:
                self.say("Invalid option.")
                continue
            self._guard(action, customer)

    def show_accounts(self, customer: Customer) -> None:
        self.heading("Account overview")
        accounts = self.service.accounts(customer)
        total = sum((a.balance for a in accounts), ZERO)
        self.say(f"{'Account':<20}{'Balance':>14}{'Available':>14}")
        for account in accounts:
            name = f"{account.type.label} #{account.number}"
            self.say(f"{name:<20}{fmt(account.balance):>14}{fmt(account.available):>14}")
        self.say(f"{'Total':<20}{fmt(total):>14}")

    def deposit(self, customer: Customer) -> None:
        self.heading("Deposit")
        account = self.pick_account(customer)
        amount = self.ask_amount("Amount to deposit: $")
        txn = self.service.deposit(customer, account.id, amount)
        self.say(f"Deposited {fmt(txn.amount)}. New balance: {fmt(txn.balance_after)}")

    def withdraw(self, customer: Customer) -> None:
        self.heading("Withdraw")
        account = self.pick_account(customer)
        amount = self.ask_amount("Amount to withdraw: $")
        txn = self.service.withdraw(customer, account.id, amount)
        note = " (overdraft)" if txn.balance_after < 0 else ""
        self.say(f"Withdrew {fmt(txn.amount)}. New balance: {fmt(txn.balance_after)}{note}")

    def transfer(self, customer: Customer) -> None:
        self.heading("Transfer")
        source = self.pick_account(customer, "Transfer from: ")
        raw = self.ask("Destination account number: #").lstrip("#")
        if not raw.isdigit():
            raise BankError("Account numbers are digits only.")
        amount = self.ask_amount("Amount to transfer: $")
        out, _ = self.service.transfer(customer, source.id, int(raw), amount)
        self.say(f"Transferred {fmt(out.amount)} {out.memo.lower()}.")
        self.say(f"#{source.number} balance: {fmt(out.balance_after)}")

    def show_history(self, customer: Customer) -> None:
        self.heading("Transaction history")
        account = self.pick_account(customer)
        records = self.service.history(customer, account.id)
        if not records:
            self.say("No transactions yet.")
            return
        self.say(f"{account.type.label} #{account.number} — last {len(records)} transaction(s)")
        self.say(f"{'Date':<17}{'Type':<14}{'Amount':>12}{'Balance':>12}  Memo")
        for txn in records:
            when = txn.created_at.astimezone().strftime("%Y-%m-%d %H:%M")
            signed = txn.amount if txn.type.is_credit else -txn.amount
            self.say(
                f"{when:<17}{txn.type.label:<14}{fmt(signed):>12}"
                f"{fmt(txn.balance_after):>12}  {txn.memo}"
            )

    def open_account(self, customer: Customer) -> None:
        self.heading("Open another account")
        account_type = self.ask_account_type()
        deposit = self.ask_amount("Opening deposit (optional): $", allow_zero=True)
        account = self.service.open_account(customer, account_type, deposit)
        self.say(f"Opened {account.type.label} account #{account.number}.")

    def change_pin(self, customer: Customer) -> None:
        self.heading("Change PIN")
        current = self.ask_secret("Current PIN: ")
        new = self.ask_secret("New PIN: ")
        if self.ask_secret("Confirm new PIN: ") != new:
            raise BankError("PINs do not match.")
        self.service.change_pin(customer, current, new)
        self.say("PIN updated.")
