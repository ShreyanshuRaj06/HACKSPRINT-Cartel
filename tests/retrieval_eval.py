from rag.retriever import search_knowledge


# ---------------------------------------------------------
# RAG Evaluation Dataset
# ---------------------------------------------------------
#
# Each test contains:
#   query          -> user question
#   expected_terms -> important concepts that should appear
#                      in at least one retrieved result
#
# We evaluate the CONTENT, not an internal record ID.
# ---------------------------------------------------------

TEST_CASES = [
    {
        "query": "What is the interest rate for a personal loan?",
        "expected_terms": [
            "personal loan",
            "interest rate",
        ],
    },
    {
        "query": "What is the interest rate for a home loan?",
        "expected_terms": [
            "home loan",
            "interest rate",
        ],
    },
    {
        "query": "What are the eligibility criteria for an education loan?",
        "expected_terms": [
            "education loan",
            "eligibility",
        ],
    },
    {
        "query": "What is the interest rate for a vehicle loan?",
        "expected_terms": [
            "vehicle loan",
            "interest rate",
        ],
    },
    {
        "query": "Is there a charge for paying my loan early?",
        "expected_terms": [
            "loan",
            "prepayment",
        ],
    },
    {
        "query": "What documents are required for KYC?",
        "expected_terms": [
            "kyc",
            "documents",
        ],
    },
    {
        "query": "What should I do if I see an unauthorized transaction?",
        "expected_terms": [
            "unauthorized transaction",
        ],
    },
    {
        "query": "What should I do if my card is lost?",
        "expected_terms": [
            "lost",
            "card",
        ],
    },
    {
        "query": "How can I close my bank account?",
        "expected_terms": [
            "close",
            "account",
        ],
    },
    {
        "query": "Should I share my OTP with a bank employee?",
        "expected_terms": [
            "otp",
            "never share",
        ],
    },
]


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def normalize(text):
    """Normalize text for simple keyword matching."""

    return text.lower().strip()


def content_matches(content, expected_terms):
    """
    Check whether the retrieved content contains
    all important concepts for the test.
    """

    content = normalize(content)

    return all(
        term.lower() in content
        for term in expected_terms
    )


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate_retrieval():

    top1_passed = 0
    recall_at_3_passed = 0

    print("=" * 75)
    print("BANKING RAG CONTRACT EVALUATION")
    print("=" * 75)

    for number, test in enumerate(TEST_CASES, start=1):

        query = test["query"]
        expected_terms = test["expected_terms"]

        response = search_knowledge(
            query,
            top_k=3
        )

        # -------------------------------------------------
        # Check API response
        # -------------------------------------------------

        if not isinstance(response, dict):

            print(f"\nTEST {number}: FAIL")
            print("Invalid response type.")
            continue

        if response.get("success") is not True:

            print(f"\nTEST {number}: FAIL")
            print(f"Query: {query}")
            print("RAG search failed.")
            print(
                f"Error: {response.get('error', 'Unknown error')}"
            )
            continue

        results = response.get("results", [])

        if not results:

            print(f"\nTEST {number}: FAIL")
            print(f"Query: {query}")
            print("No results returned.")
            continue

        # -------------------------------------------------
        # Validate result structure
        # -------------------------------------------------

        valid_structure = True

        for result in results:

            required_fields = {
                "content",
                "source",
                "score",
            }

            if not required_fields.issubset(result.keys()):
                valid_structure = False
                break

        if not valid_structure:

            print(f"\nTEST {number}: FAIL")
            print(f"Query: {query}")
            print(
                "Result does not match the RAG API contract."
            )
            continue

        # -------------------------------------------------
        # Top-1 evaluation
        # -------------------------------------------------

        top1_content = results[0]["content"]

        top1_match = content_matches(
            top1_content,
            expected_terms
        )

        # -------------------------------------------------
        # Recall@3 evaluation
        # -------------------------------------------------

        top3_match = any(
            content_matches(
                result["content"],
                expected_terms
            )
            for result in results
        )

        if top1_match:
            top1_passed += 1

        if top3_match:
            recall_at_3_passed += 1

        # -------------------------------------------------
        # Status
        # -------------------------------------------------

        if top3_match:
            status = "PASS"
        else:
            status = "FAIL"

        print("\n" + "-" * 75)

        print(f"TEST {number}: {status}")

        print(f"Query: {query}")

        print(
            "Expected concepts: "
            + ", ".join(expected_terms)
        )

        print("\nRetrieved Results:")

        for rank, result in enumerate(
            results,
            start=1
        ):

            content = result["content"]

            # Find whether this result satisfies the test.
            matched = content_matches(
                content,
                expected_terms
            )

            marker = "  <-- MATCH" if matched else ""

            print(
                f"\n  {rank}. "
                f"Score={result['score']:.4f}"
                f"{marker}"
            )

            print(
                f"     Source: {result['source']}"
            )

            preview = (
                content
                .replace("\n", " ")
                .strip()
            )

            if len(preview) > 250:
                preview = preview[:250] + "..."

            print(
                f"     Content: {preview}"
            )

    # -----------------------------------------------------
    # Final Metrics
    # -----------------------------------------------------

    total_tests = len(TEST_CASES)

    top1_accuracy = (
        top1_passed / total_tests
    ) * 100

    recall_at_3 = (
        recall_at_3_passed / total_tests
    ) * 100

    print("\n" + "=" * 75)
    print("FINAL RESULTS")
    print("=" * 75)

    print(
        f"Top-1 Content Accuracy: "
        f"{top1_passed}/{total_tests} "
        f"({top1_accuracy:.1f}%)"
    )

    print(
        f"Recall@3:               "
        f"{recall_at_3_passed}/{total_tests} "
        f"({recall_at_3:.1f}%)"
    )

    print("\nAPI CONTRACT CHECK:")

    print(
        "search_knowledge() → "
        "success + query + results"
    )

    print(
        "Each result → "
        "content + source + score"
    )

    if recall_at_3 >= 90:

        print("\nRAG STATUS: EXCELLENT")

    elif recall_at_3 >= 70:

        print("\nRAG STATUS: GOOD")

    else:

        print("\nRAG STATUS: NEEDS IMPROVEMENT")

    print("=" * 75)


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    evaluate_retrieval()