import os
from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, track

# Initialize Rich Console
console = Console()

DATABASE_DIR = "database"
TRANSACTIONS_FILE = os.path.join(DATABASE_DIR, "transactions.txt")
BUDGETS_FILE = os.path.join(DATABASE_DIR, "budgets.txt")

def load_transactions():
    """Loads transactions from transactions.txt."""
    transactions = []
    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions

    with open(TRANSACTIONS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",", 4)  # Split into 5 parts, description might contain commas
            if len(parts) == 5:
                try:
                    date_str, type, category_source, amount_paisa, description = parts
                    transactions.append({
                        "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
                        "type": type,
                        "category_source": category_source,
                        "amount_paisa": int(amount_paisa),
                        "description": description if description else "N/A"
                    })
                except ValueError:
                    console.print(f"[red]Error parsing transaction line: {line.strip()}[/red]")
            else:
                console.print(f"[red]Skipping malformed transaction line: {line.strip()}[/red]")
    return transactions

def load_budgets():
    """Loads budgets from budgets.txt."""
    budgets = {}
    if not os.path.exists(BUDGETS_FILE):
        return budgets

    with open(BUDGETS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2:
                try:
                    category, amount_paisa = parts
                    budgets[category] = int(amount_paisa)
                except ValueError:
                    console.print(f"[red]Error parsing budget line: {line.strip()}[/red]")
            else:
                console.print(f"[red]Skipping malformed budget line: {line.strip()}[/red]")
    return budgets

def get_current_month_transactions(transactions):
    """Filters transactions for the current month."""
    today = datetime.now().date()
    return [t for t in transactions if t["date"].month == today.month and t["date"].year == today.year]

def get_transactions_by_month(transactions, year, month):
    """Filters transactions for a specific month and year."""
    return [t for t in transactions if t["date"].month == month and t["date"].year == year]

def get_last_month_transactions(transactions):
    """Filters transactions for the last month."""
    today = datetime.now().date()
    first_day_current_month = today.replace(day=1)
    last_month_date = first_day_current_month - timedelta(days=1)
    return [t for t in transactions if t["date"].month == last_month_date.month and t["date"].year == last_month_date.year]

def paisa_to_currency(amount_paisa):
    """Converts paisa to currency format (e.g., Rs 12.50)."""
    return f"Rs {amount_paisa / 100:.2f}"

def generate_pie_chart(data, title="Distribution"):
    """Generates an ASCII pie chart."""
    total = sum(data.values())
    if total == 0:
        console.print(f"\n[bold]{title}: No data to display.[/bold]")
        return

    console.print(f"\n[bold]{title}:[/bold]")
    max_label_length = max(len(label) for label in data.keys())
    
    # Sort data by value in descending order
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)

    console.print(f"\n[bold]{title}:[/bold]")
    max_label_length = max(len(label) for label in data.keys())
    
    # Sort data by value in descending order
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)

    for label, value in sorted_data:
        percentage = (value / total) * 100
        # Scale bar length to a maximum of 30 characters
        bar_length = int(30 * (value / total))
        bar = "█" * bar_length
        console.print(f"{label.ljust(max_label_length)} {bar} {percentage:.1f}% ({paisa_to_currency(value)})")

def analyze_spending():
    """Analyzes spending patterns and displays insights."""
    transactions = load_transactions()
    current_month_transactions = get_current_month_transactions(transactions)
    last_month_transactions = get_last_month_transactions(transactions)

    current_month_expenses = [t for t in current_month_transactions if t["type"] == "expense"]
    last_month_expenses = [t for t in last_month_transactions if t["type"] == "expense"]

    # Spending breakdown by category
    spending_by_category = defaultdict(int)
    for expense in current_month_expenses:
        spending_by_category[expense["category_source"]] += expense["amount_paisa"]

    console.print(Panel("[bold yellow]🚀 Spending Analysis[/bold yellow]", expand=False))
    generate_pie_chart(spending_by_category, "Spending by Category (Current Month)")

    # Top 3 spending categories
    sorted_spending = sorted(spending_by_category.items(), key=lambda item: item[1], reverse=True)
    console.print("\n[bold]Top 3 Spending Categories:[/bold]")
    for category, amount in sorted_spending[:3]:
        console.print(f"- {category}: {paisa_to_currency(amount)}")

    # Average daily expense (Burn Rate)
    total_current_month_expenses = sum(expense["amount_paisa"] for expense in current_month_expenses)
    today = datetime.now().date()
    days_in_month = today.day # Assuming we are interested in average up to today
    
    average_daily_expense = total_current_month_expenses / days_in_month if days_in_month > 0 else 0
    console.print(f"\n[bold]Average Daily Expense (Burn Rate):[/bold] {paisa_to_currency(int(average_daily_expense))}")

    # Comparison with last month
    total_last_month_expenses = sum(expense["amount_paisa"] for expense in last_month_expenses)
    console.print(f"\n[bold]Total Spending Last Month:[/bold] {paisa_to_currency(total_last_month_expenses)}")

    if total_last_month_expenses > 0:
        spending_change = ((total_current_month_expenses - total_last_month_expenses) / total_last_month_expenses) * 100
        if spending_change > 0:
            console.print(f"[red]Spending is up by {spending_change:.2f}% compared to last month.[/red]")
        elif spending_change < 0:
            console.print(f"[green]Spending is down by {abs(spending_change):.2f}% compared to last month.[/green]")
        else:
            console.print("[bold]Spending is the same as last month.[/bold]")
    elif total_current_month_expenses > 0:
        console.print("[red]Spending exists this month, but no spending last month for comparison.[/red]")
    else:
        console.print("[bold]No spending recorded for this or last month.[/bold]")

    # Spending trends (simple indication)
    if total_current_month_expenses > total_last_month_expenses and total_last_month_expenses > 0:
        console.print("[red]Spending trend: Upwards 📈[/red]")
    elif total_current_month_expenses < total_last_month_expenses:
        console.print("[green]Spending trend: Downwards 📉[/green]")
    else:
        console.print("[bold]Spending trend: Stable[/bold]")

def analyze_income():
    """Analyzes income patterns and displays insights."""
    transactions = load_transactions()
    current_month_transactions = get_current_month_transactions(transactions)
    last_month_transactions = get_last_month_transactions(transactions)

    current_month_income = [t for t in current_month_transactions if t["type"] == "income"]
    last_month_income = [t for t in last_month_transactions if t["type"] == "income"]

    # Income by source
    income_by_source = defaultdict(int)
    for income in current_month_income:
        income_by_source[income["category_source"]] += income["amount_paisa"]

    console.print(Panel("[bold green]💰 Income Analysis[/bold green]", expand=False))
    generate_pie_chart(income_by_source, "Income by Source (Current Month)")

    # Total income this month
    total_current_month_income = sum(income["amount_paisa"] for income in current_month_income)
    console.print(f"\n[bold]Total Income This Month:[/bold] {paisa_to_currency(total_current_month_income)}")

    # Comparison with last month
    total_last_month_income = sum(income["amount_paisa"] for income in last_month_income)
    console.print(f"\n[bold]Total Income Last Month:[/bold] {paisa_to_currency(total_last_month_income)}")

    if total_last_month_income > 0:
        income_change = ((total_current_month_income - total_last_month_income) / total_last_month_income) * 100
        if income_change > 0:
            console.print(f"[green]Income is up by {income_change:.2f}% compared to last month.[/green]")
        elif income_change < 0:
            console.print(f"[red]Income is down by {abs(income_change):.2f}% compared to last month.[/red]")
        else:
            console.print("[bold]Income is the same as last month.[/bold]")
    elif total_current_month_income > 0:
        console.print("[green]Income exists this month, but no income last month for comparison.[/green]")
    else:
        console.print("[bold]No income recorded for this or last month.[/bold]")

    # Income stability (simple indication)
    if total_current_month_income > total_last_month_income and total_last_month_income > 0:
        console.print("[green]Income trend: Upwards 📈[/green]")
    elif total_current_month_income < total_last_month_income:
        console.print("[red]Income trend: Downwards 📉[/red]")
    else:
        console.print("[bold]Income trend: Stable[/bold]")

def analyze_savings():
    """Analyzes savings patterns and displays insights."""
    transactions = load_transactions()
    current_month_transactions = get_current_month_transactions(transactions)

    current_month_income = sum(t["amount_paisa"] for t in current_month_transactions if t["type"] == "income")
    current_month_expenses = sum(t["amount_paisa"] for t in current_month_transactions if t["type"] == "expense")

    monthly_savings = current_month_income - current_month_expenses
    savings_rate = (monthly_savings / current_month_income) * 100 if current_month_income > 0 else 0

    console.print(Panel("[bold blue]💰 Savings Analysis[/bold blue]", expand=False))
    console.print(f"[bold]Monthly Savings:[/bold] {paisa_to_currency(monthly_savings)}")
    console.print(f"[bold]Savings Rate:[/bold] {savings_rate:.2f}%")

    # Savings trend (last 3 months)
    today = datetime.now().date()
    savings_trend_data = []

    for i in range(3): # Last 3 months including current
        target_month = today.month - i
        target_year = today.year
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_transactions = get_transactions_by_month(transactions, target_year, target_month)
        month_income = sum(t["amount_paisa"] for t in month_transactions if t["type"] == "income")
        month_expenses = sum(t["amount_paisa"] for t in month_transactions if t["type"] == "expense")
        month_savings = month_income - month_expenses
        savings_trend_data.append((f"{target_month}/{target_year}", month_savings))
    
    savings_trend_data.reverse() # Show oldest to newest
    
    console.print("\n[bold]Savings Trend (Last 3 Months):[/bold]")
    for month_year, savings in savings_trend_data:
        color = "green" if savings >= 0 else "red"
        console.print(f"- {month_year}: [{color}]{paisa_to_currency(savings)}[/{color}]")

    # Savings goal progress - currently not implemented as no budget data for goals
    console.print("\n[italic yellow]Savings goal progress feature requires setting up savings goals.[/italic yellow]")

def calculate_financial_health_score():
    """Calculates and displays a financial health score."""
    transactions = load_transactions()
    budgets = load_budgets()
    current_month_transactions = get_current_month_transactions(transactions)

    total_score = 0
    score_breakdown = {}

    current_month_income = sum(t["amount_paisa"] for t in current_month_transactions if t["type"] == "income")
    current_month_expenses = sum(t["amount_paisa"] for t in current_month_transactions if t["type"] == "expense")
    
    # Savings Rate (30 points)
    monthly_savings = current_month_income - current_month_expenses
    savings_rate = (monthly_savings / current_month_income) * 100 if current_month_income > 0 else 0
    savings_score = 0
    if savings_rate >= 20: # Excellent
        savings_score = 30
    elif savings_rate >= 10: # Good
        savings_score = 20
    elif savings_rate >= 0: # Fair
        savings_score = 10
    score_breakdown["Savings Rate"] = savings_score
    total_score += savings_score

    # Budget Adherence (25 points)
    budget_adherence_score = 0
    if budgets:
        total_budgeted = sum(budgets.values())
        total_spent_on_budgeted_categories = 0
        for expense in current_month_transactions:
            if expense["type"] == "expense" and expense["category_source"] in budgets:
                total_spent_on_budgeted_categories += expense["amount_paisa"]
        
        if total_budgeted > 0:
            utilization = (total_spent_on_budgeted_categories / total_budgeted) * 100
            if utilization <= 80: # Excellent
                budget_adherence_score = 25
            elif utilization <= 100: # Good
                budget_adherence_score = 15
            else: # Poor (over budget)
                budget_adherence_score = 5
        else:
            budget_adherence_score = 10 # No budget set, neutral score
    else:
        budget_adherence_score = 10 # No budgets defined

    score_breakdown["Budget Adherence"] = budget_adherence_score
    total_score += budget_adherence_score

    # Income vs Expenses (25 points)
    income_vs_expense_score = 0
    if current_month_income > current_month_expenses:
        income_vs_expense_score = 25
    elif current_month_income == current_month_expenses:
        income_vs_expense_score = 15
    else:
        income_vs_expense_score = 5
    score_breakdown["Income vs Expenses"] = income_vs_expense_score
    total_score += income_vs_expense_score

    # Debt Management (20 points) - Placeholder as debt management is not implemented
    debt_management_score = 0 # Assume neutral for now
    score_breakdown["Debt Management"] = debt_management_score
    total_score += debt_management_score

    console.print(Panel("[bold magenta]❤️ Financial Health Score[/bold magenta]", expand=False))
    console.print(f"\n[bold]Overall Score:[/bold] {total_score}/100")

    table = Table(title="Score Breakdown")
    table.add_column("Factor", style="cyan")
    table.add_column("Score", style="magenta")
    for factor, score in score_breakdown.items():
        table.add_row(factor, str(score))
    console.print(table)

    console.print("\n[bold]Recommendations:[/bold]")
    if savings_score < 20:
        console.print("- Aim to save at least 20% of your income to improve your savings rate.")
    if budget_adherence_score < 15:
        console.print("- Review your budget and try to stick to your spending limits. Consider setting realistic budgets.")
    if income_vs_expense_score < 25:
        console.print("- Focus on increasing your income or reducing your expenses to ensure income exceeds expenses.")
    if debt_management_score == 0:
        console.print("- [italic]Debt management features are not yet implemented. This score factor is currently neutral.[/italic]")

def generate_comprehensive_report():
    """Generates a comprehensive financial report."""
    console.print(Panel("[bold bright_white on blue]📊 Comprehensive Financial Report [/bold bright_white on blue]", expand=False))
    
    # Month Overview (can be expanded)
    today = datetime.now().date()
    console.print(f"\n[bold]Report for:[/bold] {today.strftime('%B %Y')}")

    # Run all analysis functions
    analyze_income()
    analyze_spending()
    analyze_savings()
    calculate_financial_health_score()

    console.print(Panel("[bold green]Report Generation Complete![/bold green]", expand=False))













def load_transactions():
    """Loads transactions from transactions.txt."""
    transactions = []
    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions

    with open(TRANSACTIONS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",", 4)  # Split into 5 parts, description might contain commas
            if len(parts) == 5:
                try:
                    date_str, type, category_source, amount_paisa, description = parts
                    transactions.append({
                        "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
                        "type": type,
                        "category_source": category_source,
                        "amount_paisa": int(amount_paisa),
                        "description": description if description else "N/A"
                    })
                except ValueError:
                    console.print(f"[red]Error parsing transaction line: {line.strip()}[/red]")
            else:
                console.print(f"[red]Skipping malformed transaction line: {line.strip()}[/red]")
    return transactions

def load_budgets():
    """Loads budgets from budgets.txt."""
    budgets = {}
    if not os.path.exists(BUDGETS_FILE):
        return budgets

    with open(BUDGETS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 2:
                try:
                    category, amount_paisa = parts
                    budgets[category] = int(amount_paisa)
                except ValueError:
                    console.print(f"[red]Error parsing budget line: {line.strip()}[/red]")
            else:
                console.print(f"[red]Skipping malformed budget line: {line.strip()}[/red]")
    return budgets


