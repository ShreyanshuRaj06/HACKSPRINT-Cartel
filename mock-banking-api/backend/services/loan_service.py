import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'loans.json')

def load_loans():
    if not os.path.exists(DATA_FILE):
        return {"loans": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_all_loans():
    """Retrieve all loan records for mock product discovery."""
    data = load_loans()
    return data.get('loans', [])

def get_loans_by_customer_id(customer_id):
    """Retrieve loan accounts belonging to the authenticated customer."""
    data = load_loans()
    return [loan for loan in data.get('loans', []) if loan.get('customer_id') == customer_id]

def get_loan_by_id(loan_id, customer_id=None):
    """Retrieve loan details by loan ID, optionally enforcing customer scope."""
    data = load_loans()
    for loan in data.get('loans', []):
        if loan['id'] == loan_id:
            if customer_id and loan.get('customer_id') != customer_id:
                return None  # Security boundary
            return loan
    return None
