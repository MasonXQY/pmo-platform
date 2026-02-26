import sqlite3
import time
from datetime import datetime

DB_PATH = "control_plane_metrics.db"


def record_ensemble_result(tenant, model, confidence):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ensemble_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant TEXT,
            selected_model TEXT,
            confidence REAL,
            timestamp REAL,
            date TEXT
        )
    """)
    cursor.execute(
        "INSERT INTO ensemble_results (tenant, selected_model, confidence, timestamp, date) VALUES (?, ?, ?, ?, ?)",
        (
            tenant,
            model,
            confidence,
            time.time(),
            datetime.utcnow().date().isoformat()
        )
    )
    conn.commit()
    conn.close()


def model_win_rates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT selected_model,
               COUNT(*) as wins
        FROM ensemble_results
        GROUP BY selected_model
    """)

    rows = cursor.fetchall()
    conn.close()

    total = sum(row[1] for row in rows) or 1

    return {
        row[0]: {
            "wins": row[1],
            "win_rate": round(row[1] / total, 3)
        }
        for row in rows
    }
