import sqlite3
import time
from datetime import datetime

DB_PATH = "control_plane_metrics.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant TEXT,
            model TEXT,
            latency_ms REAL,
            tokens INTEGER,
            cost REAL,
            error INTEGER,
            timestamp REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()


def record_request(tenant, model, latency_ms, tokens, cost, error=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO requests (tenant, model, latency_ms, tokens, cost, error, timestamp, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            tenant,
            model,
            latency_ms,
            tokens,
            cost,
            1 if error else 0,
            time.time(),
            datetime.utcnow().date().isoformat()
        )
    )
    conn.commit()
    conn.close()


def get_metrics(tenant=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if tenant:
        cursor.execute("""
            SELECT model,
                   COUNT(*) as calls,
                   AVG(latency_ms) as avg_latency,
                   SUM(tokens) as total_tokens,
                   SUM(cost) as total_cost,
                   SUM(error) as total_errors
            FROM requests
            WHERE tenant = ?
            GROUP BY model
        """, (tenant,))
    else:
        cursor.execute("""
            SELECT model,
                   COUNT(*) as calls,
                   AVG(latency_ms) as avg_latency,
                   SUM(tokens) as total_tokens,
                   SUM(cost) as total_cost,
                   SUM(error) as total_errors
            FROM requests
            GROUP BY model
        """)

    rows = cursor.fetchall()
    conn.close()

    return {
        row[0]: {
            "calls": row[1],
            "avg_latency_ms": round(row[2], 2) if row[2] else 0,
            "total_tokens": row[3] or 0,
            "total_cost": round(row[4], 6) if row[4] else 0,
            "total_errors": row[5] or 0
        }
        for row in rows
    }


def get_daily_cost(tenant=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.utcnow().date().isoformat()

    if tenant:
        cursor.execute("""
            SELECT SUM(cost)
            FROM requests
            WHERE date = ? AND tenant = ?
        """, (today, tenant))
    else:
        cursor.execute("""
            SELECT SUM(cost)
            FROM requests
            WHERE date = ?
        """, (today,))

    row = cursor.fetchone()
    conn.close()

    return row[0] or 0
