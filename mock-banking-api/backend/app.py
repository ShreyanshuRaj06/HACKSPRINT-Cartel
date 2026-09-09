import sys
import os
from flask import Flask, jsonify

# Add backend directory to path so route and service imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import routes.accounts as accounts
import routes.customers as customers
import routes.loans as loans
import routes.transactions as transactions

app = Flask(__name__)

# Register route blueprints
app.register_blueprint(accounts.blueprint)
app.register_blueprint(customers.blueprint)
app.register_blueprint(loans.blueprint)
app.register_blueprint(transactions.blueprint)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "Retail Banking Mock API - TCS Techsprint",
        "flagship_capability": "Transaction Investigation (investigate_transactions)",
        "session": {
            "mode": "Simulated Active Session",
            "default_customer": "CUST001 (Aarav Sharma)",
            "header_override": "X-Customer-Id"
        },
        "endpoints": {
            "customers": "/api/customers",
            "customer_detail": "/api/customer/<customer_id>",
            "accounts": "/api/accounts",
            "account_balance": "/api/account/<account_id>/balance",
            "loans": "/api/loans",
            "transactions": "/api/transactions",
            "investigate": "/api/transactions/investigate"
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
