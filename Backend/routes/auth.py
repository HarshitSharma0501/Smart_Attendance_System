
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from bson import ObjectId
import bcrypt

auth_bp = Blueprint("auth", __name__)


def get_users_collection():
    from app import users_collection
    return users_collection


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email:
        return jsonify({
            "status": "error",
            "message": "Name and email cannot be empty"
        }), 400

    if role not in ["admin", "teacher"]:
        return jsonify({
            "status": "error",
            "message": "Role must be admin or teacher"
        }), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters"
        }), 400

    users_collection = get_users_collection()

    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "Email already registered"
        }), 409

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role
    }

    users_collection.insert_one(user)

    return jsonify({
        "status": "success",
        "message": "User registered successfully"
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    email = email.strip().lower()

    users_collection = get_users_collection()

    user = users_collection.find_one({
        "email": email
    })

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user["_id"])
    )

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        return jsonify({
            "status": "error",
            "message": "Invalid user identity"
        }), 401

    users_collection = get_users_collection()

    user = users_collection.find_one({
        "_id": user_object_id
    })

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    return jsonify({
        "status": "success",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200

