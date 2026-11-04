from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from bankapp.models import (
    ACCOUNT_CLASSES,
    Account,
    AccountType,
    Customer,
    Transaction,
    TxnType,
)
from bankapp.money import from_cents, to_cents

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id              INTEGER PRIMARY KEY,
    username        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    full_name       TEXT NOT NULL,
    pin_hash        TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id            INTEGER PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(id),
    type          TEXT NOT NULL CHECK (type IN ('checking', 'savings')),
    balance_cents INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id                  INTEGER PRIMARY KEY,
    account_id          INTEGER NOT NULL REFERENCES accounts(id),
    type                TEXT NOT NULL,
    amount_cents        INTEGER NOT NULL,
    balance_after_cents INTEGER NOT NULL,
    memo                TEXT NOT NULL DEFAULT '',
    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts (customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions (account_id, id);
"""


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class Repository:
    """SQLite persistence for customers, accounts and transactions."""

    def __init__(self, path: str | Path = ":memory:"):
        target = str(path)
        if target != ":memory:":
            file = Path(path).expanduser()
            file.parent.mkdir(parents=True, exist_ok=True)
            target = str(file)
        self._conn = sqlite3.connect(target)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    @contextmanager
    def atomic(self) -> Iterator[None]:
        """Commit everything in the block, or roll it all back on error."""
        with self._conn:
            yield

    # ── customers ────────────────────────────────────────────────────────────

    @staticmethod
    def _customer(row: sqlite3.Row) -> Customer:
        return Customer(
            id=row["id"],
            username=row["username"],
            full_name=row["full_name"],
            pin_hash=row["pin_hash"],
            failed_attempts=row["failed_attempts"],
            locked_until=_dt(row["locked_until"]),
            created_at=_dt(row["created_at"]),
        )

    def add_customer(self, customer: Customer) -> Customer:
        cur = self._conn.execute(
            "INSERT INTO customers (username, full_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
            (
                customer.username,
                customer.full_name,
                customer.pin_hash,
                customer.created_at.isoformat(),
            ),
        )
        customer.id = cur.lastrowid
        return customer

    def update_customer(self, customer: Customer) -> None:
        self._conn.execute(
            "UPDATE customers SET full_name = ?, pin_hash = ?, failed_attempts = ?,"
            " locked_until = ? WHERE id = ?",
            (
                customer.full_name,
                customer.pin_hash,
                customer.failed_attempts,
                customer.locked_until.isoformat() if customer.locked_until else None,
                customer.id,
            ),
        )

    def find_customer(self, username: str) -> Customer | None:
        row = self._conn.execute(
            "SELECT * FROM customers WHERE username = ?", (username.strip(),)
        ).fetchone()
        return self._customer(row) if row else None

    def get_customer(self, customer_id: int) -> Customer | None:
        row = self._conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        return self._customer(row) if row else None

    def count_customers(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]

    # ── accounts ─────────────────────────────────────────────────────────────

    @staticmethod
    def _account(row: sqlite3.Row) -> Account:
        cls = ACCOUNT_CLASSES[AccountType(row["type"])]
        return cls(
            id=row["id"],
            customer_id=row["customer_id"],
            balance=from_cents(row["balance_cents"]),
            created_at=_dt(row["created_at"]),
        )

    def add_account(self, account: Account) -> Account:
        cur = self._conn.execute(
            "INSERT INTO accounts (customer_id, type, balance_cents, created_at)"
            " VALUES (?, ?, ?, ?)",
            (
                account.customer_id,
                account.type.value,
                to_cents(account.balance),
                account.created_at.isoformat(),
            ),
        )
        account.id = cur.lastrowid
        return account

    def save_balance(self, account: Account) -> None:
        self._conn.execute(
            "UPDATE accounts SET balance_cents = ? WHERE id = ?",
            (to_cents(account.balance), account.id),
        )

    def get_account(self, account_id: int) -> Account | None:
        row = self._conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
        return self._account(row) if row else None

    def list_accounts(self, customer_id: int | None = None) -> list[Account]:
        if customer_id is None:
            rows = self._conn.execute("SELECT * FROM accounts ORDER BY id")
        else:
            rows = self._conn.execute(
                "SELECT * FROM accounts WHERE customer_id = ? ORDER BY id",
                (customer_id,),
            )
        return [self._account(row) for row in rows]

    # ── transactions ─────────────────────────────────────────────────────────

    def add_transaction(self, txn: Transaction) -> Transaction:
        cur = self._conn.execute(
            "INSERT INTO transactions"
            " (account_id, type, amount_cents, balance_after_cents, memo, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                txn.account_id,
                txn.type.value,
                to_cents(txn.amount),
                to_cents(txn.balance_after),
                txn.memo,
                txn.created_at.isoformat(),
            ),
        )
        return Transaction(
            id=cur.lastrowid,
            account_id=txn.account_id,
            type=txn.type,
            amount=txn.amount,
            balance_after=txn.balance_after,
            memo=txn.memo,
            created_at=txn.created_at,
        )

    def list_transactions(self, account_id: int, limit: int = 20) -> list[Transaction]:
        rows = self._conn.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY id DESC LIMIT ?",
            (account_id, limit),
        )
        return [
            Transaction(
                id=row["id"],
                account_id=row["account_id"],
                type=TxnType(row["type"]),
                amount=from_cents(row["amount_cents"]),
                balance_after=from_cents(row["balance_after_cents"]),
                memo=row["memo"],
                created_at=_dt(row["created_at"]),
            )
            for row in rows
        ]
