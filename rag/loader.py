import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename):
    """Load a JSON file from the data directory."""
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_knowledge_base():
    """
    Load all public banking knowledge sources
    and convert them into standardized documents.
    """

    documents = []

    # -------------------------
    # Loan Products
    # -------------------------
    loans = load_json("loan_products.json")

    for loan in loans:
        text = (
            f"Loan Product: {loan['loan_name']}\n"
            f"Description: {loan['description']}\n"
            f"Interest Rate: {loan['interest_rate']}\n"
            f"Loan Amount: ₹{loan['min_amount']} to ₹{loan['max_amount']}\n"
            f"Tenure: {loan['tenure']}\n"
            f"Processing Fee: {loan['processing_fee']}\n"
            f"Eligibility: {', '.join(loan['eligibility'])}\n"
            f"Documents Required: {', '.join(loan['documents_required'])}\n"
            f"Prepayment Allowed: {loan['prepayment_allowed']}\n"
            f"Prepayment Charges: {loan['prepayment_charges']}"
        )

        documents.append(
            {
                "text": text,
                "source": "loan_products.json",
                "category": "loan",
                "subcategory": loan["loan_name"],
                "record_id": loan["loan_id"],
            }
        )

    # -------------------------
    # FAQs
    # -------------------------
    faqs = load_json("faq.json")

    for faq in faqs:
        text = (
            f"Question: {faq['question']}\n"
            f"Answer: {faq['answer']}"
        )

        documents.append(
            {
                "text": text,
                "source": "faq.json",
                "category": "faq",
                "subcategory": faq["category"],
                "record_id": faq["faq_id"],
            }
        )

    # -------------------------
    # Fees
    # -------------------------
    fees = load_json("fees.json")

    for fee in fees:
        text = (
            f"Fee: {fee['fee_name']}\n"
            f"Category: {fee['category']}\n"
            f"Description: {fee['description']}\n"
            f"Amount: {fee['amount']}\n"
            f"Conditions: {fee['conditions']}"
        )

        documents.append(
            {
                "text": text,
                "source": "fees.json",
                "category": "fee",
                "subcategory": fee["category"],
                "record_id": fee["fee_id"],
            }
        )

    # -------------------------
    # Policies
    # -------------------------
    policies = load_json("policies.json")

    for policy in policies:
        text = (
            f"Policy: {policy['policy_name']}\n"
            f"Title: {policy['title']}\n"
            f"Category: {policy['category']}\n"
            f"Policy Details: {policy['content']}"
        )

        documents.append(
            {
                "text": text,
                "source": "policies.json",
                "category": "policy",
                "subcategory": policy["category"],
                "record_id": policy["policy_id"],
            }
        )

    return documents


if __name__ == "__main__":
    docs = load_knowledge_base()

    print("Knowledge base loaded successfully!")
    print("Total documents:", len(docs))

    for i, doc in enumerate(docs[:3], start=1):
        print(f"\n--- Document {i} ---")
        print("Source:", doc["source"])
        print("Category:", doc["category"])
        print("Record ID:", doc["record_id"])
        print(doc["text"][:300])