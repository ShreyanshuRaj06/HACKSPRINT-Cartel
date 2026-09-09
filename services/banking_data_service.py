from services.customer_service import CustomerService
from services.transaction_analyzer import TransactionAnalyzer


class BankingDataService:
    """
    Unified banking data interface.

    Combines:
        CustomerService
        TransactionAnalyzer

    This is the main data-access layer that the
    chatbot/backend can call.
    """

    def __init__(self):

        self.customer_service = CustomerService()
        self.transaction_analyzer = TransactionAnalyzer()

    # =====================================================
    # CUSTOMER CONTEXT
    # =====================================================

    def get_customer_context(self, customer_id):
        """
        Return the complete customer context required
        by the AI assistant.
        """

        summary = self.customer_service.get_customer_summary(
            customer_id
        )

        if summary is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "Customer not found"
            }

        return {
            "success": True,
            "customer_id": customer_id,
            "customer": summary["customer"],
            "accounts": summary["accounts"],
            "balance": summary["balance"],
            "transaction_count": summary["transaction_count"]
        }

    # =====================================================
    # BALANCE
    # =====================================================

    def get_balance(self, customer_id):

        profile = self.customer_service.get_customer_profile(
            customer_id
        )

        if profile is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "Customer not found"
            }

        return {
            "success": True,
            **self.customer_service.get_balance(
                customer_id
            )
        }

    # =====================================================
    # TRANSACTIONS
    # =====================================================

    def get_transactions(
        self,
        customer_id,
        transaction_type=None,
        category=None,
        start_date=None,
        end_date=None
    ):
        """
        Return customer-scoped transactions with
        optional filters.
        """

        transactions = (
            self.customer_service.get_transactions(
                customer_id
            )
        )

        # Unknown customer
        if (
            self.customer_service.get_customer_profile(
                customer_id
            )
            is None
        ):
            return {
                "success": False,
                "customer_id": customer_id,
                "transactions": [],
                "count": 0,
                "error": "Customer not found"
            }

        # -------------------------------------------------
        # Transaction type
        # -------------------------------------------------

        if transaction_type:

            transaction_type = (
                transaction_type.lower()
            )

            transactions = [
                transaction
                for transaction in transactions
                if transaction["type"].lower()
                == transaction_type
            ]

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        if category:

            category = category.lower()

            transactions = [
                transaction
                for transaction in transactions
                if transaction["category"].lower()
                == category
            ]

        # -------------------------------------------------
        # Start date
        # -------------------------------------------------

        if start_date:

            transactions = [
                transaction
                for transaction in transactions
                if transaction["date"] >= start_date
            ]

        # -------------------------------------------------
        # End date
        # -------------------------------------------------

        if end_date:

            transactions = [
                transaction
                for transaction in transactions
                if transaction["date"] <= end_date
            ]

        return {
            "success": True,
            "customer_id": customer_id,
            "count": len(transactions),
            "transactions": transactions
        }

    # =====================================================
    # SPENDING SUMMARY
    # =====================================================

    def get_spending_summary(self, customer_id):

        profile = self.customer_service.get_customer_profile(
            customer_id
        )

        if profile is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "Customer not found"
            }

        total_spending = (
            self.transaction_analyzer.total_spending(
                account_id=self._primary_account(
                    customer_id
                )
            )
        )

        category_spending = (
            self.transaction_analyzer.spending_by_category(
                account_id=self._primary_account(
                    customer_id
                )
            )
        )

        biggest_expenses = (
            self.transaction_analyzer.biggest_expenses(
                account_id=self._primary_account(
                    customer_id
                ),
                limit=5
            )
        )

        transaction_count = (
            self.customer_service.get_transaction_count(
                customer_id
            )
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "total_spending": round(
                total_spending,
                2
            ),
            "spending_by_category": category_spending,
            "biggest_expenses": biggest_expenses,
            "transaction_count": transaction_count
        }

    # =====================================================
    # MONTHLY COMPARISON
    # =====================================================

    def get_monthly_comparison(
        self,
        customer_id,
        first_year,
        first_month,
        second_year,
        second_month
    ):
        """
        Compare spending between two months.

        Uses the customer's primary account.
        """

        profile = self.customer_service.get_customer_profile(
            customer_id
        )

        if profile is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "Customer not found"
            }

        account_id = self._primary_account(
            customer_id
        )

        if account_id is None:

            return {
                "success": False,
                "customer_id": customer_id,
                "error": "No account found"
            }

        comparison = (
            self.transaction_analyzer.compare_months(
                account_id,
                first_year,
                first_month,
                second_year,
                second_month
            )
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "account_id": account_id,
            **comparison
        }

    # =====================================================
    # NET CASH FLOW
    # =====================================================

    def get_net_cash_flow(self, customer_id):

        profile = self.customer_service.get_customer_profile(
            customer_id
        )

        if profile is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "Customer not found"
            }

        account_id = self._primary_account(
            customer_id
        )

        if account_id is None:
            return {
                "success": False,
                "customer_id": customer_id,
                "error": "No account found"
            }

        net_flow = (
            self.transaction_analyzer.net_cash_flow(
                account_id
            )
        )

        return {
            "success": True,
            "customer_id": customer_id,
            "account_id": account_id,
            "net_cash_flow": round(
                net_flow,
                2
            )
        }

    # =====================================================
    # PRIMARY ACCOUNT
    # =====================================================

    def _primary_account(self, customer_id):

        accounts = self.customer_service.get_accounts(
            customer_id
        )

        if not accounts:
            return None

        # Prefer active account.
        active_accounts = [
            account
            for account in accounts
            if account.get("status", "").lower()
            == "active"
        ]

        if active_accounts:
            return active_accounts[0]["account_id"]

        return accounts[0]["account_id"]


# =========================================================
# INTEGRATION TEST
# =========================================================

if __name__ == "__main__":

    service = BankingDataService()

    customer_id = "CUST1001"

    print("=" * 70)
    print("BANKING DATA SERVICE")
    print("=" * 70)

    # -----------------------------------------------------
    # Customer context
    # -----------------------------------------------------

    context = service.get_customer_context(
        customer_id
    )

    print("\nCUSTOMER CONTEXT")
    print("-" * 70)

    print(
        f"Customer: "
        f"{context['customer']['name']}"
    )

    print(
        f"Customer ID: "
        f"{context['customer_id']}"
    )

    print(
        f"Accounts: "
        f"{len(context['accounts'])}"
    )

    print(
        f"Total balance: "
        f"₹{context['balance']['total_balance']:,.2f}"
    )

    print(
        f"Transactions: "
        f"{context['transaction_count']}"
    )

    # -----------------------------------------------------
    # Spending
    # -----------------------------------------------------

    spending = service.get_spending_summary(
        customer_id
    )

    print("\nSPENDING SUMMARY")
    print("-" * 70)

    print(
        f"Total spending: "
        f"₹{spending['total_spending']:,.2f}"
    )

    print(
        f"Transaction count: "
        f"{spending['transaction_count']}"
    )

    print("\nSpending by category:")

    for category, amount in (
        spending["spending_by_category"].items()
    ):

        print(
            f"  {category}: "
            f"₹{amount:,.2f}"
        )

    # -----------------------------------------------------
    # Net cash flow
    # -----------------------------------------------------

    cash_flow = service.get_net_cash_flow(
        customer_id
    )

    print("\nNET CASH FLOW")
    print("-" * 70)

    print(
        f"₹{cash_flow['net_cash_flow']:,.2f}"
    )

    # -----------------------------------------------------
    # Monthly comparison
    # -----------------------------------------------------

    comparison = service.get_monthly_comparison(
        customer_id,
        2026,
        8,
        2026,
        9
    )

    print("\nMONTHLY COMPARISON")
    print("-" * 70)

    print(
        f"August spending: "
        f"₹{comparison['first_month']['spending']:,.2f}"
    )

    print(
        f"September spending: "
        f"₹{comparison['second_month']['spending']:,.2f}"
    )

    print(
        f"Difference: "
        f"₹{comparison['difference']:,.2f}"
    )

    print(
        f"Change: "
        f"{comparison['percentage_change']:.2f}%"
    )

    print(
        f"Direction: "
        f"{comparison['direction']}"
    )

    # -----------------------------------------------------
    # Transaction filtering
    # -----------------------------------------------------

    food = service.get_transactions(
        customer_id,
        category="Food"
    )

    print("\nFOOD TRANSACTIONS")
    print("-" * 70)

    print(
        f"Found: {food['count']}"
    )

    for transaction in food["transactions"][:3]:

        print(
            f"  {transaction['transaction_id']} | "
            f"₹{transaction['amount']:,.2f} | "
            f"{transaction['date']}"
        )

    # -----------------------------------------------------
    # Unknown customer
    # -----------------------------------------------------

    unknown = service.get_customer_context(
        "CUST9999"
    )

    assert unknown["success"] is False

    print("\nUnknown customer protection: PASS")

    # -----------------------------------------------------
    # Final
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("BANKING DATA SERVICE: PASS")
    print("=" * 70)