from services.transaction_analyzer import TransactionAnalyzer


def run_tests():

    analyzer = TransactionAnalyzer()

    print("=" * 70)
    print("TRANSACTION ANALYZER EDGE-CASE TESTS")
    print("=" * 70)

    # -----------------------------------------------------
    # TEST 1 — Debit filtering
    # -----------------------------------------------------

    debits = analyzer.get_transactions(
        account_id="ACC10001",
        transaction_type="Debit"
    )

    assert all(
        transaction["type"] == "Debit"
        for transaction in debits
    )

    print("TEST 1 — Debit filtering: PASS")

    # -----------------------------------------------------
    # TEST 2 — Credit filtering
    # -----------------------------------------------------

    credits = analyzer.get_transactions(
        account_id="ACC10001",
        transaction_type="Credit"
    )

    assert all(
        transaction["type"] == "Credit"
        for transaction in credits
    )

    print("TEST 2 — Credit filtering: PASS")

    # -----------------------------------------------------
    # TEST 3 — Category filtering
    # -----------------------------------------------------

    food_transactions = analyzer.get_transactions(
        account_id="ACC10001",
        category="Food"
    )

    assert all(
        transaction["category"] == "Food"
        for transaction in food_transactions
    )

    print("TEST 3 — Category filtering: PASS")

    # -----------------------------------------------------
    # TEST 4 — Date filtering
    # -----------------------------------------------------

    september = analyzer.get_transactions(
        account_id="ACC10001",
        start_date="2026-09-01",
        end_date="2026-09-30"
    )

    assert all(
        "2026-09-01"
        <= transaction["date"]
        <= "2026-09-30"
        for transaction in september
    )

    print("TEST 4 — Date filtering: PASS")

    # -----------------------------------------------------
    # TEST 5 — Spending is non-negative
    # -----------------------------------------------------

    spending = analyzer.total_spending(
        account_id="ACC10001"
    )

    assert spending >= 0

    print("TEST 5 — Spending calculation: PASS")

    # -----------------------------------------------------
    # TEST 6 — Category totals
    # -----------------------------------------------------

    category_totals = analyzer.spending_by_category(
        account_id="ACC10001"
    )

    assert isinstance(category_totals, dict)

    assert all(
        amount >= 0
        for amount in category_totals.values()
    )

    print("TEST 6 — Category analysis: PASS")

    # -----------------------------------------------------
    # TEST 7 — Biggest expenses sorted correctly
    # -----------------------------------------------------

    biggest = analyzer.biggest_expenses(
        account_id="ACC10001",
        limit=5
    )

    assert len(biggest) <= 5

    assert all(
        biggest[i]["amount"]
        >= biggest[i + 1]["amount"]
        for i in range(len(biggest) - 1)
    )

    print("TEST 7 — Biggest expenses: PASS")

    # -----------------------------------------------------
    # TEST 8 — Transaction count
    # -----------------------------------------------------

    count = analyzer.transaction_count(
        account_id="ACC10001"
    )

    assert count == len(
        analyzer.get_transactions(
            account_id="ACC10001"
        )
    )

    print("TEST 8 — Transaction count: PASS")

    # -----------------------------------------------------
    # TEST 9 — Monthly comparison
    # -----------------------------------------------------

    comparison = analyzer.compare_months(
        "ACC10001",
        2026,
        8,
        2026,
        9
    )

    required_fields = {
        "first_month",
        "second_month",
        "difference",
        "percentage_change",
        "direction"
    }

    assert required_fields.issubset(
        comparison.keys()
    )

    print("TEST 9 — Monthly comparison: PASS")

    # -----------------------------------------------------
    # TEST 10 — Net cash flow
    # -----------------------------------------------------

    net_flow = analyzer.net_cash_flow(
        account_id="ACC10001"
    )

    expected_net = (
        analyzer.total_credits(
            account_id="ACC10001"
        )
        -
        analyzer.total_spending(
            account_id="ACC10001"
        )
    )

    assert net_flow == round(
        expected_net,
        2
    )

    print("TEST 10 — Net cash flow: PASS")

    # -----------------------------------------------------
    # TEST 11 — Empty account
    # -----------------------------------------------------

    empty_results = analyzer.get_transactions(
        account_id="ACC99999"
    )

    assert empty_results == []

    print("TEST 11 — Empty account: PASS")

    # -----------------------------------------------------
    # TEST 12 — Empty date range
    # -----------------------------------------------------

    empty_period = analyzer.total_spending(
        account_id="ACC10001",
        start_date="2025-01-01",
        end_date="2025-01-31"
    )

    assert empty_period == 0

    print("TEST 12 — Empty period: PASS")

    # -----------------------------------------------------
    # FINAL
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("ALL TRANSACTION ANALYZER TESTS: PASS")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()