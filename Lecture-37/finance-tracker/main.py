import questionary
from rich.console import Console
from features.transactions import transactions
from features.budgets import budgets
from features.analytics import analytics  # Import the analytics module
from features.smart_assistant import assistant
from features.data_management import data_management

# Initialize Rich Console
console = Console()


def main():
    """
    Main function to run the Personal Finance Tracker CLI.
    """
    console.print("[bold cyan]Welcome to your Personal Finance Tracker![/bold cyan]")

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "Show Balance",
                "Set Budget",
                "View Budgets",
                "🤖 Show Smart Recommendations",
                "Generate Financial Report",  # New menu option
                "Export to CSV",
                "Export to JSON",
                "Import from CSV",
                "Create Backup",
                "Restore from Backup",
                "Wipe Data",
                "View Web Dashboard",  # New menu option
                "Exit",
            ],
        ).ask()

        if choice == "Add Expense":
            transactions.add_transaction("expense")
        elif choice == "Add Income":
            transactions.add_transaction("income")
        elif choice == "List Transactions":
            transactions.list_transactions()
        elif choice == "Show Balance":
            transactions.show_balance()
        elif choice == "Set Budget":
            budgets.set_budget()
        elif choice == "View Budgets":
            budgets.view_budgets()
        elif choice == "🤖 Show Smart Recommendations":
            assistant.show_recommendations()
        elif choice == "Generate Financial Report":  # Handle the new option
            analytics.generate_comprehensive_report()
        elif choice == "Export to CSV":
            data_management.export_to_csv()
        elif choice == "Export to JSON":
            data_management.export_to_json()
        elif choice == "Import from CSV":
            data_management.import_from_csv()
        elif choice == "Create Backup":
            data_management.create_backup()
        elif choice == "Restore from Backup":
            data_management.restore_from_backup()
        elif choice == "Wipe Data":
            data_management.wipe_data()
        elif choice == "View Web Dashboard":
            import subprocess
            import sys

            console.print("[bold green]Starting Streamlit dashboard...[/bold green]")
            console.print(
                "[bold green]Access it at http://localhost:8501 (or as shown in the new window).[/bold green]"
            )
            console.print("[bold green]You can continue using the CLI.[/bold green]")

            # Use a platform-independent way to start the process in the background
            if sys.platform == "win32":
                subprocess.Popen(
                    ["streamlit", "run", "features/website/dashboard.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                subprocess.Popen(
                    ["streamlit", "run", "features/website/dashboard.py"],
                    start_new_session=True,
                )
        elif choice == "Exit" or choice is None:
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break


if __name__ == "__main__":
    main()
