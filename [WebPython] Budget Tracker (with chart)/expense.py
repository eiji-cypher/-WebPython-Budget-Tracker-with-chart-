"""
expense.py — Expense data model
"""

import uuid
from datetime import datetime


class Expense:
    CATEGORIES = [
        "Food", "Transport", "Housing", "Health",
        "Entertainment", "Shopping", "Education", "Other"
    ]

    def __init__(self, amount: float, category: str, description: str,
                 date_str: str = None, expense_id: str = None):
        self.id = expense_id or str(uuid.uuid4())[:8]
        self.amount = float(amount)
        self.category = category if category in self.CATEGORIES else "Other"
        self.description = description.strip()
        self.date = date_str or datetime.today().strftime("%Y-%m-%d")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Expense":
        return cls(
            amount=d["amount"],
            category=d["category"],
            description=d["description"],
            date_str=d["date"],
            expense_id=d["id"],
        )

    def __str__(self):
        return (f"[{self.id}] {self.date} | {self.category:<15} | "
                f"₱{self.amount:>10,.2f} | {self.description}")
