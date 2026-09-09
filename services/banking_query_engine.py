from services.banking_data_service import BankingDataService
from services.query_router import QueryRouter
from rag.retriever import search_knowledge


class BankingQueryEngine:
    """
    Unified execution layer for the banking assistant.

    Routes a user query to:

        knowledge       -> RAG / FAISS
        customer_data   -> CustomerService
        transaction     -> TransactionAnalyzer
        hybrid          -> Customer data + RAG
        unknown         -> clarification

    Main interface:

        engine.ask(query, customer_id)
    """

    def __init__(self):
        self.router = QueryRouter()
        self.banking_data = BankingDataService()

    # =====================================================
    # PUBLIC API
    # =====================================================

    def ask(self, query, customer_id=None):
        """
        Process a banking query.

        Returns a consistent response structure.
        """

        if not isinstance(query, str) or not query.strip():
            return {
                "success": False,
                "query": query,
                "route": "unknown",
                "customer_id": customer_id,
                "message": "Please provide a banking question.",
                "results": [],
                "sources": []
            }

        route_info = self.router.route(query)
        route = route_info["route"]

        # -------------------------------------------------
        # Unknown
        # -------------------------------------------------

        if route == "unknown":
            return {
                "success": False,
                "query": query,
                "route": "unknown",
                "customer_id": customer_id,
                "message": (
                    "I could not determine what banking "
                    "information you need."
                ),
                "results": [],
                "sources": []
            }

        # -------------------------------------------------
        # Knowledge / RAG
        # -------------------------------------------------

        if route == "knowledge":
            return self._knowledge_query(
                query,
                customer_id
            )

        # -------------------------------------------------
        # Customer data
        # -------------------------------------------------

        if route == "customer_data":
            return self._customer_query(
                query,
                customer_id
            )

        # -------------------------------------------------
        # Transaction
        # -------------------------------------------------

        if route == "transaction":
            return self._transaction_query(
                query,
                customer_id
            )

        # -------------------------------------------------
        # Hybrid
        # -------------------------------------------------

        if route == "hybrid":
            return self._hybrid_query(
                query,
                customer_id
            )

        return {
            "success": False,
            "query": query,
            "route": route,
            "customer_id": customer_id,
            "message": "Unsupported query route.",
            "results": [],
            "sources": []
        }

    # =====================================================
    # KNOWLEDGE / RAG
    # =====================================================

    def _knowledge_query(self, query, customer_id):

        try:
            raw_results = search_knowledge(
                query,
                top_k=5
            )
        except Exception as error:
            return {
                "success": False,
                "query": query,
                "route": "knowledge",
                "customer_id": customer_id,
                "message": f"Knowledge retrieval failed: {error}",
                "results": [],
                "sources": []
            }

        results = self._normalize_rag_results(
            raw_results
        )

        sources = self._extract_sources(
            results
        )

        return {
            "success": True,
            "query": query,
            "route": "knowledge",
            "customer_id": customer_id,
            "results": results,
            "sources": sources,
            "message": (
                "Relevant banking knowledge "
                "retrieved successfully."
            )
        }

    # =====================================================
    # CUSTOMER DATA
    # =====================================================

    def _customer_query(self, query, customer_id):

        if not customer_id:
            return {
                "success": False,
                "query": query,
                "route": "customer_data",
                "customer_id": None,
                "message": (
                    "A customer ID is required for "
                    "personal banking information."
                ),
                "results": [],
                "sources": []
            }

        context = (
            self.banking_data.get_customer_context(
                customer_id
            )
        )

        if not context["success"]:
            return {
                "success": False,
                "query": query,
                "route": "customer_data",
                "customer_id": customer_id,
                "message": context["error"],
                "results": [],
                "sources": []
            }

        return {
            "success": True,
            "query": query,
            "route": "customer_data",
            "customer_id": customer_id,
            "results": context,
            "sources": [
                "customers.json",
                "accounts.json",
                "transactions.json"
            ],
            "message": (
                "Customer information retrieved "
                "successfully."
            )
        }

    # =====================================================
    # TRANSACTION DATA
    # =====================================================

    def _transaction_query(self, query, customer_id):

        if not customer_id:
            return {
                "success": False,
                "query": query,
                "route": "transaction",
                "customer_id": None,
                "message": (
                    "A customer ID is required for "
                    "personal transaction information."
                ),
                "results": [],
                "sources": []
            }

        query_lower = query.lower()

        category = self._detect_category(
            query_lower
        )

        # -------------------------------------------------
        # Customer transactions
        # -------------------------------------------------

        transaction_result = (
            self.banking_data.get_transactions(
                customer_id=customer_id,
                category=category
            )
        )

        if not transaction_result["success"]:
            return {
                "success": False,
                "query": query,
                "route": "transaction",
                "customer_id": customer_id,
                "message": transaction_result["error"],
                "results": [],
                "sources": []
            }

        # -------------------------------------------------
        # Spending summary
        # -------------------------------------------------

        spending = (
            self.banking_data.get_spending_summary(
                customer_id
            )
        )

        # -------------------------------------------------
        # Cash flow
        # -------------------------------------------------

        cash_flow = (
            self.banking_data.get_net_cash_flow(
                customer_id
            )
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        results = {
            "transactions": transaction_result[
                "transactions"
            ],
            "count": transaction_result[
                "count"
            ],
            "spending_summary": spending,
            "net_cash_flow": cash_flow
        }

        return {
            "success": True,
            "query": query,
            "route": "transaction",
            "customer_id": customer_id,
            "results": results,
            "sources": [
                "transactions.json",
                "accounts.json"
            ],
            "message": (
                "Transaction information analyzed "
                "successfully."
            )
        }

    # =====================================================
    # HYBRID
    # =====================================================

    def _hybrid_query(self, query, customer_id):

        customer_result = None

        # -------------------------------------------------
        # Customer information
        # -------------------------------------------------

        if customer_id:

            customer_result = (
                self.banking_data.get_customer_context(
                    customer_id
                )
            )

        # -------------------------------------------------
        # RAG knowledge
        # -------------------------------------------------

        try:
            raw_knowledge = search_knowledge(
                query,
                top_k=5
            )

            knowledge_results = (
                self._normalize_rag_results(
                    raw_knowledge
                )
            )

        except Exception as error:

            return {
                "success": False,
                "query": query,
                "route": "hybrid",
                "customer_id": customer_id,
                "message": (
                    f"Knowledge retrieval failed: {error}"
                ),
                "results": [],
                "sources": []
            }

        # -------------------------------------------------
        # Sources
        # -------------------------------------------------

        sources = self._extract_sources(
            knowledge_results
        )

        if customer_result and customer_result.get(
            "success"
        ):

            sources.extend([
                "customers.json",
                "accounts.json",
                "transactions.json"
            ])

        sources = list(
            dict.fromkeys(sources)
        )

        return {
            "success": True,
            "query": query,
            "route": "hybrid",
            "customer_id": customer_id,
            "results": {
                "customer_data": customer_result,
                "knowledge": knowledge_results
            },
            "sources": sources,
            "message": (
                "Customer information and banking "
                "knowledge retrieved successfully."
            )
        }

    # =====================================================
    # CATEGORY DETECTION
    # =====================================================

    @staticmethod
    def _detect_category(query):

        categories = [
            "food",
            "shopping",
            "utilities",
            "entertainment",
            "transport",
            "business"
        ]

        for category in categories:

            if category in query:
                return category

        return None

    # =====================================================
    # RAG RESULT NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_rag_results(results):
        """
        Make RAG output consistent.

        The current retriever may return dictionaries
        or strings depending on its implementation.

        Dictionary example:

            {
                "source": "faq.json",
                "category": "Cards",
                "record_id": "FAQ003",
                "text": "...",
                "score": 0.76
            }

        String example:

            "Some retrieved banking document..."
        """

        if results is None:
            return []

        normalized = []

        for result in results:

            # ---------------------------------------------
            # Structured result
            # ---------------------------------------------

            if isinstance(result, dict):

                normalized.append(
                    result.copy()
                )

            # ---------------------------------------------
            # String result
            # ---------------------------------------------

            elif isinstance(result, str):

                normalized.append({
                    "text": result,
                    "source": "rag",
                    "category": "unknown",
                    "record_id": None,
                    "score": None
                })

            # ---------------------------------------------
            # Anything else
            # ---------------------------------------------

            else:

                normalized.append({
                    "text": str(result),
                    "source": "rag",
                    "category": "unknown",
                    "record_id": None,
                    "score": None
                })

        return normalized

    # =====================================================
    # SOURCE EXTRACTION
    # =====================================================

    @staticmethod
    def _extract_sources(results):

        sources = []

        for result in results:

            if not isinstance(result, dict):
                continue

            source = result.get(
                "source"
            )

            if (
                source
                and source not in sources
            ):
                sources.append(source)

        return sources


# =========================================================
# INTEGRATION TEST
# =========================================================

if __name__ == "__main__":

    engine = BankingQueryEngine()

    customer_id = "CUST1001"

    test_queries = [

        "What is the interest rate for a personal loan?",

        "What is my account balance?",

        "How much did I spend on food?",

        "What is my balance and what are the account fees?",

        "Hello"
    ]

    print("=" * 70)
    print("BANKING QUERY ENGINE TEST")
    print("=" * 70)

    passed = 0

    expected_routes = [
        "knowledge",
        "customer_data",
        "transaction",
        "hybrid",
        "unknown"
    ]

    for number, query in enumerate(
        test_queries,
        start=1
    ):

        print("\n" + "-" * 70)

        print(
            f"TEST {number}"
        )

        print(
            f"Query: {query}"
        )

        response = engine.ask(
            query=query,
            customer_id=customer_id
        )

        actual_route = response["route"]

        expected_route = expected_routes[
            number - 1
        ]

        route_pass = (
            actual_route
            == expected_route
        )

        if route_pass:
            passed += 1

        print(
            f"Expected route: "
            f"{expected_route}"
        )

        print(
            f"Actual route:   "
            f"{actual_route}"
        )

        print(
            f"Success: "
            f"{response['success']}"
        )

        print(
            f"Sources: "
            f"{response['sources']}"
        )

        print(
            f"Route test: "
            f"{'PASS' if route_pass else 'FAIL'}"
        )

        # Show RAG result details
        if actual_route in (
            "knowledge",
            "hybrid"
        ):

            if actual_route == "knowledge":
                knowledge = response["results"]

            else:
                knowledge = response[
                    "results"
                ]["knowledge"]

            print(
                f"RAG results: "
                f"{len(knowledge)}"
            )

            for rank, result in enumerate(
                knowledge[:3],
                start=1
            ):

                print(
                    f"  {rank}. "
                    f"{result.get('source', 'rag')} | "
                    f"{result.get('record_id', '-')}"
                )

                score = result.get(
                    "score"
                )

                if score is not None:
                    print(
                        f"     score: "
                        f"{score:.4f}"
                    )

    # -----------------------------------------------------
    # Final
    # -----------------------------------------------------

    print("\n" + "=" * 70)

    print(
        f"QUERY ENGINE ROUTING: "
        f"{passed}/{len(test_queries)} "
        f"({passed / len(test_queries) * 100:.1f}%)"
    )

    if passed == len(test_queries):

        print(
            "BANKING QUERY ENGINE: PASS"
        )

    else:

        print(
            "BANKING QUERY ENGINE: NEEDS IMPROVEMENT"
        )

    print("=" * 70)