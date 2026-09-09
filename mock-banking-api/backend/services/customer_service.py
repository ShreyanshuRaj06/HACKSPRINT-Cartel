import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'customers.json')

def load_customers():
    if not os.path.exists(DATA_FILE):
        return {"customers": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_customer_by_id(customer_id):
    """Retrieve customer details by customer_id."""
    data = load_customers()
    for customer in data.get('customers', []):
        if customer['id'] == customer_id:
            return customer
    return None

def get_all_customers():
    """Retrieve list of all customers (for mock/demo UI selection)."""
    data = load_customers()
    return data.get('customers', [])
