import os
from datetime import datetime, timedelta
from services.transaction_service import get_transactions
from services.transaction_analyzer import TransactionAnalyzer
from services.customer_service import get_customer_by_id

def parse_relative_period(period_name, reference_date=None):
    """
    Helper to resolve common relative period names.
    If custom dates (YYYY-MM-DD) are passed, they pass through directly.
    """
    if not reference_date:
        reference_date = datetime.now()

    p = (period_name or '').lower().strip()
    if not p:
        return None, None

    # Current month
    if p in ['this_month', 'current_month']:
        start = reference_date.replace(day=1)
        next_month = (start + timedelta(days=32)).replace(day=1)
        end = next_month - timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # Previous month
    elif p in ['last_month', 'previous_month']:
        first_of_this_month = reference_date.replace(day=1)
        end = first_of_this_month - timedelta(days=1)
        start = end.replace(day=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # Past 7 / 30 days
    elif p in ['last_7_days', 'past_week']:
        start = reference_date - timedelta(days=7)
        return start.strftime("%Y-%m-%d"), reference_date.strftime("%Y-%m-%d")
    elif p in ['last_30_days', 'past_month']:
        start = reference_date - timedelta(days=30)
        return start.strftime("%Y-%m-%d"), reference_date.strftime("%Y-%m-%d")

    return None, None

def investigate_transactions(
    customer_id,
    account_id=None,
    time_period=None,
    start_date=None,
    end_date=None,
    comparison_period=None,
    category=None,
    analysis_type="overview",
    top_n=5
):
    """
    Authoritative transaction investigation capability.
    Coordinates: Customer scoping -> Transaction retrieval -> Deterministic math.
    Resilient to empty datasets, custom date ranges, and custom categories.
    """
    # 1. Customer scope validation
    customer = get_customer_by_id(customer_id)
    if not customer:
        return {
            "verified": False,
            "error": f"Customer '{customer_id}' not found.",
            "error_code": "CUSTOMER_NOT_FOUND"
        }

    # 2. Resolve target date range if relative string is provided
    if time_period:
        p_start, p_end = parse_relative_period(time_period)
        start_date = start_date or p_start
        end_date = end_date or p_end

    # 3. Retrieve target transactions
    current_txns = get_transactions(
        customer_id=customer_id,
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        category=category
    )

    if current_txns is None:
        return {
            "verified": False,
            "error": f"Unauthorized account access or account '{account_id}' not found for customer '{customer_id}'.",
            "error_code": "UNAUTHORIZED_ACCOUNT_ACCESS"
        }

    # 4. Handle comparison period if requested
    comparison_txns = None
    cmp_start, cmp_end = None, None

    if comparison_period or analysis_type == "comparison":
        if comparison_period:
            cmp_start, cmp_end = parse_relative_period(comparison_period)

        comparison_txns = get_transactions(
            customer_id=customer_id,
            account_id=account_id,
            start_date=cmp_start,
            end_date=cmp_end,
            category=category
        )

    # 5. Run deterministic calculations in TransactionAnalyzer
    analysis_result = TransactionAnalyzer.analyze(
        transactions=current_txns,
        comparison_transactions=comparison_txns,
        category=category,
        top_n=top_n
    )

    # 6. Attach metadata
    return {
        "status": "success",
        "verified": True,
        "investigation_meta": {
            "customer_id": customer_id,
            "customer_name": customer.get('name', 'Unknown'),
            "account_id": account_id or "ALL_ACCOUNTS",
            "analysis_type": analysis_type,
            "target_period": {
                "start_date": start_date or "ALL_TIME",
                "end_date": end_date or "ALL_TIME",
                "period_label": time_period or f"{start_date or 'Start'} to {end_date or 'End'}"
            },
            "comparison_period": {
                "start_date": cmp_start or "ALL_TIME",
                "end_date": cmp_end or "ALL_TIME",
                "period_label": comparison_period or "Comparison Period"
            } if comparison_txns is not None else None
        },
        "data": analysis_result
    }
