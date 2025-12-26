import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import ProgressBar

# Assuming these are available from other modules or will be implemented here
# from ..transactions.transactions import get_transactions
# from ..budgets.budgets import get_budgets

console = Console()

def get_transactions():
    """
    Reads transactions from transactions.txt.
    Returns a list of dictionaries, each representing a transaction.
    """
    transactions = []
    try:
        with open("database/transactions.txt", "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 6:
                    transactions.append({
                        "date": datetime.datetime.strptime(parts[0], "%Y-%m-%d").date(),
                        "type": parts[1],
                        "category": parts[2],
                        "amount": int(parts[3]),  # Stored as paisa/cents
                        "description": parts[4],
                        "id": parts[5]
                    })
    except FileNotFoundError:
        pass  # No transactions yet
    return transactions

def get_budgets():
    """
    Reads budgets from budgets.txt.
    Returns a dictionary where keys are categories and values are budget amounts (in paisa).
    """
    budgets = {}
    try:
        with open("database/budgets.txt", "r") as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    budgets[parts[0]] = int(parts[1])
    except FileNotFoundError:
        pass  # No budgets yet
    return budgets

def show_recommendations():
    """
    Provides a daily financial overview including today's spending,
    remaining daily budget, alerts, and a quick tip.
    """
    today = datetime.date.today()
    transactions = get_transactions()
    budgets = get_budgets()

    # Calculate today's spending
    today_spending = sum(
        t["amount"] for t in transactions
        if t["date"] == today and t["type"] == "expense"
    )

    # Calculate total monthly budget
    total_monthly_budget = sum(budgets.values())

    # Get current month's total expenses
    current_month_expenses = sum(
        t["amount"] for t in transactions
        if t["date"].year == today.year and t["date"].month == today.month and t["type"] == "expense"
    )
    
    # Calculate days in current month
    if today.month == 12:
        days_in_month = (datetime.date(today.year + 1, 1, 1) - datetime.date(today.year, 12, 1)).days
    else:
        days_in_month = (datetime.date(today.year, today.month + 1, 1) - datetime.date(today.year, today.month, 1)).days

    # Calculate remaining daily budget
    remaining_days = days_in_month - today.day + 1
    
    daily_budget = 0
    if total_monthly_budget > 0 and remaining_days > 0:
        daily_budget = (total_monthly_budget - current_month_expenses) / remaining_days

    console.print(Panel(f"📊 Daily Financial Check ({today.strftime('%b %d, %Y')})", style="bold blue"))
    console.print(f"Today's Spending: [red]Rs {today_spending / 100:.2f}[/red]")
    
    daily_budget_status = "✅" if (daily_budget * 100) >= today_spending else "⚠️"
    console.print(f"Remaining Daily Budget: [green]Rs {daily_budget / 100:.2f}[/green] {daily_budget_status}")
    console.print(f"Remaining: [green]Rs {(daily_budget * remaining_days - today_spending) / 100:.2f}[/green]")

    console.print("\n⚠️  Alerts:")
    # Placeholder for alerts
    for category, budget_amount in budgets.items():
        category_expenses = sum(
            t["amount"] for t in transactions
            if t["date"].year == today.year and t["date"].month == today.month
            and t["type"] == "expense" and t["category"] == category
        )
        if budget_amount > 0 and (category_expenses / budget_amount) >= 0.8:
            console.print(f"• [yellow]{category}[/yellow] category at [yellow]{(category_expenses / budget_amount):.0%}[/yellow] budget (Rs {category_expenses / 100:.2f} / Rs {budget_amount / 100:.2f})")

    # Placeholder for a quick tip
    console.print("\n💡 Tip: You're on track! Consider moving Rs 500 to savings.")

def main():
    """Main function to run the smart assistant features."""
    daily_financial_check()

if __name__ == "__main__":
    main()
