"""
budget.py — Budget CRUD operations with CSV file persistence
"""

import os
import csv
from expense import Expense

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Budget:
    FILE = os.path.join(BASE_DIR, "expenses.csv")
    FIELDNAMES = ["id", "amount", "category", "description", "date"]

    def __init__(self):
        self.expenses: list[Expense] = []
        self._load()

    # ── Persistence ──────────────────────────
    def _load(self):
        if not os.path.exists(self.FILE):
            return
        with open(self.FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.expenses.append(Expense.from_dict(row))

    def _save(self):
        with open(self.FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for exp in self.expenses:
                writer.writerow(exp.to_dict())

    # ── CRUD ─────────────────────────────────
    def add(self, expense: Expense) -> Expense:
        self.expenses.append(expense)
        self._save()
        return expense

    def read_all(self, category: str = None, month: str = None) -> list[Expense]:
        result = self.expenses
        if category:
            result = [e for e in result if e.category.lower() == category.lower()]
        if month:
            result = [e for e in result if e.date.startswith(month)]
        return result

    def update(self, expense_id: str, **kwargs) -> "Expense | None":
        for exp in self.expenses:
            if exp.id == expense_id:
                if "amount" in kwargs:
                    exp.amount = float(kwargs["amount"])
                if "category" in kwargs and kwargs["category"] in Expense.CATEGORIES:
                    exp.category = kwargs["category"]
                if "description" in kwargs:
                    exp.description = kwargs["description"].strip()
                if "date" in kwargs:
                    exp.date = kwargs["date"]
                self._save()
                return exp
        return None

    def delete(self, expense_id: str) -> bool:
        original = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.id != expense_id]
        if len(self.expenses) < original:
            self._save()
            return True
        return False

    def total(self, **filters) -> float:
        return sum(e.amount for e in self.read_all(**filters))
