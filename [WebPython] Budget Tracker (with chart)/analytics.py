"""
analytics.py — Spending analytics: summaries and matplotlib charts
Saves charts as PNG files for web display.
"""

import os
from collections import defaultdict
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from budget import Budget
from expense import Expense

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(BASE_DIR, "static", "charts")


class Analytics:
    def __init__(self, budget: Budget):
        self.budget = budget
        os.makedirs(CHART_DIR, exist_ok=True)

    # ── Aggregation Helpers ───────────────────
    def _by_category(self, expenses):
        totals = defaultdict(float)
        for e in expenses:
            totals[e.category] += e.amount
        return dict(totals)

    def _by_day(self, expenses):
        totals = defaultdict(float)
        for e in expenses:
            totals[e.date] += e.amount
        return dict(sorted(totals.items()))

    def _by_month(self, expenses):
        totals = defaultdict(float)
        for e in expenses:
            totals[e.date[:7]] += e.amount
        return dict(sorted(totals.items()))

    # ── Summary Data ─────────────────────────
    def summary(self, month=None):
        expenses = self.budget.read_all(month=month)
        total = sum(e.amount for e in expenses)
        by_cat = self._by_category(expenses)
        breakdown = [
            {"category": cat, "amount": amt,
             "percent": round(amt / total * 100, 1) if total else 0}
            for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1])
        ]
        return {"total": total, "count": len(expenses), "breakdown": breakdown}

    # ── Pie Chart ────────────────────────────
    def pie_chart(self, month=None):
        expenses = self.budget.read_all(month=month)
        if not expenses:
            return None
        by_cat = self._by_category(expenses)
        labels, sizes = list(by_cat.keys()), list(by_cat.values())
        colors = list(plt.cm.Set3.colors[:len(labels)])
        fig, ax = plt.subplots(figsize=(7, 5))
        _, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct="%1.1f%%",
            colors=colors, explode=[0.04] * len(labels),
            startangle=140, textprops={"fontsize": 11}
        )
        for at in autotexts:
            at.set_fontweight("bold")
        title = "Spending by Category" + (f"  ({month})" if month else "")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=20)
        plt.tight_layout()
        path = os.path.join(CHART_DIR, "pie.png")
        plt.savefig(path, dpi=120, bbox_inches="tight")
        plt.close()
        return "static/charts/pie.png"

    # ── Line Chart ───────────────────────────
    def line_chart(self, month=None):
        expenses = self.budget.read_all(month=month)
        if not expenses:
            return None
        by_day = self._by_day(expenses)
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in by_day]
        amounts = list(by_day.values())
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(dates, amounts, marker="o", linewidth=2,
                color="#4C72B0", markersize=6, markerfacecolor="#DD8452")
        ax.fill_between(dates, amounts, alpha=0.15, color="#4C72B0")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate()
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Amount (₱)", fontsize=11)
        ax.set_title("Daily Spending Trend" + (f"  ({month})" if month else ""),
                     fontsize=13, fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₱{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()
        path = os.path.join(CHART_DIR, "line.png")
        plt.savefig(path, dpi=120, bbox_inches="tight")
        plt.close()
        return "static/charts/line.png"

    # ── Monthly Bar Chart ────────────────────
    def monthly_chart(self):
        expenses = self.budget.read_all()
        if not expenses:
            return None
        by_month = self._by_month(expenses)
        months, amounts = list(by_month.keys()), list(by_month.values())
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(months, amounts, color="#4C72B0", edgecolor="white", width=0.5)
        for bar, amt in zip(bars, amounts):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(amounts) * 0.01,
                    f"₱{amt:,.0f}", ha="center", va="bottom", fontsize=9)
        ax.set_xlabel("Month", fontsize=11)
        ax.set_ylabel("Total (₱)", fontsize=11)
        ax.set_title("Monthly Spending Overview", fontsize=13, fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₱{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()
        path = os.path.join(CHART_DIR, "monthly.png")
        plt.savefig(path, dpi=120, bbox_inches="tight")
        plt.close()
        return "static/charts/monthly.png"
