from flask import Blueprint, request, jsonify
from container import user_service

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    user, error = user_service.create_user(
        str(data.get("name", "")),
        str(data.get("email", "")),
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(user.to_dict()), 201


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user, error = user_service.get_user(user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(user.to_dict())
