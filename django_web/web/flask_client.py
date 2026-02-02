import requests
from django.conf import settings


def flask_get(path: str, params: dict | None = None) -> dict | list:
    """
    Small helper for GET requests to Flask API.
    Returns parsed JSON or raises an exception (so Django shows a clear error).
    """
    base = settings.FLASK_API_BASE_URL.rstrip("/")
    url = f"{base}{path}"

    resp = requests.get(url, params=params, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_post(path: str, json: dict) -> dict:
    base = settings.FLASK_API_BASE_URL.rstrip("/")
    url = f"{base}{path}"

    resp = requests.post(url, json=json, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_put(path: str, json: dict) -> dict:
    base = settings.FLASK_API_BASE_URL.rstrip("/")
    url = f"{base}{path}"

    resp = requests.put(url, json=json, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_delete(path: str) -> None:
    base = settings.FLASK_API_BASE_URL.rstrip("/")
    url = f"{base}{path}"

    resp = requests.delete(url, timeout=5)
    resp.raise_for_status()
