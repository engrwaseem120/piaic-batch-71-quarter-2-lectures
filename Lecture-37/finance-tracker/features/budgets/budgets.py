import questionary
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress_bar import ProgressBar

# Initialize Rich Console
console = Console()

# --- Data Storage ---
BUDGETS_FILE = "database/budgets.txt"
TRANSACTIONS_FILE = "database/transactions.txt"

# --- Budget Categories ---
BUDGET_CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Other']

def set_budget():
    """
    Sets a monthly budget for a specific category.
    """
    try:
        category = questionary.select(
            "Select a category to set a budget for:",
            choices=BUDGET_CATEGORIES
        ).ask()

        if not category:
            return

        amount_str = questionary.text(f"Enter the monthly budget for {category}:").ask()
        budget_amount = int(float(amount_str) * 100)  # Store as cents

        if budget_amount <= 0:
            console.print("[bold red]Invalid amount. Please enter a positive number.[/bold red]")
            return

        # Read existing budgets
        try:
            with open(BUDGETS_FILE, "r") as f:
                budgets = f.readlines()
        except FileNotFoundError:
            budgets = []

        # Update budget if category exists, otherwise add new
        updated = False
        with open(BUDGETS_FILE, "w") as f:
            for line in budgets:
                if line.startswith(f"{category},"):
                    f.write(f"{category},{budget_amount}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"{category},{budget_amount}\n")

        console.print(f"[bold green]Budget for {category} set to {amount_str}![/bold green]")

    except (ValueError, TypeError):
        console.print("[bold red]Invalid amount. Please enter a valid number.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")


def view_budgets():
    """
    Displays budget vs. actual spending for the current month.
    """
    try:
        # 1. Read budgets
        try:
            with open(BUDGETS_FILE, "r") as f:
                budget_lines = f.readlines()
        except FileNotFoundError:
            console.print("[bold yellow]No budgets set. Please set a budget first.[/bold yellow]")
            return

        budgets = {}
        for line in budget_lines:
            category, amount = line.strip().split(',')
            budgets[category] = int(amount)

        # 2. Read transactions and calculate spending for the current month
        try:
            with open(TRANSACTIONS_FILE, "r") as f:
                transactions = f.readlines()
        except FileNotFoundError:
            transactions = []

        spent_by_category = {cat: 0 for cat in BUDGET_CATEGORIES}
        current_month = datetime.now().strftime("%Y-%m")

        for transaction in transactions:
            date, trans_type, category, amount, _ = transaction.strip().split(',', 4)
            if date.startswith(current_month) and trans_type == "expense" and category in spent_by_category:
                spent_by_category[category] += int(amount)
        
        # 3. Create and display the table
        table = Table(title=f"[bold blue]Budget Status for {datetime.now().strftime('%B %Y')}[/bold blue]")
        table.add_column("Category", style="cyan")
        table.add_column("Budget", justify="right", style="green")
        table.add_column("Spent", justify="right", style="red")
        table.add_column("Remaining", justify="right", style="yellow")
        table.add_column("Utilization %", justify="center")
        table.add_column("Status", justify="center")

        total_budget = 0
        total_spent = 0
        categories_over_budget = []

        for category, budget_amount in budgets.items():
            spent_amount = spent_by_category.get(category, 0)
            remaining_amount = budget_amount - spent_amount
            utilization = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0

            total_budget += budget_amount
            total_spent += spent_amount

            # Determine status and color
            if utilization > 100:
                status = "[bold red]Over[/bold red]"
                categories_over_budget.append(category)
                progress = ProgressBar(total=100, completed=100, complete_style="red")
            elif utilization >= 70:
                status = "[bold yellow]Warning[/bold yellow]"
                progress = ProgressBar(total=100, completed=utilization, complete_style="yellow")
            else:
                status = "[bold green]OK[/bold green]"
                progress = ProgressBar(total=100, completed=utilization, complete_style="green")
            
            table.add_row(
                category,
                f"{budget_amount / 100:.2f}",
                f"{spent_amount / 100:.2f}",
                f"{remaining_amount / 100:.2f}",
                progress,
                status
            )

        console.print(table)

        # 4. Display overall summary
        total_remaining = total_budget - total_spent
        overall_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        summary_table = Table(title="[bold blue]Overall Monthly Summary[/bold blue]", expand=True)
        summary_table.add_column("Total Budget", style="green", justify="right")
        summary_table.add_column("Total Spent", style="red", justify="right")
        summary_table.add_column("Total Remaining", style="yellow", justify="right")
        summary_table.add_column("Overall Utilization", justify="center")

        summary_table.add_row(
            f"{total_budget / 100:.2f}",
            f"{total_spent / 100:.2f}",
            f"{total_remaining / 100:.2f}",
            f"{overall_utilization:.2f}%"
        )
        console.print(summary_table)

        if categories_over_budget:
            console.print("\n[bold red]Categories Over Budget:[/bold red] " + ", ".join(categories_over_budget))
            console.print("[bold yellow]Recommendation:[/bold yellow] Review spending in these areas to stay on track.")


    except Exception as e:
        console.print(f"[bold red]An error occurred while viewing budgets: {e}[/bold red]")
