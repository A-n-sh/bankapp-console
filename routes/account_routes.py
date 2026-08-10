from flask import Blueprint, request, jsonify
import store
from models.checking_account import CheckingAccount
from models.savings_account import SavingsAccount

account_bp = Blueprint("accounts", __name__, url_prefix="/api/accounts")

VALID_TYPES = {"CHECKING", "SAVINGS"}


@account_bp.route("", methods=["POST"])
def create_account():
    data = request.get_json(silent=True) or {}
    user_id = data.get("userId")
    account_type = str(data.get("accountType", "")).upper()

    if user_id is None or account_type not in VALID_TYPES:
        return jsonify({"error": "userId and accountType (CHECKING or SAVINGS) required"}), 400

    user = store.users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if account_type == "CHECKING":
        account = CheckingAccount(user_id, user.get_name())
    else:
        account = SavingsAccount(user_id, user.get_name())

    store.accounts[account.get_account_id()] = account
    return jsonify(account.to_dict()), 201


@account_bp.route("/<int:account_id>", methods=["GET"])
def get_account(account_id):
    account = store.accounts.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/deposit", methods=["POST"])
def deposit(account_id):
    account = store.accounts.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "amount must be a positive number"}), 400

    account.deposit(amount)
    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/withdraw", methods=["POST"])
def withdraw(account_id):
    account = store.accounts.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json(silent=True) or {}
    amount = data.get("amount")

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "amount must be a positive number"}), 400

    if not account.withdraw(amount):
        return jsonify({"error": "Insufficient funds"}), 400

    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/transactions", methods=["GET"])
def get_transactions(account_id):
    account = store.accounts.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify([r.to_dict() for r in account.get_transactions()])
