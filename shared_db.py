"""Shared JSON-based database for persistent cross-user data storage."""
import json
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), "_shared_data.json")
_lock = threading.Lock()


def _load():
    with _lock:
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
    return {}


def _save(data):
    try:
        with _lock:
            with open(DB_PATH, "w") as f:
                json.dump(data, f, ensure_ascii=False)
    except (IOError, OSError):
        pass  # Silently fail on read-only filesystems (cloud)


def get(key, default=None):
    """Get a value from shared DB."""
    db = _load()
    return db.get(key, default if default is not None else [])


def put(key, value):
    """Set a value in shared DB."""
    db = _load()
    db[key] = value
    _save(db)
