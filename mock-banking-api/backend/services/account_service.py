import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'accounts.json')

def load_accounts():
    if not os.path.exists(DATA_FILE):
        return {"accounts": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_accounts_by_customer_id(customer_id):
    """Retrieve all accounts belonging to a specific customer."""
    data = load_accounts()
    return [acc for acc in data.get('accounts', []) if acc['customer_id'] == customer_id]

def get_account_by_id(account_id, customer_id=None):
    """
    Retrieve account details by account_id.
    If customer_id is provided, verifies that the account belongs to that customer.
    """
    data = load_accounts()
    for acc in data.get('accounts', []):
        if acc['id'] == account_id:
            if customer_id and acc['customer_id'] != customer_id:
                return None  # Security boundary: Customer doesn't own this account
            return acc
    return None

def get_balance_by_id(account_id, customer_id=None):
    """Retrieve balance details for an account within the customer's scope."""
    account = get_account_by_id(account_id, customer_id=customer_id)
    if not account:
        return None
    return {
        "account_id": account['id'],
        "customer_id": account['customer_id'],
        "account_type": account.get('account_type', 'Savings'),
        "balance": account['balance'],
        "currency": account.get('currency', 'INR')
    }

def validate_customer_account(customer_id, account_id):
    """Check whether an account belongs to the customer."""
    account = get_account_by_id(account_id, customer_id=customer_id)
    return account is not None
