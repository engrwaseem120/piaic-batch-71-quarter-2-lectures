import questionary
from datetime import datetime
from rich.console import Console
from rich.table import Table

# Initialize Rich Console for beautiful output
console = Console()

# --- Data Storage ---
TRANSACTIONS_FILE = "database/transactions.txt"

def add_transaction(transaction_type):
    """
    Adds a new expense or income transaction.
    """
    try:
        amount_str = questionary.text(f"Enter the amount for the {transaction_type}:").ask()
        amount = int(float(amount_str) * 100)  # Store as cents
        if amount <= 0:
            console.print("[bold red]Invalid amount. Please enter a positive number.[/bold red]")
            return

        if transaction_type == "expense":
            category = questionary.select(
                "Select an expense category:",
                choices=['Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Other']
            ).ask()
        else:
            category = questionary.select(
                "Select an income source:",
                choices=['Salary', 'Freelance', 'Business', 'Investment', 'Gift', 'Other']
            ).ask()

        description = questionary.text("Enter a description:").ask()
        date_str = questionary.text("Enter the date (YYYY-MM-DD), or leave empty for today:").ask()

        if not date_str:
            date = datetime.now().strftime("%Y-%m-%d")
        else:
            # Validate date format
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                date = date_str
            except ValueError:
                console.print("[bold red]Invalid date format. Please use YYYY-MM-DD.[/bold red]")
                return

        # Save the transaction
        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(f"{date},{transaction_type},{category},{amount},{description}\n")

        console.print(f"[bold green]Successfully added {transaction_type}![/bold green]")

    except (ValueError, TypeError):
        console.print("[bold red]Invalid amount. Please enter a valid number.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def list_transactions():
    """
    Lists all transactions in a table.
    """
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            transactions = f.readlines()

        if not transactions:
            console.print("[bold yellow]No transactions found.[/bold yellow]")
            return

        table = Table(title="All Transactions")
        table.add_column("Date", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Category", style="yellow")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Description", style="white")

        # Sort by date, newest first
        transactions.sort(key=lambda t: datetime.strptime(t.split(',')[0], "%Y-%m-%d"), reverse=True)

        for transaction in transactions:
            date, trans_type, category, amount, description = transaction.strip().split(',', 4)
            amount_display = f"{int(amount) / 100:.2f}"
            
            style = "red" if trans_type == "expense" else "green"
            table.add_row(date, trans_type, category, f"[{style}]{amount_display}[/{style}]", description)

        console.print(table)

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def show_balance():
    """
    Calculates and displays the balance for the current month.
    """
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            transactions = f.readlines()

        if not transactions:
            console.print("[bold yellow]No transactions found.[/bold yellow]")
            return

        total_income = 0
        total_expenses = 0
        current_month = datetime.now().strftime("%Y-%m")

        for transaction in transactions:
            date, trans_type, _, amount, _ = transaction.strip().split(',', 4)
            if date.startswith(current_month):
                if trans_type == "income":
                    total_income += int(amount)
                else:
                    total_expenses += int(amount)

        balance = total_income - total_expenses

        total_income_display = f"{total_income / 100:.2f}"
        total_expenses_display = f"{total_expenses / 100:.2f}"
        balance_display = f"{balance / 100:.2f}"

        balance_style = "green" if balance >= 0 else "red"

        panel = Table(title="[bold blue]Current Month Balance[/bold blue]", expand=True)
        panel.add_column("Total Income", style="green", justify="right")
        panel.add_column("Total Expenses", style="red", justify="right")
        panel.add_column("Balance", style=balance_style, justify="right")
        panel.add_row(total_income_display, total_expenses_display, balance_display)
        
        console.print(panel)

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
