import json
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

CUSTOMERS_FILE = DATA_DIR / "customers.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"


class CustomerService:
    """
    Customer-scoped banking data access layer.

    Resolves:
        Customer → Accounts → Transactions

    This layer prevents the chatbot from directly querying
    arbitrary customer/account records.
    """

    def __init__(self):

        self.customers = self._load_json(
            CUSTOMERS_FILE
        )

        self.accounts = self._load_json(
            ACCOUNTS_FILE
        )

        self.transactions = self._load_json(
            TRANSACTIONS_FILE
        )

    # -----------------------------------------------------
    # JSON loader
    # -----------------------------------------------------

    @staticmethod
    def _load_json(path):

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    # -----------------------------------------------------
    # Customer profile
    # -----------------------------------------------------

    def get_customer_profile(self, customer_id):
        """
        Return the profile for a customer.
        """

        for customer in self.customers:

            if customer.get("customer_id") == customer_id:

                return customer.copy()

        return None

    # -----------------------------------------------------
    # Customer accounts
    # -----------------------------------------------------

    def get_accounts(self, customer_id):
        """
        Return all accounts belonging to the customer.
        """

        customer_exists = (
            self.get_customer_profile(customer_id)
            is not None
        )

        if not customer_exists:
            return []

        return [
            account.copy()
            for account in self.accounts
            if account.get("customer_id") == customer_id
        ]

    # -----------------------------------------------------
    # Customer balance
    # -----------------------------------------------------

    def get_balance(self, customer_id):
        """
        Return account balances belonging to the customer.

        Supports multiple accounts.
        """

        accounts = self.get_accounts(
            customer_id
        )

        if not accounts:
            return {
                "customer_id": customer_id,
                "accounts": [],
                "total_balance": 0.0,
                "currency": "INR"
            }

        account_details = []

        total_balance = 0.0

        for account in accounts:

            balance = float(
                account.get("balance", 0)
            )

            total_balance += balance

            account_details.append({
                "account_id": account["account_id"],
                "account_type": account["account_type"],
                "balance": balance,
                "currency": account["currency"],
                "status": account["status"]
            })

        return {
            "customer_id": customer_id,
            "accounts": account_details,
            "total_balance": round(
                total_balance,
                2
            ),
            "currency": "INR"
        }

    # -----------------------------------------------------
    # Customer transactions
    # -----------------------------------------------------

    def get_transactions(self, customer_id):
        """
        Return transactions from ALL accounts belonging
        to the customer.
        """

        accounts = self.get_accounts(
            customer_id
        )

        account_ids = {
            account["account_id"]
            for account in accounts
        }

        transactions = [
            transaction.copy()
            for transaction in self.transactions
            if transaction.get("account_id")
            in account_ids
        ]

        return sorted(
            transactions,
            key=lambda transaction: (
                transaction["date"],
                transaction["transaction_id"]
            ),
            reverse=True
        )

    # -----------------------------------------------------
    # Customer transaction count
    # -----------------------------------------------------

    def get_transaction_count(self, customer_id):

        return len(
            self.get_transactions(
                customer_id
            )
        )

    # -----------------------------------------------------
    # Customer summary
    # -----------------------------------------------------

    def get_customer_summary(self, customer_id):
        """
        Return a compact customer-level summary.
        """

        profile = self.get_customer_profile(
            customer_id
        )

        if profile is None:
            return None

        accounts = self.get_accounts(
            customer_id
        )

        balance = self.get_balance(
            customer_id
        )

        transaction_count = (
            self.get_transaction_count(
                customer_id
            )
        )

        return {
            "customer": profile,
            "accounts": accounts,
            "balance": balance,
            "transaction_count": transaction_count
        }


# ---------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------

if __name__ == "__main__":

    service = CustomerService()

    customer_id = "CUST1001"

    print("=" * 70)
    print("CUSTOMER SERVICE TEST")
    print("=" * 70)

    # -----------------------------------------------------
    # Profile
    # -----------------------------------------------------

    profile = service.get_customer_profile(
        customer_id
    )

    print("\nCustomer profile:")

    if profile:

        print(
            f"  ID: {profile['customer_id']}"
        )

        print(
            f"  Name: {profile['name']}"
        )

        print(
            f"  Email: {profile['email']}"
        )

    else:

        print("  Customer not found.")

    # -----------------------------------------------------
    # Accounts
    # -----------------------------------------------------

    accounts = service.get_accounts(
        customer_id
    )

    print("\nAccounts:")

    for account in accounts:

        print(
            f"  {account['account_id']} | "
            f"{account['account_type']} | "
            f"₹{account['balance']:,.2f}"
        )

    # -----------------------------------------------------
    # Balance
    # -----------------------------------------------------

    balance = service.get_balance(
        customer_id
    )

    print("\nBalance summary:")

    print(
        f"  Total balance: "
        f"₹{balance['total_balance']:,.2f}"
    )

    # -----------------------------------------------------
    # Transactions
    # -----------------------------------------------------

    transactions = service.get_transactions(
        customer_id
    )

    print("\nTransactions:")

    print(
        f"  Total transactions: "
        f"{len(transactions)}"
    )

    for transaction in transactions[:5]:

        print(
            f"  {transaction['transaction_id']} | "
            f"{transaction['account_id']} | "
            f"{transaction['type']} | "
            f"{transaction['category']} | "
            f"₹{transaction['amount']:,.2f} | "
            f"{transaction['date']}"
        )

    # -----------------------------------------------------
    # Security check
    # -----------------------------------------------------

    other_customer_transactions = (
        service.get_transactions(
            "CUST1002"
        )
    )

    customer_account_ids = {
        account["account_id"]
        for account in accounts
    }

    leaked = [
        transaction
        for transaction in transactions
        if transaction["account_id"]
        not in customer_account_ids
    ]

    assert leaked == []

    print("\nCustomer isolation check: PASS")

    print("\n" + "=" * 70)
    print("CUSTOMER SERVICE: PASS")
    print("=" * 70)