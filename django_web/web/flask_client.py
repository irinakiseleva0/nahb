import requests
from django.conf import settings

BASE = settings.FLASK_API_BASE_URL.rstrip("/")

def _headers(is_write: bool = False):
    h = {"Content-Type": "application/json"}
    if is_write:
        h["X-API-KEY"] = settings.FLASK_API_KEY
    return h

def flask_get(path, params=None):
    r = requests.get(f"{BASE}{path}", params=params, headers=_headers(False))
    r.raise_for_status()
    return r.json()

def flask_post(path, data):
    r = requests.post(f"{BASE}{path}", json=data, headers=_headers(True))
    r.raise_for_status()
    return r.json()

def flask_put(path, data):
    r = requests.put(f"{BASE}{path}", json=data, headers=_headers(True))
    r.raise_for_status()
    return r.json()

def flask_delete(path):
    r = requests.delete(f"{BASE}{path}", headers=_headers(True))
    r.raise_for_status()
    return r.json()
