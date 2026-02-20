"""
app.py — Flask web server for Personal Budget Tracker
Run: python app.py
Visit: http://localhost:5000
"""

import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from expense import Expense
from budget import Budget
from analytics import Analytics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Flask uses relative 'templates' and 'static' folders next to app.py
app = Flask(__name__)
app.secret_key = "budget-tracker-secret"

budget = Budget()
analytics = Analytics(budget)


# ─────────────────────────────────────────────
#  HOME — List all expenses
# ─────────────────────────────────────────────
@app.route("/")
def index():
    category = request.args.get("category", "")
    month = request.args.get("month", "")
    expenses = budget.read_all(
        category=category if category else None,
        month=month if month else None
    )
    total = sum(e.amount for e in expenses)
    return render_template("index.html",
                           expenses=expenses,
                           total=total,
                           categories=Expense.CATEGORIES,
                           selected_category=category,
                           selected_month=month)


# ─────────────────────────────────────────────
#  ADD Expense
# ─────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add():
    try:
        amount = float(request.form["amount"])
        category = request.form["category"]
        description = request.form["description"]
        date_str = request.form["date"] or None
        exp = budget.add(Expense(amount, category, description, date_str))
        flash(f"Expense added: {exp.description} (₱{exp.amount:,.2f})", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("index"))


# ─────────────────────────────────────────────
#  EDIT — Get expense data for modal
# ─────────────────────────────────────────────
@app.route("/edit/<expense_id>")
def edit(expense_id):
    expenses = budget.read_all()
    exp = next((e for e in expenses if e.id == expense_id), None)
    if not exp:
        return jsonify({"error": "Not found"}), 404
    return jsonify(exp.to_dict())


# ─────────────────────────────────────────────
#  UPDATE Expense
# ─────────────────────────────────────────────
@app.route("/update/<expense_id>", methods=["POST"])
def update(expense_id):
    try:
        fields = {
            "amount": float(request.form["amount"]),
            "category": request.form["category"],
            "description": request.form["description"],
            "date": request.form["date"],
        }
        updated = budget.update(expense_id, **fields)
        if updated:
            flash(f"Updated: {updated.description}", "success")
        else:
            flash("Expense not found.", "danger")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for("index"))


# ─────────────────────────────────────────────
#  DELETE Expense
# ─────────────────────────────────────────────
@app.route("/delete/<expense_id>", methods=["POST"])
def delete(expense_id):
    success = budget.delete(expense_id)
    flash("Expense deleted." if success else "Not found.",
          "success" if success else "danger")
    return redirect(url_for("index"))


# ─────────────────────────────────────────────
#  ANALYTICS PAGE
# ─────────────────────────────────────────────
@app.route("/analytics")
def analytics_page():
    month = request.args.get("month", "")
    summary = analytics.summary(month=month if month else None)
    ts = int(time.time())
    pie = analytics.pie_chart(month=month if month else None)
    line = analytics.line_chart(month=month if month else None)
    monthly = analytics.monthly_chart()
    return render_template("index.html",
                           view="analytics",
                           summary=summary,
                           pie_chart=pie,
                           line_chart=line,
                           monthly_chart=monthly,
                           selected_month=month,
                           categories=Expense.CATEGORIES,
                           ts=ts)


import threading
import webview

def start_flask():
    app.run(debug=False, port=5000)

if __name__ == "__main__":
    # Start Flask in background thread
    threading.Thread(target=start_flask, daemon=True).start()

    # Create desktop window
    webview.create_window(
        "Personal Budget Tracker",
        "http://127.0.0.1:5000",
        width=1000,
        height=700
    )

    webview.start()
