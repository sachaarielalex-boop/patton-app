"""Shared key/value store with permanent, cross-user persistence.

If Supabase credentials are configured (Streamlit secrets SUPABASE_URL +
SUPABASE_KEY, or the same environment variables), every get/put goes to a
Supabase Postgres table named `kv_store(key text primary key, value jsonb)`.
That makes all data shared across every user and device, permanently.

If no Supabase credentials are present (e.g. local development), it falls back
to a local JSON file (writable temp dir on read-only filesystems). The public
API — get(key, default) and put(key, value) — is unchanged.
"""
import json
import os
import tempfile
import threading
import urllib.request
import urllib.parse
import urllib.error

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None

_lock = threading.Lock()

# ── Supabase configuration ─────────────────────────────────
_TABLE = "kv_store"


def _supabase_conf():
    """Return (base_url, api_key) if Supabase is configured, else (None, None)."""
    url = key = None
    if st is not None:
        try:
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")
        except Exception:
            url = key = None
    url = url or os.environ.get("SUPABASE_URL")
    key = key or os.environ.get("SUPABASE_KEY")
    if url and key:
        return url.rstrip("/"), key
    return None, None


def _sb_headers(api_key, write=False):
    h = {
        "apikey": api_key,
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json",
    }
    if write:
        h["Prefer"] = "resolution=merge-duplicates,return=minimal"
    return h


def _sb_get(url, api_key, key):
    endpoint = "{}/rest/v1/{}?key=eq.{}&select=value".format(
        url, _TABLE, urllib.parse.quote(key, safe="")
    )
    req = urllib.request.Request(endpoint, headers=_sb_headers(api_key))
    with urllib.request.urlopen(req, timeout=10) as resp:
        rows = json.loads(resp.read().decode("utf-8"))
    if rows:
        return rows[0].get("value")
    return None


def _sb_put(url, api_key, key, value):
    endpoint = "{}/rest/v1/{}".format(url, _TABLE)
    body = json.dumps([{"key": key, "value": value}]).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=body, headers=_sb_headers(api_key, write=True), method="POST"
    )
    urllib.request.urlopen(req, timeout=15).read()


# ── Local-file fallback ────────────────────────────────────
REPO_PATH = os.path.join(os.path.dirname(__file__), "_shared_data.json")
TMP_PATH = os.path.join(tempfile.gettempdir(), "patton_shared_data.json")


def _writable_path():
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
        pass


# ── Public API ─────────────────────────────────────────────
def get(key, default=None):
    """Get a value from the shared store."""
    fallback = default if default is not None else []
    url, api_key = _supabase_conf()
    if url:
        try:
            val = _sb_get(url, api_key, key)
            return val if val is not None else fallback
        except Exception:
            return fallback
    db = _load()
    return db.get(key, fallback)


def put(key, value):
    """Set a value in the shared store (persisted for every user)."""
    url, api_key = _supabase_conf()
    if url:
        try:
            _sb_put(url, api_key, key, value)
            return
        except Exception:
            pass  # fall through to local so data is not silently lost locally
    db = _load()
    db[key] = value
    _save(db)
