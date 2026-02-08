import requests
from django.conf import settings


def _url(path: str) -> str:
    base = settings.FLASK_API_BASE_URL.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return base + path


def flask_get(path: str, params=None):
    resp = requests.get(_url(path), params=params, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_post(path: str, payload: dict):
    resp = requests.post(_url(path), json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_put(path: str, payload: dict):
    resp = requests.put(_url(path), json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()


def flask_delete(path: str):
    resp = requests.delete(_url(path), timeout=5)
    resp.raise_for_status()
    return resp.json() if resp.content else None
