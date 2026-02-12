# app/security.py
import os
from flask import request, jsonify, current_app

def require_api_key():
    expected = current_app.config.get("API_KEY") or os.getenv("API_KEY")
    provided = request.headers.get("X-API-KEY")

    if not expected:
        return jsonify({"error": "API_KEY not configured"}), 500

    if not provided or provided != expected:
        return jsonify({"error": "Unauthorized"}), 401

    return None
