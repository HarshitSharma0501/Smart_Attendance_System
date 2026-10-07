from flask import Blueprint, request, jsonify
import bcrypt

auth_bp = Blueprint("auth", __name__)

def get_users_collection():
    from app import users_collection
    return users_collection

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not name or not email or not password or not role:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    if role not in ["admin", "teacher"]:
        return jsonify({
            "status": "error",
            "message": "Role must be admin or teacher"
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
    )

    user = {
        "name": name,
        "email": email,
        "password": hashed_password.decode("utf-8"),
        "role": role
    }

    users_collection.insert_one(user)

    return jsonify({
        "status": "success",
        "message": "User registered successfully"
    }), 201