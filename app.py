import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email

app = Flask(__name__)
app.secret_key = "dev-secret-key"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not all([name, email, password, confirm_password]):
        return render_template("register.html", error="All fields are required.")

    if password != confirm_password:
        return render_template("register.html", error="Passwords do not match.")

    try:
        create_user(name, email, password)
    except sqlite3.IntegrityError:
        return render_template("register.html", error="Email already registered.")

    flash("Account created! Please sign in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("landing"))
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user_id"] = user["id"]
    return render_template("login.html", success=f"Welcome back, {user['name']}!")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "initials": "AJ",
        "member_since": "January 2024",
    }

    stats = {
        "total_spent": "₹24,850",
        "transaction_count": 47,
        "top_category": "Food",
    }

    transactions = [
        {"id": 1, "date": "2024-01-15", "description": "Grocery shopping",    "category": "Food",          "amount": "₹1,250"},
        {"id": 2, "date": "2024-01-14", "description": "Metro card recharge",  "category": "Transport",     "amount": "₹500"},
        {"id": 3, "date": "2024-01-13", "description": "Netflix subscription", "category": "Entertainment", "amount": "₹649"},
        {"id": 4, "date": "2024-01-12", "description": "Electricity bill",     "category": "Bills",         "amount": "₹2,100"},
        {"id": 5, "date": "2024-01-11", "description": "Doctor consultation",  "category": "Health",        "amount": "₹800"},
        {"id": 6, "date": "2024-01-10", "description": "Amazon order",         "category": "Shopping",      "amount": "₹1,399"},
    ]

    categories = [
        {"name": "Food",          "amount": "₹8,450", "pct": 34},
        {"name": "Bills",         "amount": "₹6,200", "pct": 25},
        {"name": "Transport",     "amount": "₹4,100", "pct": 17},
        {"name": "Entertainment", "amount": "₹3,200", "pct": 13},
        {"name": "Health",        "amount": "₹1,900", "pct": 8},
        {"name": "Shopping",      "amount": "₹700",   "pct": 3},
    ]

    return render_template("profile.html", user=user, stats=stats, transactions=transactions, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
