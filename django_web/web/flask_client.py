import requests
from django.conf import settings

BASE = settings.FLASK_API_BASE_URL.rstrip("/")


def _headers(is_write: bool = False):
    headers = {"Content-Type": "application/json"}

    if is_write:
        headers["X-API-KEY"] = settings.FLASK_API_KEY

    return headers


def _handle_response(r: requests.Response):
    """
    Central error handler for Flask API
    """
    if r.status_code == 204:
        return None

    try:
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        # nice error message for Django views
        raise Exception(
            f"Flask API error {r.status_code}: {r.text}"
        ) from e


def flask_get(path, params=None):
    r = requests.get(f"{BASE}{path}", params=params, headers=_headers(False))
    return _handle_response(r)


def flask_post(path, data):
    r = requests.post(f"{BASE}{path}", json=data, headers=_headers(True))
    return _handle_response(r)


def flask_put(path, data):
    r = requests.put(f"{BASE}{path}", json=data, headers=_headers(True))
    return _handle_response(r)


def flask_delete(path):
    r = requests.delete(f"{BASE}{path}", headers=_headers(True))
    return _handle_response(r)
