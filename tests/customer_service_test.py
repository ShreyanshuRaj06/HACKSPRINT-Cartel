from services.customer_service import CustomerService


def run_tests():

    service = CustomerService()

    print("=" * 70)
    print("CUSTOMER SERVICE TESTS")
    print("=" * 70)

    customer_ids = [
        "CUST1001",
        "CUST1002",
        "CUST1003",
        "CUST1004",
        "CUST1005",
        "CUST1006",
        "CUST1007",
        "CUST1008",
    ]

    # -----------------------------------------------------
    # TEST 1 — Every customer exists
    # -----------------------------------------------------

    for customer_id in customer_ids:

        profile = service.get_customer_profile(
            customer_id
        )

        assert profile is not None
        assert profile["customer_id"] == customer_id

    print("TEST 1 — Customer profiles: PASS")

    # -----------------------------------------------------
    # TEST 2 — Every customer has accounts
    # -----------------------------------------------------

    for customer_id in customer_ids:

        accounts = service.get_accounts(
            customer_id
        )

        assert len(accounts) > 0

        for account in accounts:
            assert account["customer_id"] == customer_id

    print("TEST 2 — Account ownership: PASS")

    # -----------------------------------------------------
    # TEST 3 — Transaction isolation
    # -----------------------------------------------------

    for customer_id in customer_ids:

        accounts = service.get_accounts(
            customer_id
        )

        allowed_accounts = {
            account["account_id"]
            for account in accounts
        }

        transactions = service.get_transactions(
            customer_id
        )

        for transaction in transactions:

            assert (
                transaction["account_id"]
                in allowed_accounts
            )

    print("TEST 3 — Transaction isolation: PASS")

    # -----------------------------------------------------
    # TEST 4 — Unknown customer
    # -----------------------------------------------------

    assert (
        service.get_customer_profile(
            "CUST9999"
        )
        is None
    )

    print("TEST 4 — Unknown customer: PASS")

    # -----------------------------------------------------
    # TEST 5 — Unknown customer has no transactions
    # -----------------------------------------------------

    assert (
        service.get_transactions(
            "CUST9999"
        )
        == []
    )

    print("TEST 5 — Unknown customer transactions: PASS")

    # -----------------------------------------------------
    # TEST 6 — Balance consistency
    # -----------------------------------------------------

    for customer_id in customer_ids:

        accounts = service.get_accounts(
            customer_id
        )

        balance = service.get_balance(
            customer_id
        )

        expected = round(
            sum(
                float(account["balance"])
                for account in accounts
            ),
            2
        )

        assert (
            balance["total_balance"]
            == expected
        )

    print("TEST 6 — Balance consistency: PASS")

    # -----------------------------------------------------
    # TEST 7 — Customer summary
    # -----------------------------------------------------

    for customer_id in customer_ids:

        summary = service.get_customer_summary(
            customer_id
        )

        assert summary is not None
        assert "customer" in summary
        assert "accounts" in summary
        assert "balance" in summary
        assert "transaction_count" in summary

    print("TEST 7 — Customer summary: PASS")

    # -----------------------------------------------------
    # TEST 8 — Customer transaction count
    # -----------------------------------------------------

    for customer_id in customer_ids:

        transactions = service.get_transactions(
            customer_id
        )

        count = service.get_transaction_count(
            customer_id
        )

        assert count == len(transactions)

    print("TEST 8 — Transaction counts: PASS")

    # -----------------------------------------------------
    # Final
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("ALL CUSTOMER SERVICE TESTS: PASS")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()