"""
models.py
----------
Simple "model" layer that wraps SQL queries into clean Python functions.
Keeps app.py (routes) free of raw SQL for readability.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

VALID_CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Salary", "Other"]


# =========================================================
# USER MODEL
# =========================================================

class User:
    @staticmethod
    def create(name, email, password):
        """Hashes the password and inserts a new user. Returns True/False."""
        conn = get_db_connection()
        try:
            password_hash = generate_password_hash(password)  # secure hash (pbkdf2/sha256)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name, email.lower().strip(), password_hash, now),
            )
            conn.commit()
            return True
        except Exception:
            # Most common failure: UNIQUE constraint on email
            return False
        finally:
            conn.close()

    @staticmethod
    def find_by_email(email):
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        conn.close()
        return user

    @staticmethod
    def find_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(user_row, password):
        """Checks a plaintext password against the stored hash."""
        return check_password_hash(user_row["password_hash"], password)


# =========================================================
# TRANSACTION MODEL
# =========================================================

class Transaction:
    @staticmethod
    def create(user_id, t_type, category, amount, txn_date, note):
        conn = get_db_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """INSERT INTO transactions
               (user_id, type, category, amount, txn_date, note, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, t_type, category, amount, txn_date, note, now),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_for_user(user_id, category=None, date_from=None, date_to=None):
        """Returns transactions for a user, optionally filtered by category/date range."""
        conn = get_db_connection()
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if date_from:
            query += " AND txn_date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND txn_date <= ?"
            params.append(date_to)

        query += " ORDER BY txn_date DESC, id DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_by_id(txn_id, user_id):
        """Fetch a single transaction, scoped to the owning user (security)."""
        conn = get_db_connection()
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ? AND user_id = ?", (txn_id, user_id)
        ).fetchone()
        conn.close()
        return row

    @staticmethod
    def update(txn_id, user_id, t_type, category, amount, txn_date, note):
        conn = get_db_connection()
        conn.execute(
            """UPDATE transactions
               SET type = ?, category = ?, amount = ?, txn_date = ?, note = ?
               WHERE id = ? AND user_id = ?""",
            (t_type, category, amount, txn_date, note, txn_id, user_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(txn_id, user_id):
        conn = get_db_connection()
        conn.execute(
            "DELETE FROM transactions WHERE id = ? AND user_id = ?", (txn_id, user_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_summary(user_id):
        """Returns total income, total expense, and balance for a user."""
        conn = get_db_connection()
        income = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'income'",
            (user_id,),
        ).fetchone()["total"]
        expense = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'expense'",
            (user_id,),
        ).fetchone()["total"]
        conn.close()
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
        }

    @staticmethod
    def get_expense_by_category(user_id):
        """Returns category -> total expense mapping, used for the pie chart."""
        conn = get_db_connection()
        rows = conn.execute(
            """SELECT category, COALESCE(SUM(amount), 0) AS total
               FROM transactions
               WHERE user_id = ? AND type = 'expense'
               GROUP BY category
               ORDER BY total DESC""",
            (user_id,),
        ).fetchall()
        conn.close()
        return {row["category"]: row["total"] for row in rows}
