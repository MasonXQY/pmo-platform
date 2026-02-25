import hashlib
import sqlite3
import time

CACHE_DB = "control_plane_cache.db"
CACHE_TTL_SECONDS = 3600  # 1 hour


def init_cache():
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            model TEXT,
            response TEXT,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()


def _hash_prompt(model, prompt):
    raw = f"{model}:{prompt}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def get_cached(model, prompt):
    key = _hash_prompt(model, prompt)

    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT response, timestamp FROM cache WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    response, ts = row

    if time.time() - ts > CACHE_TTL_SECONDS:
        return None

    return response


def set_cache(model, prompt, response):
    key = _hash_prompt(model, prompt)

    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.cursor()
    cursor.execute(
        "REPLACE INTO cache (key, model, response, timestamp) VALUES (?, ?, ?, ?)",
        (key, model, response, time.time())
    )
    conn.commit()
    conn.close()
