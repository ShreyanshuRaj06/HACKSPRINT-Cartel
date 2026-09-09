import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "transactions.json"


class TransactionAnalyzer:
    """
    Deterministic transaction-analysis engine.

    This class performs numerical calculations directly
    from the banking transaction dataset.

    The LLM should explain these results, not calculate them.
    """

    def __init__(self, data_file=DATA_FILE):
        self.data_file = Path(data_file)
        self.transactions = self._load_transactions()

    # -----------------------------------------------------
    # Data loading
    # -----------------------------------------------------

    def _load_transactions(self):
        with open(
            self.data_file,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    # -----------------------------------------------------
    # Basic filtering
    # -----------------------------------------------------

    def get_transactions(
        self,
        account_id=None,
        transaction_type=None,
        category=None,
        start_date=None,
        end_date=None
    ):
        """
        Return transactions matching the supplied filters.
        """

        results = []

        for transaction in self.transactions:

            if (
                account_id is not None
                and transaction["account_id"] != account_id
            ):
                continue

            if (
                transaction_type is not None
                and transaction["type"] != transaction_type
            ):
                continue

            if (
                category is not None
                and transaction["category"] != category
            ):
                continue

            transaction_date = datetime.strptime(
                transaction["date"],
                "%Y-%m-%d"
            ).date()

            if start_date is not None:

                start = self._parse_date(start_date)

                if transaction_date < start:
                    continue

            if end_date is not None:

                end = self._parse_date(end_date)

                if transaction_date > end:
                    continue

            results.append(transaction)

        return results

    # -----------------------------------------------------
    # Total spending
    # -----------------------------------------------------

    def total_spending(
        self,
        account_id=None,
        start_date=None,
        end_date=None
    ):
        """
        Calculate total debit spending.
        """

        transactions = self.get_transactions(
            account_id=account_id,
            transaction_type="Debit",
            start_date=start_date,
            end_date=end_date
        )

        return round(
            sum(
                transaction["amount"]
                for transaction in transactions
            ),
            2
        )

    # -----------------------------------------------------
    # Total credits
    # -----------------------------------------------------

    def total_credits(
        self,
        account_id=None,
        start_date=None,
        end_date=None
    ):
        """
        Calculate total incoming money.
        """

        transactions = self.get_transactions(
            account_id=account_id,
            transaction_type="Credit",
            start_date=start_date,
            end_date=end_date
        )

        return round(
            sum(
                transaction["amount"]
                for transaction in transactions
            ),
            2
        )

    # -----------------------------------------------------
    # Category spending
    # -----------------------------------------------------

    def spending_by_category(
        self,
        account_id=None,
        start_date=None,
        end_date=None
    ):
        """
        Calculate debit spending grouped by category.
        """

        transactions = self.get_transactions(
            account_id=account_id,
            transaction_type="Debit",
            start_date=start_date,
            end_date=end_date
        )

        totals = defaultdict(float)

        for transaction in transactions:

            totals[
                transaction["category"]
            ] += transaction["amount"]

        return {
            category: round(amount, 2)
            for category, amount in sorted(
                totals.items(),
                key=lambda item: item[1],
                reverse=True
            )
        }

    # -----------------------------------------------------
    # Biggest expenses
    # -----------------------------------------------------

    def biggest_expenses(
        self,
        account_id=None,
        start_date=None,
        end_date=None,
        limit=5
    ):
        """
        Return the largest debit transactions.
        """

        transactions = self.get_transactions(
            account_id=account_id,
            transaction_type="Debit",
            start_date=start_date,
            end_date=end_date
        )

        transactions = sorted(
            transactions,
            key=lambda transaction: transaction["amount"],
            reverse=True
        )

        return transactions[:limit]

    # -----------------------------------------------------
    # Transaction count
    # -----------------------------------------------------

    def transaction_count(
        self,
        account_id=None,
        transaction_type=None,
        start_date=None,
        end_date=None
    ):
        """
        Count transactions matching the filters.
        """

        return len(
            self.get_transactions(
                account_id=account_id,
                transaction_type=transaction_type,
                start_date=start_date,
                end_date=end_date
            )
        )

    # -----------------------------------------------------
    # Monthly spending
    # -----------------------------------------------------

    def monthly_spending(
        self,
        account_id=None,
        year=None,
        month=None
    ):
        """
        Calculate spending for a specific month.
        """

        if year is None or month is None:
            raise ValueError(
                "year and month are required."
            )

        start = datetime(
            year,
            month,
            1
        ).date()

        if month == 12:
            end = datetime(
                year + 1,
                1,
                1
            ).date()

        else:
            end = datetime(
                year,
                month + 1,
                1
            ).date()

        end = end.fromordinal(
            end.toordinal() - 1
        )

        return self.total_spending(
            account_id=account_id,
            start_date=start,
            end_date=end
        )

    # -----------------------------------------------------
    # Month comparison
    # -----------------------------------------------------

    def compare_months(
        self,
        account_id,
        year1,
        month1,
        year2,
        month2
    ):
        """
        Compare spending between two months.
        """

        first_month = self.monthly_spending(
            account_id,
            year1,
            month1
        )

        second_month = self.monthly_spending(
            account_id,
            year2,
            month2
        )

        difference = round(
            second_month - first_month,
            2
        )

        if first_month == 0:
            percentage_change = None

        else:
            percentage_change = round(
                (
                    difference
                    / first_month
                ) * 100,
                2
            )

        if difference > 0:
            direction = "increased"

        elif difference < 0:
            direction = "decreased"

        else:
            direction = "unchanged"

        return {
            "first_month": {
                "year": year1,
                "month": month1,
                "spending": first_month
            },
            "second_month": {
                "year": year2,
                "month": month2,
                "spending": second_month
            },
            "difference": difference,
            "percentage_change": percentage_change,
            "direction": direction
        }

    # -----------------------------------------------------
    # Net cash flow
    # -----------------------------------------------------

    def net_cash_flow(
        self,
        account_id=None,
        start_date=None,
        end_date=None
    ):
        """
        Credits minus debits.
        """

        credits = self.total_credits(
            account_id,
            start_date,
            end_date
        )

        debits = self.total_spending(
            account_id,
            start_date,
            end_date
        )

        return round(
            credits - debits,
            2
        )

    # -----------------------------------------------------
    # Date helper
    # -----------------------------------------------------

    @staticmethod
    def _parse_date(value):

        if hasattr(value, "year"):
            return value

        return datetime.strptime(
            str(value),
            "%Y-%m-%d"
        ).date()


# ---------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------

if __name__ == "__main__":

    analyzer = TransactionAnalyzer()

    print("=" * 70)
    print("TRANSACTION ANALYZER TEST")
    print("=" * 70)

    account = "ACC10001"

    print(f"\nAccount: {account}")

    print(
        "\nTotal spending:"
    )

    print(
        analyzer.total_spending(
            account_id=account
        )
    )

    print(
        "\nTotal credits:"
    )

    print(
        analyzer.total_credits(
            account_id=account
        )
    )

    print(
        "\nSpending by category:"
    )

    for category, amount in analyzer.spending_by_category(
        account_id=account
    ).items():

        print(
            f"  {category}: ₹{amount:,.2f}"
        )

    print(
        "\nBiggest expenses:"
    )

    for transaction in analyzer.biggest_expenses(
        account_id=account,
        limit=3
    ):

        print(
            f"  {transaction['transaction_id']} | "
            f"{transaction['category']} | "
            f"₹{transaction['amount']:,.2f} | "
            f"{transaction['date']}"
        )

    print(
        "\nTransaction count:"
    )

    print(
        analyzer.transaction_count(
            account_id=account
        )
    )

    print(
        "\nNet cash flow:"
    )

    print(
        analyzer.net_cash_flow(
            account_id=account
        )
    )

    print("\n" + "=" * 70)
    print("TRANSACTION ANALYZER: PASS")
    print("=" * 70)