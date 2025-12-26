# Day 6: Data Management

## Goal
Provide users with tools to manage their financial data, including import, export, backup, and restore.

## Learning Focus
- File I/O (CSV, JSON)
- Data serialization
- User confirmation for destructive actions
- Directory and file manipulation

## Fintech Concepts
- **Data Portability**: Allowing users to take their data with them in a common format.
- **Data Backup and Recovery**: Protecting against data loss.
- **Data Integrity**: Ensuring data is consistent and accurate during import/export.

## Features to Build

### 1. Export Data
- **Export to CSV**: Export all transactions to a `transactions.csv` file.
  - Columns: `date`, `type`, `category`, `amount`, `description`, `id`
- **Export to JSON**: Export all transactions to a `transactions.json` file.
  - JSON format should be a list of objects.

### 2. Import Data
- **Import from CSV**: Import transactions from a `transactions.csv` file.
  - Should handle duplicates by checking transaction IDs.
  - Should validate data to ensure it's in the correct format.

### 3. Backup and Restore
- **Create Backup**: Create a zip archive of the `database` directory.
  - The backup file should be named `backup-YYYY-MM-DD-HH-MM-SS.zip`.
- **Restore from Backup**: Restore the `database` directory from a selected backup file.
  - Should prompt the user for confirmation before overwriting existing data.

### 4. Wipe Data
- **Wipe All Data**: Delete all transactions and budgets.
  - Should require a very clear and explicit confirmation from the user (e.g., typing "DELETE" to confirm).

## Success Criteria
✅ Can export transactions to CSV.
✅ Can export transactions to JSON.
✅ Can import transactions from CSV, handling duplicates.
✅ Can create a backup of the data.
✅ Can restore data from a backup.
✅ Can wipe all data with user confirmation.
✅ All features are integrated into the main CLI menu.
