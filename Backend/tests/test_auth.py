
import uuid
import pytest

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app import app, users_collection


@pytest.fixture
def test_client():
    app.config["TESTING"] = True

    with app.test_client() as testing_client:
        yield testing_client

    # Remove only users created in the test database
    users_collection.delete_many({
        "email": {"$regex": r"^pytest_"}
    })


@pytest.fixture
def test_user(test_client):
    email = f"pytest_{uuid.uuid4().hex}@example.com"

    user_data = {
        "name": "Test Teacher",
        "email": email,
        "password": "Teacher@123",
        "role": "teacher"
    }

    response = test_client.post(
        "/api/auth/register",
        json=user_data
    )

    assert response.status_code == 201

    return user_data


def test_health_endpoint(test_client):
    response = test_client.get("/api/health")

    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_register_user(test_client, test_user):
    user = users_collection.find_one({
        "email": test_user["email"]
    })

    assert user is not None
    assert user["name"] == test_user["name"]
    assert user["password"] != test_user["password"]


def test_duplicate_registration(test_client, test_user):
    response = test_client.post(
        "/api/auth/register",
        json=test_user
    )

    assert response.status_code == 409


def test_login_success(test_client, test_user):
    response = test_client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )

    assert response.status_code == 200
    assert response.json["access_token"]
    assert response.json["user"]["email"] == test_user["email"]


def test_login_invalid_password(test_client, test_user):
    response = test_client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401


def test_profile_without_token(test_client):
    response = test_client.get("/api/auth/profile")

    assert response.status_code == 401


def test_profile_with_valid_token(test_client, test_user):
    login_response = test_client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )

    token = login_response.json["access_token"]

    response = test_client.get(
        "/api/auth/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["user"]["email"] == test_user["email"]
    assert response.json["user"]["role"] == "teacher"
