from flask import Blueprint, jsonify, request
import services.customer_service as customer_service

blueprint = Blueprint('customers', __name__)

@blueprint.route('/api/customers', methods=['GET'])
def get_all_customers():
    """List all customers (useful for Streamlit UI customer switcher)."""
    customers = customer_service.get_all_customers()
    return jsonify(customers)

@blueprint.route('/api/customer/<string:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get details of a specific customer."""
    customer = customer_service.get_customer_by_id(customer_id)
    if customer is None:
        return jsonify({'error': 'Customer not found', 'error_code': 'CUSTOMER_NOT_FOUND'}), 404
    return jsonify(customer)
