from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise ValueError("MongoDB configuration missing in .env file")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]

@app.route("/")
def home():
    return jsonify({
        "message": "Smart Attendance API Running"
    })

@app.route("/api/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify({
            "status": "success",
            "message": "Backend and MongoDB are working"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)