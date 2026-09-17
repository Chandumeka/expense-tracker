"""
database.py
------------
Handles all raw database connectivity for the Expense Tracker app.
Uses SQLite for simplicity (zero external setup) — the schema below
is standard SQL and can be ported to MySQL almost as-is (see schema.sql).
"""

import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# Path to the SQLite database file (created automatically on first run)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")


def get_db_connection():
    """
    Creates and returns a new SQLite connection.
    row_factory = sqlite3.Row lets us access columns by name (like a dict),
    which keeps template code clean (e.g. row['amount']).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def init_db(seed_demo=True):
    """
    Creates tables if they do not already exist, and optionally
    inserts a demo user + sample transactions so the app is not empty
    on first run.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # ---------- USERS TABLE ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # ---------- TRANSACTIONS TABLE ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            txn_date TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()

    # ---------- SEED DEMO DATA (only if DB is empty) ----------
    if seed_demo:
        existing = cur.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        if existing == 0:
            _seed_demo_data(conn)

    conn.close()


def _seed_demo_data(conn):
    """Inserts one demo user with a handful of sample transactions."""
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    demo_password_hash = generate_password_hash("password123")
    cur.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ("Demo User", "demo@example.com", demo_password_hash, now),
    )
    user_id = cur.lastrowid

    sample_transactions = [
        # (type, category, amount, date, note)
        ("income", "Salary", 55000, "2025-09-01", "Monthly salary"),
        ("income", "Other", 2500, "2025-09-05", "Freelance project"),
        ("expense", "Food", 1200, "2025-09-02", "Groceries"),
        ("expense", "Bills", 3200, "2025-09-03", "Electricity bill"),
        ("expense", "Travel", 850, "2025-09-06", "Cab rides"),
        ("expense", "Shopping", 4200, "2025-09-08", "New shoes"),
        ("expense", "Food", 650, "2025-09-10", "Dinner with friends"),
        ("expense", "Other", 500, "2025-09-11", "Miscellaneous"),
    ]

    for t_type, category, amount, txn_date, note in sample_transactions:
        cur.execute(
            """INSERT INTO transactions
               (user_id, type, category, amount, txn_date, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, t_type, category, amount, txn_date, note, now),
        )

    conn.commit()
