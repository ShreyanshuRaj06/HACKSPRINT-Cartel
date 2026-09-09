from flask import Blueprint, jsonify, request
import services.transaction_service as transaction_service
import services.investigation_service as investigation_service

blueprint = Blueprint('transactions', __name__)

@blueprint.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    Retrieve raw transactions for authenticated customer with optional filters.
    """
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id', 'CUST001')
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    txn_type = request.args.get('type')

    transactions = transaction_service.get_transactions(
        customer_id=customer_id,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        txn_type=txn_type
    )

    if transactions is None:
        return jsonify({'error': 'Unauthorized account access or account not found', 'error_code': 'UNAUTHORIZED_ACCESS'}), 403

    return jsonify(transactions)

@blueprint.route('/api/transactions/<string:account_id>', methods=['GET'])
def get_account_transactions(account_id):
    """Retrieve transactions for a specific account belonging to the customer."""
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id', 'CUST001')
    transactions = transaction_service.get_transactions(customer_id=customer_id, account_id=account_id)
    if transactions is None:
        return jsonify({'error': 'Unauthorized account access or account not found', 'error_code': 'UNAUTHORIZED_ACCESS'}), 403
    return jsonify(transactions)

@blueprint.route('/api/transactions/investigate', methods=['POST', 'GET'])
def investigate():
    """
    High-level API endpoint for Streamlit & Gemini to execute transaction investigations.
    Supports queries like 'Why did I spend so much?', 'Top expenses', 'Month comparison', etc.
    """
    # Accept params from JSON body (POST) or query string (GET)
    if request.method == 'POST' and request.is_json:
        payload = request.get_json() or {}
    else:
        payload = request.args.to_dict()

    customer_id = request.headers.get('X-Customer-Id') or payload.get('customer_id', 'CUST001')
    account_id = payload.get('account_id')
    time_period = payload.get('time_period')
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')
    comparison_period = payload.get('comparison_period')
    category = payload.get('category')
    analysis_type = payload.get('analysis_type', 'overview')
    top_n = int(payload.get('top_n', 5))

    result = investigation_service.investigate_transactions(
        customer_id=customer_id,
        account_id=account_id,
        time_period=time_period,
        start_date=start_date,
        end_date=end_date,
        comparison_period=comparison_period,
        category=category,
        analysis_type=analysis_type,
        top_n=top_n
    )

    if not result.get("verified", True) and result.get("error_code") == "UNAUTHORIZED_ACCOUNT_ACCESS":
        return jsonify(result), 403
    elif not result.get("verified", True) and result.get("error_code") == "CUSTOMER_NOT_FOUND":
        return jsonify(result), 404

    return jsonify(result)
