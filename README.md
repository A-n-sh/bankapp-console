# bankapp-console

A console banking app written in Python. Data is stored in SQLite, so it is still there after you quit.

## Features

- Checking accounts (overdraft up to $100) and savings accounts (2% APR, credited monthly)
- Several accounts per customer, each with a 6-digit account number
- Deposits, withdrawals, and transfers to any account in the bank
- Transfers are atomic: both sides succeed, or nothing changes
- Transaction history showing each running balance and memo
- PINs hashed with salted PBKDF2; three wrong PINs lock the login for 5 minutes
- Money handled as `Decimal` and stored as integer cents, so no float rounding errors

## Quick start

Requires Python 3.10+. There are no runtime dependencies.

```bash
python -m bankapp --demo            # seeds alice / 1234 and bob / 5678 into an empty bank
python -m bankapp --db ./bank.db    # use a specific database file
python -m bankapp --apply-interest  # credit one month of savings interest and exit
```

By default the database is at `~/.bankapp/bank.db`. Set the `BANKAPP_DB` environment variable to use a different path.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest
ruff check . && ruff format --check .
```

## Layout

| Module | Responsibility |
| --- | --- |
| `bankapp/models.py` | Domain classes: `Account` (abstract), `CheckingAccount`, `SavingsAccount`, `Customer`, `Transaction` |
| `bankapp/service.py` | `BankService`: every banking operation and business rule |
| `bankapp/storage.py` | `Repository`: SQLite schema and persistence |
| `bankapp/security.py` | PIN validation and hashing |
| `bankapp/money.py` | Parsing, rounding, and formatting money amounts |
| `bankapp/cli.py` | `ConsoleApp`: the interactive menus |
| `bankapp/__main__.py` | Command-line entry point |
