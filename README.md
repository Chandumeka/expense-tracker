# 💰 Personal Expense Tracker

A complete full-stack Personal Expense Tracker web app with authentication,
built with **Flask**, **SQLite**, **Bootstrap 5**, and **Chart.js**.

## Features

- 🔐 Signup / Login / Logout with hashed passwords (Werkzeug's pbkdf2, hashlib-based)
- 📊 Dashboard with income / expense / balance cards and a doughnut chart
- ➕ Add income & expense transactions with category, date, and notes
- 📋 View, filter (by category & date range), edit, and delete transactions
- 🌗 Light / Dark theme toggle (persisted in the browser)
- 📱 Fully responsive Bootstrap UI with flash messages for feedback

## Project Structure

```
expense_tracker/
├── app.py                  # Main Flask app (routes / controllers)
├── database.py             # DB connection + table creation + demo seed
├── models.py                # User & Transaction data-access layer
├── requirements.txt
├── schema_mysql.sql        # Reference schema if migrating to MySQL
├── expense_tracker.db      # SQLite database (auto-created on first run)
├── templates/
│   ├── base.html            # Shared layout, navbar, flash messages
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── transactions.html
│   └── edit_transaction.html
└── static/
    ├── css/style.css        # Theme system + all custom styling
    └── js/script.js         # Theme toggle, delete confirm, alerts
```

## Setup & Run

**1. Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
python app.py
```

The app will:
- Automatically create `expense_tracker.db` (SQLite) on first run
- Seed a demo account with sample transactions

**4. Open in your browser**

```
http://127.0.0.1:5000
```

## Demo Login

```
Email:    demo@example.com
Password: password123
```

Or just sign up for a new account from the Sign Up page.

## Switching to MySQL (optional)

This project uses SQLite by default for zero-setup simplicity. To use MySQL:

1. `pip install mysql-connector-python`
2. Run `schema_mysql.sql` against your MySQL server
3. In `database.py`, replace the `sqlite3.connect(...)` call with a
   `mysql.connector.connect(host=..., user=..., password=..., database=...)`
   call, and change `?` placeholders to `%s` in `models.py`.

## Notes on Security

- Passwords are never stored in plain text — they're hashed using
  Werkzeug's `generate_password_hash` (pbkdf2-sha256, from Python's `hashlib`).
- Sessions are signed using Flask's `secret_key`. **Change the secret key**
  in `app.py` before deploying to production, and load it from an
  environment variable instead of hardcoding it.
- All transaction queries are scoped to `user_id` from the session, so
  users can never view or edit each other's data.

## Tech Stack

| Layer      | Technology                     |
|------------|---------------------------------|
| Frontend   | HTML, CSS, Bootstrap 5, Chart.js |
| Backend    | Python, Flask                   |
| Database   | SQLite (MySQL-compatible schema included) |
| Auth       | Flask sessions + Werkzeug password hashing |

Enjoy tracking your expenses! 🎉
