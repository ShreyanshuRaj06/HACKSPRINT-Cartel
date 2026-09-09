import json
import random
from datetime import date, timedelta
from pathlib import Path


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "transactions.json"

random.seed(42)

START_DATE = date(2026, 6, 1)
END_DATE = date(2026, 9, 30)

TARGET_TOTAL = 140


# ---------------------------------------------------------
# Banking transaction templates
# ---------------------------------------------------------

DEBIT_TEMPLATES = [
    ("Food", "Restaurant Payment"),
    ("Food", "Food Delivery"),
    ("Shopping", "Online Shopping"),
    ("Shopping", "Retail Purchase"),
    ("Transport", "Cab Payment"),
    ("Transport", "Fuel Payment"),
    ("Utilities", "Electricity Bill"),
    ("Utilities", "Internet Bill"),
    ("Healthcare", "Pharmacy Payment"),
    ("Healthcare", "Medical Consultation"),
    ("Entertainment", "Movie Tickets"),
    ("Entertainment", "Streaming Subscription"),
    ("Investment", "Mutual Fund Investment"),
    ("Business", "Office Supplies"),
    ("Business", "Vendor Payment"),
]

CREDIT_TEMPLATES = [
    ("Salary", "Monthly Salary Credit"),
    ("Transfer", "Funds Received"),
    ("Business", "Client Payment"),
]


# ---------------------------------------------------------
# Amount ranges
# ---------------------------------------------------------

DEBIT_RANGES = {
    "Food": (300, 3500),
    "Shopping": (500, 12000),
    "Transport": (200, 3000),
    "Utilities": (500, 5000),
    "Healthcare": (500, 8000),
    "Entertainment": (300, 4000),
    "Investment": (5000, 30000),
    "Business": (1500, 25000),
}

CREDIT_RANGES = {
    "Salary": (50000, 150000),
    "Transfer": (2000, 30000),
    "Business": (10000, 150000),
}


# ---------------------------------------------------------
# Load existing transactions
# ---------------------------------------------------------

with open(DATA_FILE, "r", encoding="utf-8") as file:
    transactions = json.load(file)


existing_ids = {
    transaction["transaction_id"]
    for transaction in transactions
}

existing_count = len(transactions)


# ---------------------------------------------------------
# Generate dates
# ---------------------------------------------------------

date_range = (
    END_DATE - START_DATE
).days + 1

all_dates = [
    START_DATE + timedelta(days=i)
    for i in range(date_range)
]


# ---------------------------------------------------------
# Account-specific spending profiles
# ---------------------------------------------------------

profiles = {
    "ACC10001": {
        "debit_weights": {
            "Food": 4,
            "Shopping": 4,
            "Transport": 2,
            "Utilities": 1,
            "Entertainment": 2,
        }
    },

    "ACC10002": {
        "debit_weights": {
            "Utilities": 4,
            "Shopping": 3,
            "Food": 2,
            "Transport": 1,
        }
    },

    "ACC10003": {
        "debit_weights": {
            "Business": 6,
            "Transport": 2,
            "Utilities": 1,
            "Food": 1,
        }
    },

    "ACC10004": {
        "debit_weights": {
            "Food": 4,
            "Transport": 3,
            "Shopping": 2,
            "Entertainment": 2,
        }
    },

    "ACC10005": {
        "debit_weights": {
            "Investment": 5,
            "Shopping": 2,
            "Food": 1,
            "Transport": 1,
        }
    },

    "ACC10006": {
        "debit_weights": {
            "Healthcare": 4,
            "Entertainment": 3,
            "Food": 2,
            "Transport": 1,
        }
    },

    "ACC10007": {
        "debit_weights": {
            "Business": 6,
            "Transport": 2,
            "Shopping": 1,
            "Utilities": 1,
        }
    },

    "ACC10008": {
        "debit_weights": {
            "Shopping": 5,
            "Food": 2,
            "Entertainment": 2,
            "Transport": 1,
        }
    },
}


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def choose_category(account_id):

    weights = profiles[account_id]["debit_weights"]

    categories = list(weights.keys())
    values = list(weights.values())

    return random.choices(
        categories,
        weights=values,
        k=1
    )[0]


def next_transaction_id():

    number = 10001

    while f"TXN{number}" in existing_ids:
        number += 1

    transaction_id = f"TXN{number}"

    existing_ids.add(transaction_id)

    return transaction_id


def random_amount(transaction_type, category):

    if transaction_type == "Debit":
        minimum, maximum = DEBIT_RANGES[category]

    else:
        minimum, maximum = CREDIT_RANGES[category]

    return round(
        random.uniform(
            minimum,
            maximum
        ),
        2
    )


# ---------------------------------------------------------
# Generate additional transactions
# ---------------------------------------------------------

accounts = [
    f"ACC{10000 + i}"
    for i in range(1, 9)
]


additional_needed = max(
    0,
    TARGET_TOTAL - existing_count
)


new_transactions = []


for _ in range(additional_needed):

    account_id = random.choice(accounts)

    transaction_date = random.choice(
        all_dates
    )

    # Mostly debit transactions,
    # with some credits.
    transaction_type = random.choices(
        ["Debit", "Credit"],
        weights=[80, 20],
        k=1
    )[0]

    if transaction_type == "Debit":

        category, description = random.choice(
            [
                template
                for template in DEBIT_TEMPLATES
                if template[0]
                in profiles[account_id]["debit_weights"]
            ]
        )

    else:

        category, description = random.choice(
            CREDIT_TEMPLATES
        )

    amount = random_amount(
        transaction_type,
        category
    )

    transaction = {
        "transaction_id": next_transaction_id(),
        "account_id": account_id,
        "date": transaction_date.isoformat(),
        "type": transaction_type,
        "category": category,
        "description": description,
        "amount": amount,
        "currency": "INR",
        "status": "Completed",
    }

    new_transactions.append(
        transaction
    )


# ---------------------------------------------------------
# Combine and sort
# ---------------------------------------------------------

transactions.extend(
    new_transactions
)

transactions.sort(
    key=lambda item: (
        item["date"],
        item["transaction_id"]
    )
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

with open(
    DATA_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        transactions,
        file,
        indent=2,
        ensure_ascii=False
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("=" * 70)
print("TRANSACTION DATA GENERATOR")
print("=" * 70)

print(
    f"Existing transactions : {existing_count}"
)

print(
    f"New transactions      : {len(new_transactions)}"
)

print(
    f"Total transactions    : {len(transactions)}"
)

print(
    f"Date range            : "
    f"{transactions[0]['date']} → "
    f"{transactions[-1]['date']}"
)

print("\nTransaction distribution:")

for account_id in accounts:

    count = sum(
        1
        for transaction in transactions
        if transaction["account_id"] == account_id
    )

    print(
        f"  {account_id}: {count}"
    )

print("\nDATA GENERATION: COMPLETE")

print("=" * 70)