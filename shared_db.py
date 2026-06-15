"""Shared JSON-based database for persistent cross-user data storage."""
import json
import os
import tempfile
import threading

# Repo-local file (read-only on Streamlit Cloud) and a writable temp fallback.
REPO_PATH = os.path.join(os.path.dirname(__file__), "_shared_data.json")
TMP_PATH = os.path.join(tempfile.gettempdir(), "patton_shared_data.json")
_lock = threading.Lock()


def _writable_path():
    """Return the first path we can actually write to (cloud FS is read-only)."""
    for path in (REPO_PATH, TMP_PATH):
        try:
            with open(path, "a"):
                pass
            return path
        except (IOError, OSError):
            continue
    return TMP_PATH


DB_PATH = _writable_path()


def _read(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            return {}
    return {}


def _load():
    with _lock:
        data = _read(DB_PATH)
        # On cloud DB_PATH is the temp file; seed missing keys from any
        # committed repo data so defaults survive a fresh container.
        if DB_PATH != REPO_PATH:
            for k, v in _read(REPO_PATH).items():
                data.setdefault(k, v)
        return data


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
