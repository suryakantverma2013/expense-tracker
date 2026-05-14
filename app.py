import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, get_user_by_id, get_expenses_by_user

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

    user_id = session["user_id"]
    user_row = get_user_by_id(user_id)
    expenses = get_expenses_by_user(user_id)

    try:
        dt = datetime.strptime(user_row["created_at"], "%Y-%m-%d %H:%M:%S")
        member_since = dt.strftime("%B %Y")
    except (ValueError, TypeError):
        member_since = "Unknown"

    name = user_row["name"]
    user = {
        "name": name,
        "email": user_row["email"],
        "initials": "".join(p[0].upper() for p in name.split()[:2]),
        "member_since": member_since,
    }

    # Aggregate stats
    total = sum(e["amount"] for e in expenses)
    cat_totals = {}
    for e in expenses:
        cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]
    top_category = max(cat_totals, key=cat_totals.get) if cat_totals else None

    stats = {
        "total_spent": f"₹{total:,.0f}",
        "transaction_count": len(expenses),
        "top_category": top_category or "—",
    }

    transactions = [
        {
            "id": e["id"],
            "date": e["date"],
            "description": e["description"] or "—",
            "category": e["category"],
            "amount": f"₹{e['amount']:,.0f}",
        }
        for e in expenses[:20]
    ]

    categories = sorted(
        [
            {
                "name": cat,
                "amount": f"₹{amt:,.0f}",
                "pct": round((amt / total) * 100) if total else 0,
            }
            for cat, amt in cat_totals.items()
        ],
        key=lambda x: x["pct"],
        reverse=True,
    )

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
