from bank import Bank
from customer import Customer
from checking_account import CheckingAccount
from savings_account import SavingsAccount
from account import Account


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_amount(prompt: str) -> float | None:
    """Prompt for a dollar amount. Returns None if invalid."""
    raw = input(prompt).strip()
    try:
        return float(raw)
    except ValueError:
        print("  Invalid amount. Please enter a number.")
        return None


def pick_account(customer: Customer) -> Account | None:
    """Show the customer's accounts and let them pick one by number."""
    accounts = customer.get_accounts()
    if not accounts:
        print("  You have no accounts.")
        return None

    print()
    for i, acc in enumerate(accounts, start=1):
        print(f"  {i}. {acc}")
    print()

    raw = input("  Select account (number): ").strip()
    try:
        idx = int(raw) - 1
        if 0 <= idx < len(accounts):
            return accounts[idx]
        print("  Invalid selection.")
        return None
    except ValueError:
        print("  Invalid input.")
        return None


# ── Menus ─────────────────────────────────────────────────────────────────────

def show_accounts(customer: Customer) -> None:
    print()
    accounts = customer.get_accounts()
    if not accounts:
        print("  No accounts found.")
        return
    print(f"  Accounts for {customer.get_name()}:")
    for acc in accounts:
        print(f"    {acc}")


def do_deposit(customer: Customer) -> None:
    print("\n  -- Deposit --")
    account = pick_account(customer)
    if not account:
        return
    amount = get_amount("  Amount to deposit: $")
    if amount is not None:
        account.deposit(amount)


def do_withdraw(customer: Customer) -> None:
    print("\n  -- Withdraw --")
    account = pick_account(customer)
    if not account:
        return
    amount = get_amount("  Amount to withdraw: $")
    if amount is not None:
        account.withdraw(amount)


def do_transfer(customer: Customer) -> None:
    print("\n  -- Transfer --")
    accounts = customer.get_accounts()
    if len(accounts) < 2:
        print("  You need at least 2 accounts to transfer.")
        return

    print("  Transfer FROM:")
    source = pick_account(customer)
    if not source:
        return

    print("  Transfer TO:")
    destination = pick_account(customer)
    if not destination:
        return

    if source.get_account_id() == destination.get_account_id():
        print("  Cannot transfer to the same account.")
        return

    amount = get_amount("  Amount to transfer: $")
    if amount is None:
        return

    if source.withdraw(amount):
        destination.deposit(amount)
        print("  Transfer complete.")


def show_transactions(customer: Customer) -> None:
    print("\n  -- Transaction History --")
    account = pick_account(customer)
    if not account:
        return
    records = account.get_transactions()
    if not records:
        print("  No transactions yet.")
        return
    print()
    print(f"  {'Txn':<8} {'Type':<12} {'Amount':>12}  {'Date & Time'}")
    print(f"  {'-'*8} {'-'*12} {'-'*12}  {'-'*19}")
    for r in records:
        print(
            f"  Txn #{r.get_txn_id():<4} "
            f"{r.get_txn_type():<12} "
            f"${r.get_amount():>10,.2f}  "
            f"{r.get_created_at().strftime('%Y-%m-%d %H:%M:%S')}"
        )


# ── Login ─────────────────────────────────────────────────────────────────────

def login(bank: Bank) -> Customer | None:
    print()
    name = input("  Enter your name: ").strip()
    customer = bank.find_customer(name)
    if not customer:
        print("  Customer not found.")
        return None

    for attempt in range(3):
        pin = input("  Enter PIN: ").strip()
        if customer.verify_pin(pin):
            print(f"\n  Welcome back, {customer.get_name()}!")
            return customer
        remaining = 2 - attempt
        if remaining > 0:
            print(f"  Incorrect PIN. {remaining} attempt(s) remaining.")

    print("  Too many incorrect attempts.")
    return None


# ── Main session ──────────────────────────────────────────────────────────────

def session(customer: Customer) -> None:
    while True:
        print()
        print("  -------------------------------")
        print("   What would you like to do?")
        print("  -------------------------------")
        print("  1. See all my accounts")
        print("  2. Deposit")
        print("  3. Withdraw")
        print("  4. Transfer")
        print("  5. Transaction history")
        print("  6. Log out")
        print("  -------------------------------")
        print()

        choice = input("  Choose an option: ").strip()

        match choice:
            case "1":
                show_accounts(customer)
            case "2":
                do_deposit(customer)
            case "3":
                do_withdraw(customer)
            case "4":
                do_transfer(customer)
            case "5":
                show_transactions(customer)
            case "6":
                print(f"\n  Goodbye, {customer.get_name()}!\n")
                break
            case _:
                print("  Invalid option. Please choose 1–6.")


# ── Seed data ─────────────────────────────────────────────────────────────────

def seed(bank: Bank) -> None:
    """Create demo customers and accounts."""
    alice = Customer("Alice", "1234")
    alice.add_account(CheckingAccount("Alice", initial_balance=500.00))
    alice.add_account(SavingsAccount("Alice", initial_balance=1200.00))
    bank.add_customer(alice)

    bob = Customer("Bob", "5678")
    bob.add_account(CheckingAccount("Bob", initial_balance=250.00))
    bank.add_customer(bob)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    bank = Bank("Citi Bank")
    seed(bank)

    account_types = ", ".join(sorted(bank.get_account_types()))  # Set[str]

    print("=" * 48)
    print(f"       Welcome to {bank.get_name()}")
    print(f"       Account types: {account_types}")
    print("=" * 48)

    while True:
        print()
        print("  1. Log in")
        print("  2. Exit")
        print()

        choice = input("  Choose an option: ").strip()

        match choice:
            case "1":
                customer = login(bank)
                if customer:
                    session(customer)
            case "2":
                print("\n  Thank you for banking with Citi. Goodbye!\n")
                break
            case _:
                print("  Invalid option.")


if __name__ == "__main__":
    main()
