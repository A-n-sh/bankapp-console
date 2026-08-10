from flask import Blueprint, request, jsonify
import store
from models.user import User

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    user = User(name, email)
    store.users[user.get_user_id()] = user
    return jsonify(user.to_dict()), 201


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = store.users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())
