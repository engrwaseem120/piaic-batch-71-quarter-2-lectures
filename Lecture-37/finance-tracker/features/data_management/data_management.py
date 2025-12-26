import questionary
import csv
import json
import datetime
import shutil
import os
from rich.console import Console


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

def export_to_csv():
    """Exports all transactions to a CSV file."""
    transactions = get_transactions()
    if not transactions:
        console.print("[yellow]No transactions to export.[/yellow]")
        return

    # Create exports directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")
        
    file_path = "exports/transactions.csv"
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "type", "category", "amount", "description", "id"])
            writer.writeheader()
            for t in transactions:
                # Convert date object to string for CSV
                t_copy = t.copy()
                t_copy["date"] = t_copy["date"].strftime("%Y-%m-%d")
                writer.writerow(t_copy)
        console.print(f"[green]Successfully exported transactions to {file_path}[/green]")
    except IOError as e:
        console.print(f"[red]Error exporting to CSV: {e}[/red]")

def export_to_json():
    """Exports all transactions to a JSON file."""
    transactions = get_transactions()
    if not transactions:
        console.print("[yellow]No transactions to export.[/yellow]")
        return

    # Create exports directory if it doesn't exist
    if not os.path.exists("exports"):
        os.makedirs("exports")

    file_path = "exports/transactions.json"
    try:
        # Convert date objects to strings for JSON serialization
        transactions_to_export = []
        for t in transactions:
            t_copy = t.copy()
            t_copy["date"] = t_copy["date"].strftime("%Y-%m-%d")
            transactions_to_export.append(t_copy)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(transactions_to_export, f, indent=4)
        console.print(f"[green]Successfully exported transactions to {file_path}[/green]")
    except IOError as e:
        console.print(f"[red]Error exporting to JSON: {e}[/red]")

def import_from_csv():
    """Imports transactions from a CSV file, avoiding duplicates."""
    file_path = "exports/transactions.csv"
    if not os.path.exists(file_path):
        console.print(f"[red]File not found: {file_path}[/red]")
        console.print("[yellow]Please export your transactions to CSV first.[/yellow]")
        return

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            new_transactions = list(reader)
    except (IOError, csv.Error) as e:
        console.print(f"[red]Error reading CSV file: {e}[/red]")
        return

    if not new_transactions:
        console.print("[yellow]No transactions found in the CSV file.[/yellow]")
        return

    existing_transactions = get_transactions()
    existing_ids = {t["id"] for t in existing_transactions}

    transactions_to_add = []
    skipped_count = 0
    invalid_count = 0

    for t in new_transactions:
        if t.get("id") in existing_ids:
            skipped_count += 1
            continue
        
        # Improved validation
        required_fields = ["date", "type", "category", "amount", "description", "id"]
        if not all(t.get(k) for k in required_fields):
            invalid_count += 1
            continue
        
        try:
            # Validate and format data before appending
            formatted_transaction = (
                f"{datetime.datetime.strptime(t['date'], '%Y-%m-%d').date()},"
                f"{t['type']},"
                f"{t['category']},"
                f"{int(t['amount'])},"
                f"{t['description']},"
                f"{t['id']}"
            )
            transactions_to_add.append(formatted_transaction)
        except (ValueError, TypeError):
            invalid_count += 1
            continue

    if not transactions_to_add:
        console.print("[yellow]No new transactions to import.[/yellow]")
        if skipped_count:
            console.print(f"Skipped {skipped_count} duplicate transaction(s).")
        if invalid_count:
            console.print(f"Skipped {invalid_count} invalid transaction(s).")
        return

    try:
        # Check if file is not empty to decide if a newline is needed
        is_new_file = not os.path.exists("database/transactions.txt") or os.path.getsize("database/transactions.txt") == 0
        
        with open("database/transactions.txt", "a") as f:
            if not is_new_file:
                f.write("\n")
            f.write("\n".join(transactions_to_add))
            
        console.print(f"[green]Successfully imported {len(transactions_to_add)} new transaction(s).[/green]")
        if skipped_count:
            console.print(f"Skipped {skipped_count} duplicate transaction(s).")
        if invalid_count:
            console.print(f"Skipped {invalid_count} invalid transaction(s).")
    except IOError as e:
        console.print(f"[red]Error writing to transactions file: {e}[/red]")

def create_backup():
    """Creates a zip archive of the database directory."""
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_filename = f"backup-{timestamp}"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        shutil.make_archive(backup_path, 'zip', "database")
        console.print(f"[green]Successfully created backup: {backup_path}.zip[/green]")
    except Exception as e:
        console.print(f"[red]Error creating backup: {e}[/red]")

def restore_from_backup():
    """Restores the database from a selected backup file."""
    backup_dir = "backups"
    if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
        console.print("[yellow]No backups found.[/yellow]")
        return

    backups = [f for f in os.listdir(backup_dir) if f.endswith(".zip")]
    if not backups:
        console.print("[yellow]No backup files found.[/yellow]")
        return

    selected_backup = questionary.select(
        "Which backup would you like to restore?",
        choices=backups
    ).ask()

    if not selected_backup:
        console.print("[yellow]Backup restore cancelled.[/yellow]")
        return

    confirm = questionary.confirm(
        "This will overwrite all current data. Are you sure you want to continue?",
        default=False
    ).ask()

    if not confirm:
        console.print("[yellow]Backup restore cancelled.[/yellow]")
        return

    backup_path = os.path.join(backup_dir, selected_backup)
    try:
        # First, remove the existing database directory
        if os.path.exists("database"):
            shutil.rmtree("database")
        
        # Then, extract the backup
        shutil.unpack_archive(backup_path, "database", 'zip')
        console.print(f"[green]Successfully restored data from {selected_backup}[/green]")
    except Exception as e:
        console.print(f"[red]Error restoring from backup: {e}[/red]")

def wipe_data():
    """Wipes all user data (transactions and budgets)."""
    console.print("[bold red]This is a destructive action and will permanently delete all your data.[/bold red]")
    confirmation = questionary.text(
        "To confirm, please type 'DELETE':"
    ).ask()

    if confirmation != "DELETE":
        console.print("[yellow]Data wipe cancelled.[/yellow]")
        return

    try:
        transactions_file = "database/transactions.txt"
        budgets_file = "database/budgets.txt"

        if os.path.exists(transactions_file):
            os.remove(transactions_file)
            console.print("[green]Transactions file deleted.[/green]")
        else:
            console.print("[yellow]Transactions file not found.[/yellow]")

        if os.path.exists(budgets_file):
            os.remove(budgets_file)
            console.print("[green]Budgets file deleted.[/green]")
        else:
            console.print("[yellow]Budgets file not found.[/yellow]")

        console.print("[bold green]All data has been wiped.[/bold green]")

    except Exception as e:
        console.print(f"[red]An error occurred while wiping data: {e}[/red]")


