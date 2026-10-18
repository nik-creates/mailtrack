import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent / "tracking.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            recipient TEXT,
            subject TEXT,
            sent_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS opens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            opened_at TEXT,
            ip TEXT,
            user_agent TEXT,
            FOREIGN KEY (email_id) REFERENCES emails(id)
        )
        """
    )
    conn.commit()
    conn.close()


def register_email(tracking_id: str, recipient: str, subject: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO emails (id, recipient, subject, sent_at) VALUES (?, ?, ?, ?)",
        (tracking_id, recipient, subject, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def log_open(tracking_id: str, ip: str, user_agent: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO opens (email_id, opened_at, ip, user_agent) VALUES (?, ?, ?, ?)",
        (tracking_id, datetime.now(timezone.utc).isoformat(), ip, user_agent),
    )
    conn.commit()
    conn.close()


def get_all_emails():
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT e.id, e.recipient, e.subject, e.sent_at,
               COUNT(o.id) as open_count,
               MIN(o.opened_at) as first_opened,
               MAX(o.opened_at) as last_opened
        FROM emails e
        LEFT JOIN opens o ON e.id = o.email_id
        GROUP BY e.id
        ORDER BY e.sent_at DESC
        """
    ).fetchall()
    conn.close()
    return rows


def get_opens_for_email(tracking_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM opens WHERE email_id = ? ORDER BY opened_at",
        (tracking_id,),
    ).fetchall()
    conn.close()
    return rows
