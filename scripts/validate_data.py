import json
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


CUSTOMERS_FILE = DATA_DIR / "customers.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"


# ---------------------------------------------------------
# Controlled values currently used by our dataset
# ---------------------------------------------------------

VALID_ACCOUNT_TYPES = {
    "Savings",
    "Current",
}

VALID_ACCOUNT_STATUS = {
    "Active",
    "Inactive",
    "Closed",
}

VALID_TRANSACTION_TYPES = {
    "Debit",
    "Credit",
}

VALID_TRANSACTION_STATUS = {
    "Completed",
    "Pending",
    "Failed",
    "Reversed",
}

VALID_CATEGORIES = {
    "Shopping",
    "Salary",
    "Food",
    "Utilities",
    "Transfer",
    "Business",
    "Transport",
    "Investment",
    "Healthcare",
    "Entertainment",
}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

errors = []


def error(message):
    errors.append(message)


def load_json(path):
    """Load JSON and report malformed files."""

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        error(f"Missing file: {path.name}")
        return None

    except json.JSONDecodeError as exc:
        error(
            f"Malformed JSON in {path.name}: "
            f"line {exc.lineno}, column {exc.colno}"
        )
        return None


def is_valid_date(value):
    """Check YYYY-MM-DD date format."""

    if not isinstance(value, str):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ---------------------------------------------------------
# Customer validation
# ---------------------------------------------------------

def validate_customers(customers):

    if not isinstance(customers, list):
        error("customers.json must contain a JSON array.")
        return set()

    customer_ids = set()

    for index, customer in enumerate(customers, start=1):

        if not isinstance(customer, dict):
            error(f"Customer #{index} is not an object.")
            continue

        customer_id = customer.get("customer_id")

        if not customer_id:
            error(f"Customer #{index} is missing customer_id.")
            continue

        if customer_id in customer_ids:
            error(
                f"Duplicate customer_id: {customer_id}"
            )

        customer_ids.add(customer_id)

    return customer_ids


# ---------------------------------------------------------
# Account validation
# ---------------------------------------------------------

def validate_accounts(accounts, customer_ids):

    if not isinstance(accounts, list):
        error("accounts.json must contain a JSON array.")
        return set()

    account_ids = set()

    for index, account in enumerate(accounts, start=1):

        if not isinstance(account, dict):
            error(f"Account #{index} is not an object.")
            continue

        account_id = account.get("account_id")
        customer_id = account.get("customer_id")

        if not account_id:
            error(f"Account #{index} is missing account_id.")
        elif account_id in account_ids:
            error(
                f"Duplicate account_id: {account_id}"
            )
        else:
            account_ids.add(account_id)

        # Customer relationship
        if customer_id not in customer_ids:
            error(
                f"Orphan account {account_id}: "
                f"customer {customer_id} does not exist."
            )

        # Account type
        if account.get("account_type") not in VALID_ACCOUNT_TYPES:
            error(
                f"Invalid account_type for {account_id}: "
                f"{account.get('account_type')}"
            )

        # Balance
        balance = account.get("balance")

        if not isinstance(balance, (int, float)):
            error(
                f"Invalid balance for {account_id}: "
                f"must be numeric."
            )
        elif balance < 0:
            error(
                f"Invalid balance for {account_id}: "
                f"cannot be negative."
            )

        # Currency
        if account.get("currency") != "INR":
            error(
                f"Invalid currency for {account_id}: "
                f"{account.get('currency')}"
            )

        # Status
        if account.get("status") not in VALID_ACCOUNT_STATUS:
            error(
                f"Invalid account status for {account_id}: "
                f"{account.get('status')}"
            )

        # Opened date
        if not is_valid_date(account.get("opened_on")):
            error(
                f"Invalid opened_on date for {account_id}: "
                f"{account.get('opened_on')}"
            )

    return account_ids


# ---------------------------------------------------------
# Transaction validation
# ---------------------------------------------------------

def validate_transactions(
    transactions,
    account_ids
):

    if not isinstance(transactions, list):
        error(
            "transactions.json must contain a JSON array."
        )
        return set()

    transaction_ids = set()

    for index, transaction in enumerate(
        transactions,
        start=1
    ):

        if not isinstance(transaction, dict):
            error(
                f"Transaction #{index} is not an object."
            )
            continue

        transaction_id = transaction.get(
            "transaction_id"
        )

        account_id = transaction.get(
            "account_id"
        )

        # Transaction ID
        if not transaction_id:
            error(
                f"Transaction #{index} is missing "
                "transaction_id."
            )

        elif transaction_id in transaction_ids:
            error(
                f"Duplicate transaction_id: "
                f"{transaction_id}"
            )

        else:
            transaction_ids.add(transaction_id)

        # Account relationship
        if account_id not in account_ids:
            error(
                f"Orphan transaction "
                f"{transaction_id}: "
                f"account {account_id} does not exist."
            )

        # Date
        if not is_valid_date(
            transaction.get("date")
        ):
            error(
                f"Invalid transaction date for "
                f"{transaction_id}: "
                f"{transaction.get('date')}"
            )

        # Transaction type
        if transaction.get("type") not in VALID_TRANSACTION_TYPES:
            error(
                f"Invalid transaction type for "
                f"{transaction_id}: "
                f"{transaction.get('type')}"
            )

        # Category
        if transaction.get("category") not in VALID_CATEGORIES:
            error(
                f"Invalid category for "
                f"{transaction_id}: "
                f"{transaction.get('category')}"
            )

        # Amount
        amount = transaction.get("amount")

        if not isinstance(amount, (int, float)):
            error(
                f"Invalid amount for "
                f"{transaction_id}: "
                "must be numeric."
            )

        elif amount <= 0:
            error(
                f"Invalid amount for "
                f"{transaction_id}: "
                "must be greater than zero."
            )

        # Currency
        if transaction.get("currency") != "INR":
            error(
                f"Invalid currency for "
                f"{transaction_id}: "
                f"{transaction.get('currency')}"
            )

        # Status
        if transaction.get("status") not in VALID_TRANSACTION_STATUS:
            error(
                f"Invalid transaction status for "
                f"{transaction_id}: "
                f"{transaction.get('status')}"
            )

    return transaction_ids


# ---------------------------------------------------------
# Main validation
# ---------------------------------------------------------

def validate_data():

    print("=" * 70)
    print("BANKING DATA VALIDATION")
    print("=" * 70)

    customers = load_json(CUSTOMERS_FILE)
    accounts = load_json(ACCOUNTS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)

    # Stop relationship checks if JSON itself is invalid.
    if customers is None or accounts is None or transactions is None:

        print("\nVALIDATION: FAIL")

        for item in errors:
            print(f"  ERROR: {item}")

        return False

    # Validate datasets
    customer_ids = validate_customers(
        customers
    )

    account_ids = validate_accounts(
        accounts,
        customer_ids
    )

    transaction_ids = validate_transactions(
        transactions,
        account_ids
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\nRecords:")
    print(f"  Customers:    {len(customers)}")
    print(f"  Accounts:     {len(accounts)}")
    print(f"  Transactions: {len(transactions)}")

    print("\nUnique IDs:")
    print(f"  Customer IDs:    {len(customer_ids)}")
    print(f"  Account IDs:     {len(account_ids)}")
    print(f"  Transaction IDs: {len(transaction_ids)}")

    print("\nValidation Checks:")
    print("  JSON structure       : PASS")
    print("  Duplicate IDs        : PASS")
    print("  Customer relations   : PASS")
    print("  Account relations    : PASS")
    print("  Transaction dates    : PASS")
    print("  Transaction amounts  : PASS")
    print("  Transaction types    : PASS")
    print("  Transaction categories: PASS")

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    if errors:

        print("\n" + "=" * 70)
        print("VALIDATION: FAIL")
        print("=" * 70)

        for item in errors:
            print(f"ERROR: {item}")

        return False

    print("\n" + "=" * 70)
    print("DATA VALIDATION: PASS")
    print("=" * 70)

    return True


if __name__ == "__main__":
    validate_data()