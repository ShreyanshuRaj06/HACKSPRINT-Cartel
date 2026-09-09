import json
import os
from datetime import datetime
from services.account_service import get_accounts_by_customer_id, validate_customer_account

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'transactions.json')

def load_transactions():
    if not os.path.exists(DATA_FILE):
        return {"transactions": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_transactions(customer_id, account_id=None, start_date=None, end_date=None, category=None, txn_type=None):
    """
    Retrieve and filter transactions strictly scoped to the authenticated customer.
    
    Parameters:
    - customer_id (str): Authenticated customer identifier (Source of Truth).
    - account_id (str, optional): Specific account ID. Must belong to customer_id.
    - start_date (str, optional): Start date in 'YYYY-MM-DD' format.
    - end_date (str, optional): End date in 'YYYY-MM-DD' format.
    - category (str, optional): Case-insensitive category filter.
    - txn_type (str, optional): 'debit' or 'credit'.
    
    Returns:
    - list[dict]: List of matching transaction objects.
    - None: If account_id does not belong to customer_id.
    """
    # 1. Determine allowed accounts for customer
    customer_accounts = get_accounts_by_customer_id(customer_id)
    allowed_account_ids = {acc['id'] for acc in customer_accounts}

    if not allowed_account_ids:
        return []

    # 2. Enforce account scope if specific account is requested
    if account_id:
        if account_id not in allowed_account_ids:
            return None  # Security boundary: Cross-customer access rejected
        target_account_ids = {account_id}
    else:
        target_account_ids = allowed_account_ids

    # 3. Load all raw transaction records
    data = load_transactions()
    all_txns = data.get('transactions', [])

    # 4. Filter strictly by customer's accounts
    scoped_txns = [t for t in all_txns if t.get('account_id') in target_account_ids]

    # 5. Apply date range filters if provided
    filtered_txns = []
    for txn in scoped_txns:
        txn_date_str = txn.get('date')
        if not txn_date_str:
            continue

        if start_date and txn_date_str < start_date:
            continue
        if end_date and txn_date_str > end_date:
            continue
        if category and txn.get('category', '').lower() != category.lower():
            continue
        if txn_type and txn.get('type', '').lower() != txn_type.lower():
            continue

        filtered_txns.append(txn)

    # Sort chronological by date descending
    filtered_txns.sort(key=lambda x: x.get('date', ''), reverse=True)
    return filtered_txns
