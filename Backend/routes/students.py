
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timezone

students_bp = Blueprint(
    "students",
    __name__,
    url_prefix="/api/students"
)


@students_bp.route("/", methods=["POST"])
@jwt_required()
def register_student():
    from app import db

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json(silent=True) or {}

    student_id = str(data.get("student_id", "")).strip()
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()

    if not student_id or not name or not email:
        return jsonify({
            "error": "student_id, name and email are required"
        }), 400

    students_collection = db["students"]

    existing = students_collection.find_one({
        "student_id": student_id
    })

    if existing:
        return jsonify({
            "error": "Student ID already exists"
        }), 409

    student = {
        "student_id": student_id,
        "name": name,
        "email": email,
        "created_at": datetime.now(timezone.utc)
    }

    result = students_collection.insert_one(student)

    return jsonify({
        "message": "Student registered successfully",
        "student": {
            "id": str(result.inserted_id),
            "student_id": student_id,
            "name": name,
            "email": email
        }
    }), 201

