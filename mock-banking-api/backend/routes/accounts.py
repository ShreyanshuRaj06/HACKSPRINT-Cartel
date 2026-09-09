from flask import Blueprint, jsonify, request
import services.account_service as account_service

blueprint = Blueprint('accounts', __name__)

@blueprint.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Retrieve accounts for a customer (default session customer: CUST001)."""
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id', 'CUST001')
    accounts = account_service.get_accounts_by_customer_id(customer_id)
    return jsonify(accounts)

@blueprint.route('/api/account/<string:account_id>/balance', methods=['GET'])
def get_account_balance(account_id):
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id', 'CUST001')
    balance = account_service.get_balance_by_id(account_id, customer_id=customer_id)
    if balance is None:
        return jsonify({'error': 'Account not found or unauthorized', 'error_code': 'ACCOUNT_NOT_FOUND'}), 404
    return jsonify(balance)

@blueprint.route('/api/account/<string:account_id>', methods=['GET'])
def get_account(account_id):
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id', 'CUST001')
    account = account_service.get_account_by_id(account_id, customer_id=customer_id)
    if account is None:
        return jsonify({'error': 'Account not found or unauthorized', 'error_code': 'ACCOUNT_NOT_FOUND'}), 404
    return jsonify(account)
