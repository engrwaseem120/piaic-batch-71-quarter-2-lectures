import streamlit as st
import pandas as pd
from rich.console import Console
from rich.table import Table
import os
import datetime

# Assuming these functions will be adapted or imported from existing features
# Placeholder for data loading functions


# Helper function to load transactions
def _load_transactions():
    transactions_list = []
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                try:
                    date_str, trans_type, category, amount_paisa_str, description = (
                        line.strip().split(",", 4)
                    )
                    transactions_list.append(
                        {
                            "date": date_str,
                            "type": trans_type,
                            "category": category,
                            "amount": int(amount_paisa_str),  # Stored in paisa/cents
                            "description": description,
                        }
                    )
                except ValueError:
                    st.warning(f"Skipping malformed transaction line: {line.strip()}")
    return transactions_list


# Helper function to load budgets
def _load_budgets():
    budgets_dict = {}
    if os.path.exists(BUDGETS_FILE):
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                try:
                    category, amount_paisa_str = line.strip().split(",", 1)
                    budgets_dict[category] = int(
                        amount_paisa_str
                    )  # Stored in paisa/cents
                except ValueError:
                    st.warning(f"Skipping malformed budget line: {line.strip()}")
    return budgets_dict


def load_transactions():
    return _load_transactions()


def load_budgets():
    return _load_budgets()


# --- Data Storage ---
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

# Initialize Rich Console for beautiful output
console = Console()

# --- Data Storage ---

# --- Dashboard Layout ---
st.set_page_config(layout="wide", page_title="Finance Tracker Dashboard")

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .reportview-container .main {
        color: #1a1a1a;
        background-color: #f0f2f6;
    }
    /* Add some shadow to metrics and dataframes to simulate cards */
    .stMetric > div, .stDataFrame { /* Target the inner div of stMetric for shadow */
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        transition: 0.3s;
        border-radius: 5px;
        padding: 1rem;
        background-color: white;
        margin-bottom: 1rem; /* Add some space below cards */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💰 Finance Tracker Dashboard")

# --- Balance Section ---
with st.container():
    st.header("Overall Balance")
    col1, col2, col3 = st.columns(3)


total_income = 0
total_expenses = 0
transactions = load_transactions()  # Load actual transactions here later

for t in transactions:
    if t["type"] == "income":
        total_income += t["amount"]
    else:
        total_expenses += t["amount"]

current_balance = total_income - total_expenses

with col1:
    st.metric(
        label="Total Income",
        value=f"Rs {total_income / 100:,.2f}",
        delta_color="normal",
    )
with col2:
    st.metric(
        label="Total Expenses",
        value=f"Rs {total_expenses / 100:,.2f}",
        delta_color="inverse",
    )
with col3:
    st.metric(
        label="Current Balance",
        value=f"Rs {current_balance / 100:,.2f}",
        delta_color="off",
    )

st.markdown("---")

with st.container():
    st.header("Budget Status")

budgets = load_budgets()  # Load actual budgets here later

# Calculate spent for each category
category_spending = {}
for t in transactions:
    if t["type"] == "expense":
        category = t["category"]
        category_spending[category] = category_spending.get(category, 0) + t["amount"]

for category, budget_amount in budgets.items():
    spent_amount = category_spending.get(category, 0)

    if budget_amount > 0:
        utilization_percentage = (spent_amount / budget_amount) * 100
    else:
        utilization_percentage = 0  # Handle zero budget to avoid division by zero

    st.subheader(f"{category} Budget")

    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
        st.write(f"Budget: Rs {budget_amount / 100:,.2f}")
        st.write(f"Spent: Rs {spent_amount / 100:,.2f}")
        st.write(f"Remaining: Rs {(budget_amount - spent_amount) / 100:,.2f}")
    with col_b2:
        if utilization_percentage < 70:
            st.progress(
                min(utilization_percentage / 100, 1.0)
            )  # Ensure progress bar doesn't exceed 100% internally
            st.markdown(
                f"<p style='color:green;'>{utilization_percentage:.1f}% used</p>",
                unsafe_allow_html=True,
            )
        elif utilization_percentage < 100:
            st.progress(min(utilization_percentage / 100, 1.0))
            st.markdown(
                f"<p style='color:gold;'>{utilization_percentage:.1f}% used</p>",
                unsafe_allow_html=True,
            )
        else:
            st.progress(min(utilization_percentage / 100, 1.0))
            st.markdown(
                f"<p style='color:red;'>{utilization_percentage:.1f}% used (OVER BUDGET!)</p>",
                unsafe_allow_html=True,
            )

st.markdown("---")

with st.container():
    st.header("Recent Transactions")

# Sort transactions by date (newest first)
transactions_df = pd.DataFrame(transactions)
if not transactions_df.empty:
    transactions_df["date"] = pd.to_datetime(transactions_df["date"])
    transactions_df = transactions_df.sort_values(by="date", ascending=False)
    # Convert amount from paisa to rupees for display
    transactions_df["amount"] = transactions_df["amount"] / 100

# Display last 10 transactions
st.dataframe(
    transactions_df.head(10).style.apply(
        lambda x: ["color: red" if x["type"] == "expense" else "color: green"] * len(x),
        axis=1,
    ),
    hide_index=True,
    column_config={
        "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "type": "Type",
        "category": "Category",
        "amount": st.column_config.NumberColumn(
            "Amount (Rs)", format="%.2f", width="small"
        ),
        "description": "Description",
    },
)
