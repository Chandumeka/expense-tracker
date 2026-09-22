"""
app.py
-------
Main Flask application for the Personal Expense Tracker.

Run with:  python app.py
Then open: http://127.0.0.1:5000

Demo login (auto-seeded on first run):
    email:    demo@example.com
    password: password123
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import re

from database import init_db
from models import User, Transaction, VALID_CATEGORIES

# ------------------------------------------------------------------
# APP CONFIGURATION
# ------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"  # required for sessions & flash messages

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ------------------------------------------------------------------
# AUTH DECORATOR
# ------------------------------------------------------------------
def login_required(view_func):
    """Redirects to login page if the user does not have an active session."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# ------------------------------------------------------------------
# ROOT
# ------------------------------------------------------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# SIGNUP
# ------------------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # ---- Validation ----
        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        if not EMAIL_REGEX.match(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("signup.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        if User.find_by_email(email):
            flash("An account with this email already exists. Please log in.", "danger")
            return render_template("signup.html")

        # ---- Create account ----
        success = User.create(name, email, password)
        if success:
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Something went wrong. Please try again.", "danger")

    return render_template("signup.html")


# ------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.find_by_email(email)

        if user and User.verify_password(user, password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")


# ------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    summary = Transaction.get_summary(user_id)
    category_data = Transaction.get_expense_by_category(user_id)

    # Show only the 5 most recent transactions on the dashboard
    recent_transactions = Transaction.get_all_for_user(user_id)[:5]

    return render_template(
        "dashboard.html",
        summary=summary,
        category_labels=list(category_data.keys()),
        category_values=list(category_data.values()),
        recent_transactions=recent_transactions,
    )


# ------------------------------------------------------------------
# PROFILE - VIEW + EDIT
# ------------------------------------------------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user = User.find_by_id(user_id)

    if not user:
        flash("Account not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_new_password = request.form.get("confirm_new_password", "")

        # ---- Validation ----
        if not name or not email:
            flash("Name and email are required.", "danger")
            return redirect(url_for("profile"))

        if not EMAIL_REGEX.match(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("profile"))

        if not current_password:
            flash("Enter your current password to save changes.", "danger")
            return redirect(url_for("profile"))

        # Current password is always required to confirm identity before any change
        if not User.verify_password(user, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("profile"))

        # If changing the email, make sure no other account already has it
        if email.lower() != user["email"].lower() and User.email_taken_by_other(email, user_id):
            flash("That email is already in use by another account.", "danger")
            return redirect(url_for("profile"))

        # New password is optional — only validate/apply it if they typed one
        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters long.", "danger")
                return redirect(url_for("profile"))
            if new_password != confirm_new_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("profile"))

        User.update_profile(user_id, name, email, new_password or None)
        session["user_name"] = name  # keep navbar greeting in sync
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ------------------------------------------------------------------
# TRANSACTIONS - LIST + FILTER
# ------------------------------------------------------------------
@app.route("/transactions")
@login_required
def transactions():
    user_id = session["user_id"]

    category = request.args.get("category", "All")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")

    txns = Transaction.get_all_for_user(
        user_id,
        category=category if category != "All" else None,
        date_from=date_from or None,
        date_to=date_to or None,
    )

    return render_template(
        "transactions.html",
        transactions=txns,
        categories=["All"] + VALID_CATEGORIES,
        selected_category=category,
        date_from=date_from,
        date_to=date_to,
    )


# ------------------------------------------------------------------
# TRANSACTIONS - ADD
# ------------------------------------------------------------------
@app.route("/transactions/add", methods=["POST"])
@login_required
def add_transaction():
    user_id = session["user_id"]

    t_type = request.form.get("type")
    category = request.form.get("category")
    amount = request.form.get("amount")
    txn_date = request.form.get("txn_date")
    note = request.form.get("note", "").strip()

    # ---- Validation ----
    if t_type not in ("income", "expense"):
        flash("Invalid transaction type.", "danger")
        return redirect(url_for("transactions"))

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError):
        flash("Please enter a valid positive amount.", "danger")
        return redirect(url_for("transactions"))

    if not txn_date:
        flash("Please select a date.", "danger")
        return redirect(url_for("transactions"))

    Transaction.create(user_id, t_type, category, amount, txn_date, note)
    flash(f"{t_type.capitalize()} added successfully!", "success")
    return redirect(request.referrer or url_for("dashboard"))


# ------------------------------------------------------------------
# TRANSACTIONS - EDIT
# ------------------------------------------------------------------
@app.route("/transactions/edit/<int:txn_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(txn_id):
    user_id = session["user_id"]
    txn = Transaction.get_by_id(txn_id, user_id)

    if not txn:
        flash("Transaction not found.", "danger")
        return redirect(url_for("transactions"))

    if request.method == "POST":
        t_type = request.form.get("type")
        category = request.form.get("category")
        amount = request.form.get("amount")
        txn_date = request.form.get("txn_date")
        note = request.form.get("note", "").strip()

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (TypeError, ValueError):
            flash("Please enter a valid positive amount.", "danger")
            return render_template("edit_transaction.html", txn=txn, categories=VALID_CATEGORIES)

        Transaction.update(txn_id, user_id, t_type, category, amount, txn_date, note)
        flash("Transaction updated successfully!", "success")
        return redirect(url_for("transactions"))

    return render_template("edit_transaction.html", txn=txn, categories=VALID_CATEGORIES)


# ------------------------------------------------------------------
# TRANSACTIONS - DELETE
# ------------------------------------------------------------------
@app.route("/transactions/delete/<int:txn_id>", methods=["POST"])
@login_required
def delete_transaction(txn_id):
    user_id = session["user_id"]
    Transaction.delete(txn_id, user_id)
    flash("Transaction deleted.", "info")
    return redirect(request.referrer or url_for("transactions"))


# ------------------------------------------------------------------
# JSON API - used by Chart.js on the dashboard (AJAX refresh)
# ------------------------------------------------------------------
@app.route("/api/summary")
@login_required
def api_summary():
    user_id = session["user_id"]
    summary = Transaction.get_summary(user_id)
    category_data = Transaction.get_expense_by_category(user_id)
    return jsonify({
        "summary": summary,
        "categories": category_data,
    })


# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
if __name__ == "__main__":
    init_db(seed_demo=True)   # creates tables + demo data if DB is empty
    app.run(debug=True)
