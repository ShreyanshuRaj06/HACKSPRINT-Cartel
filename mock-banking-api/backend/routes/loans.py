from flask import Blueprint, jsonify, request
import services.loan_service as loan_service

blueprint = Blueprint('loans', __name__)

@blueprint.route('/api/loans', methods=['GET'])
def get_loans():
    """Retrieve loans for the active customer, or all loans if requested."""
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id')
    if customer_id:
        loans_list = loan_service.get_loans_by_customer_id(customer_id)
    else:
        loans_list = loan_service.get_all_loans()
    return jsonify(loans_list)

@blueprint.route('/api/loan/<string:loan_id>', methods=['GET'])
def get_loan(loan_id):
    customer_id = request.headers.get('X-Customer-Id') or request.args.get('customer_id')
    loan = loan_service.get_loan_by_id(loan_id, customer_id=customer_id)
    if loan is None:
        return jsonify({'error': 'Loan not found or unauthorized', 'error_code': 'LOAN_NOT_FOUND'}), 404
    return jsonify(loan)
