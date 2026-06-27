"""
Expense Tracker - WeIntern Week 2 Task 1
Tracks daily expenses, categorizes spending, and generates summaries.
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

# ── Constants ────────────────────────────────────────────────────────────────

DATA_FILE = "expenses.csv"
FIELDNAMES = ["id", "date", "amount", "category", "description"]
CATEGORIES = [
    "Food", "Transport", "Shopping", "Entertainment",
    "Health", "Utilities", "Education", "Other"
]


# ── File persistence ─────────────────────────────────────────────────────────

def load_expenses():
    """Load expenses from CSV file. Returns a list of dicts."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expenses = []
        for row in reader:
            row["amount"] = float(row["amount"])
            expenses.append(row)
        return expenses


def save_expenses(expenses):
    """Save the full expenses list to CSV."""
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(expenses)


# ── Core functions ───────────────────────────────────────────────────────────

def next_id(expenses):
    """Generate the next integer ID."""
    return str(max((int(e["id"]) for e in expenses), default=0) + 1)


def add_expense(expenses):
    """Prompt the user for expense details and append to the list."""
    print("\n─── Add Expense ───")

    # Amount
    while True:
        try:
            amount = float(input("Amount (₹): ").strip())
            if amount <= 0:
                raise ValueError
            break
        except ValueError:
            print("  Please enter a positive number.")

    # Category
    print("Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    while True:
        try:
            choice = int(input("Choose category (1-{}): ".format(len(CATEGORIES))))
            if 1 <= choice <= len(CATEGORIES):
                category = CATEGORIES[choice - 1]
                break
        except ValueError:
            pass
        print("  Invalid choice.")

    # Description
    description = input("Description: ").strip() or "—"

    # Date
    date_str = input("Date (YYYY-MM-DD, leave blank for today): ").strip()
    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("  Invalid date; using today.")
            date_str = datetime.today().strftime("%Y-%m-%d")

    expense = {
        "id": next_id(expenses),
        "date": date_str,
        "amount": amount,
        "category": category,
        "description": description,
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"  ✓ Expense #{expense['id']} saved.")


def view_expenses(expenses, title="All Expenses"):
    """Print expenses in a formatted table."""
    if not expenses:
        print("  No expenses found.")
        return

    print(f"\n─── {title} ───")
    header = f"{'ID':>4}  {'Date':<12}  {'Amount':>10}  {'Category':<15}  Description"
    print(header)
    print("─" * len(header))
    total = 0.0
    for e in expenses:
        print(f"{e['id']:>4}  {e['date']:<12}  ₹{e['amount']:>9.2f}  {e['category']:<15}  {e['description']}")
        total += e["amount"]
    print("─" * len(header))
    print(f"{'TOTAL':>4}  {'':12}  ₹{total:>9.2f}")


def filter_by_category(expenses):
    """Let user pick a category and show matching expenses."""
    print("\nCategories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    choice = input("Choose category (1-{}): ".format(len(CATEGORIES))).strip()
    try:
        category = CATEGORIES[int(choice) - 1]
    except (ValueError, IndexError):
        print("  Invalid choice.")
        return
    filtered = [e for e in expenses if e["category"] == category]
    view_expenses(filtered, title=f"Expenses — {category}")


def filter_by_date_range(expenses):
    """Filter expenses between two dates entered by the user."""
    print("\n─── Filter by Date Range ───")
    start = input("Start date (YYYY-MM-DD): ").strip()
    end   = input("End date   (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end,   "%Y-%m-%d")
    except ValueError:
        print("  Invalid date format.")
        return
    filtered = [e for e in expenses if start <= e["date"] <= end]
    view_expenses(filtered, title=f"Expenses {start} → {end}")


def monthly_summary(expenses):
    """Show total and % breakdown per category for a chosen month."""
    print("\n─── Monthly Summary ───")
    month = input("Enter month (YYYY-MM): ").strip()
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("  Invalid format.")
        return

    filtered = [e for e in expenses if e["date"].startswith(month)]
    if not filtered:
        print(f"  No expenses found for {month}.")
        return

    totals   = defaultdict(float)
    grand    = 0.0
    for e in filtered:
        totals[e["category"]] += e["amount"]
        grand += e["amount"]

    print(f"\n  Summary for {month}  (Grand total: ₹{grand:.2f})\n")
    print(f"  {'Category':<15}  {'Amount':>10}  {'Share':>7}")
    print("  " + "─" * 38)
    for cat, amt in sorted(totals.items(), key=lambda x: -x[1]):
        pct = (amt / grand) * 100
        print(f"  {cat:<15}  ₹{amt:>9.2f}  {pct:>6.1f}%")

    # Optional pie chart
    try:
        import matplotlib.pyplot as plt
        labels = list(totals.keys())
        sizes  = [totals[k] for k in labels]
        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title(f"Spending Distribution — {month}")
        plt.tight_layout()
        plt.savefig(f"summary_{month}.png")
        print(f"\n  Pie chart saved as summary_{month}.png")
        plt.show()
    except ImportError:
        pass  # matplotlib not installed — skip silently


def delete_expense(expenses):
    """Remove an expense by ID."""
    eid = input("Enter expense ID to delete: ").strip()
    for i, e in enumerate(expenses):
        if e["id"] == eid:
            expenses.pop(i)
            save_expenses(expenses)
            print(f"  ✓ Expense #{eid} deleted.")
            return
    print("  ID not found.")


# ── Main menu ────────────────────────────────────────────────────────────────

def main():
    expenses = load_expenses()
    menu = [
        ("Add expense",            lambda: add_expense(expenses)),
        ("View all expenses",      lambda: view_expenses(expenses)),
        ("Filter by category",     lambda: filter_by_category(expenses)),
        ("Filter by date range",   lambda: filter_by_date_range(expenses)),
        ("Monthly summary",        lambda: monthly_summary(expenses)),
        ("Delete expense",         lambda: delete_expense(expenses)),
        ("Quit",                   None),
    ]

    print("\n╔══════════════════════════╗")
    print("║     💰 Expense Tracker    ║")
    print("╚══════════════════════════╝")

    while True:
        print()
        for i, (label, _) in enumerate(menu, 1):
            print(f"  {i}. {label}")
        choice = input("\nChoose an option: ").strip()
        try:
            idx = int(choice) - 1
            label, action = menu[idx]
        except (ValueError, IndexError):
            print("  Invalid option.")
            continue

        if action is None:   # Quit
            print("  Goodbye!")
            break
        action()


if __name__ == "__main__":
    main()
