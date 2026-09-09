import re


class QueryRouter:
    """
    Routes banking questions to the correct data source.

    Possible routes:
        knowledge       -> RAG / FAISS
        customer_data   -> CustomerService
        transaction     -> TransactionAnalyzer
        hybrid          -> Customer data + RAG
        unknown         -> clarification
    """

    # -----------------------------------------------------
    # Keywords
    # -----------------------------------------------------

    KNOWLEDGE_KEYWORDS = {
        "loan",
        "interest",
        "rate",
        "eligibility",
        "eligible",
        "fee",
        "fees",
        "charge",
        "charges",
        "policy",
        "kyc",
        "document",
        "documents",
        "faq",
        "card",
        "lost card",
        "stolen card",
        "otp",
        "password",
        "pin",
        "upi",
        "neft",
        "rtgs",
        "imps",
        "account closure",
        "close account",
        "prepayment",
    }

    CUSTOMER_KEYWORDS = {
        "my account",
        "my balance",
        "account balance",
        "my account balance",
        "my profile",
        "my details",
        "my information",
        "my accounts",
        "my transactions",
        "my money",
    }

    TRANSACTION_KEYWORDS = {
        "transaction",
        "transactions",
        "spent",
        "spend",
        "spending",
        "expense",
        "expenses",
        "debit",
        "credit",
        "credited",
        "debited",
        "food",
        "shopping",
        "utilities",
        "entertainment",
        "transport",
        "cash flow",
        "cashflow",
        "monthly",
        "month",
        "last month",
        "this month",
        "biggest expense",
        "largest expense",
    }

    # -----------------------------------------------------
    # Normalization
    # -----------------------------------------------------

    @staticmethod
    def normalize(query):
        """
        Normalize a user query for keyword matching.
        """

        query = query.lower().strip()

        query = re.sub(
            r"\s+",
            " ",
            query
        )

        return query

    # -----------------------------------------------------
    # Score knowledge route
    # -----------------------------------------------------

    def _knowledge_score(self, query):

        score = 0

        for keyword in self.KNOWLEDGE_KEYWORDS:

            if keyword in query:
                score += 1

        return score

    # -----------------------------------------------------
    # Score customer route
    # -----------------------------------------------------

    def _customer_score(self, query):

        score = 0

        for keyword in self.CUSTOMER_KEYWORDS:

            if keyword in query:
                score += 1

        return score

    # -----------------------------------------------------
    # Score transaction route
    # -----------------------------------------------------

    def _transaction_score(self, query):

        score = 0

        for keyword in self.TRANSACTION_KEYWORDS:

            if keyword in query:
                score += 1

        return score

    # -----------------------------------------------------
    # Route
    # -----------------------------------------------------

    def route(self, query):

        normalized = self.normalize(query)

        knowledge_score = (
            self._knowledge_score(normalized)
        )

        customer_score = (
            self._customer_score(normalized)
        )

        transaction_score = (
            self._transaction_score(normalized)
        )

        # ---------------------------------------------
        # Hybrid queries
        # ---------------------------------------------

        if (
            customer_score > 0
            and knowledge_score > 0
        ):
            route = "hybrid"

        elif (
            transaction_score > 0
            and knowledge_score > 0
        ):
            route = "hybrid"

        # ---------------------------------------------
        # Customer-specific queries
        # ---------------------------------------------

        elif customer_score > 0:
            route = "customer_data"

        # ---------------------------------------------
        # Transaction queries
        # ---------------------------------------------

        elif transaction_score > 0:
            route = "transaction"

        # ---------------------------------------------
        # Knowledge queries
        # ---------------------------------------------

        elif knowledge_score > 0:
            route = "knowledge"

        # ---------------------------------------------
        # Unknown
        # ---------------------------------------------

        else:
            route = "unknown"

        return {
            "query": query,
            "normalized_query": normalized,
            "route": route,
            "scores": {
                "knowledge": knowledge_score,
                "customer_data": customer_score,
                "transaction": transaction_score,
            }
        }


# =========================================================
# TESTS
# =========================================================

if __name__ == "__main__":

    router = QueryRouter()

    test_queries = [

        (
            "What is the interest rate for a personal loan?",
            "knowledge"
        ),

        (
            "Am I eligible for a home loan?",
            "knowledge"
        ),

        (
            "What documents are required for KYC?",
            "knowledge"
        ),

        (
            "What is my account balance?",
            "customer_data"
        ),

        (
            "Show me my accounts",
            "customer_data"
        ),

        (
            "How much did I spend on food?",
            "transaction"
        ),

        (
            "What are my biggest expenses?",
            "transaction"
        ),

        (
            "How much did I spend last month?",
            "transaction"
        ),

        (
            "What is my balance and what are the account fees?",
            "hybrid"
        ),

        (
            "Show my transactions and tell me about UPI charges",
            "hybrid"
        ),

        (
            "Hello",
            "unknown"
        ),
    ]

    print("=" * 70)
    print("QUERY ROUTER TESTS")
    print("=" * 70)

    passed = 0

    for number, (query, expected) in enumerate(
        test_queries,
        start=1
    ):

        result = router.route(query)

        actual = result["route"]

        success = actual == expected

        if success:
            passed += 1

        status = "PASS" if success else "FAIL"

        print(
            f"\nTEST {number} — {status}"
        )

        print(
            f"Query: {query}"
        )

        print(
            f"Expected: {expected}"
        )

        print(
            f"Actual:   {actual}"
        )

        print(
            f"Scores:   {result['scores']}"
        )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    accuracy = (
        passed / len(test_queries)
    ) * 100

    print("\n" + "=" * 70)

    print(
        f"ROUTER ACCURACY: "
        f"{passed}/{len(test_queries)} "
        f"({accuracy:.1f}%)"
    )

    if passed == len(test_queries):

        print(
            "QUERY ROUTER: PASS"
        )

    else:

        print(
            "QUERY ROUTER: NEEDS IMPROVEMENT"
        )

    print("=" * 70)