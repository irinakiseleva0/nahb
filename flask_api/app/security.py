from flask import current_app, request, jsonify

def require_api_key():
    key = request.headers.get("X-API-KEY")
    if not key or key != current_app.config.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401
    return None
