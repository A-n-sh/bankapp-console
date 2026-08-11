from flask import Blueprint, request, jsonify
from container import account_service

account_bp = Blueprint("accounts", __name__, url_prefix="/api/accounts")


def _status(error: str) -> int:
    return 404 if "not found" in error.lower() else 400


@account_bp.route("", methods=["POST"])
def create_account():
    data = request.get_json(silent=True) or {}
    account, error = account_service.createAccount(
        data.get("userId"),
        data.get("accountType", ""),
    )
    if error:
        return jsonify({"error": error}), _status(error)
    return jsonify(account.to_dict()), 201


@account_bp.route("/<int:account_id>", methods=["GET"])
def get_account(account_id):
    account, error = account_service.getAccount(account_id)
    if error:
        return jsonify({"error": error}), _status(error)
    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/deposit", methods=["POST"])
def deposit(account_id):
    data = request.get_json(silent=True) or {}
    account, error = account_service.deposit(account_id, data.get("amount"))
    if error:
        return jsonify({"error": error}), _status(error)
    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/withdraw", methods=["POST"])
def withdraw(account_id):
    data = request.get_json(silent=True) or {}
    account, error = account_service.withdraw(account_id, data.get("amount"))
    if error:
        return jsonify({"error": error}), _status(error)
    return jsonify(account.to_dict())


@account_bp.route("/<int:account_id>/transactions", methods=["GET"])
def get_transactions(account_id):
    records, error = account_service.getTransactions(account_id)
    if error:
        return jsonify({"error": error}), _status(error)
    return jsonify([r.to_dict() for r in records])
