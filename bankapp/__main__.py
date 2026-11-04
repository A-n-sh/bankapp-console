import argparse
import os
from pathlib import Path

from bankapp.cli import ConsoleApp
from bankapp.money import fmt
from bankapp.service import BankService, seed_demo
from bankapp.storage import Repository

DEFAULT_DB = Path(os.environ.get("BANKAPP_DB", "~/.bankapp/bank.db"))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="bankapp", description="Console banking app.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite file (default: %(default)s)")
    parser.add_argument(
        "--demo", action="store_true", help="seed demo customers if the bank is empty"
    )
    parser.add_argument(
        "--apply-interest", action="store_true", help="credit a month of savings interest and exit"
    )
    args = parser.parse_args(argv)

    repo = Repository(args.db)
    service = BankService(repo)
    try:
        if args.demo and repo.count_customers() == 0:
            seed_demo(service)
            print("Seeded demo customers: alice / 1234, bob / 5678")
        if args.apply_interest:
            applied = service.apply_monthly_interest()
            for txn in applied:
                print(f"#{txn.account_id:06d}: +{fmt(txn.amount)} -> {fmt(txn.balance_after)}")
            print(f"Applied interest to {len(applied)} account(s).")
            return
        ConsoleApp(service).run()
    finally:
        repo.close()


if __name__ == "__main__":
    main()
