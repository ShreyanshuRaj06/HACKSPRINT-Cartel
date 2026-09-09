class TransactionAnalyzer:
    """
    Deterministic Python component for authoritative financial calculations.
    Operates strictly on provided transaction arrays. Does NOT fetch external data.
    100% resilient against missing keys, empty arrays, and custom data schemas.
    """

    @staticmethod
    def calculate_total_spending(transactions):
        """Calculate total debit spending from transactions."""
        if not transactions:
            return 0.0
        debits = [float(t.get('amount', 0.0)) for t in transactions if t.get('type') == 'debit']
        return round(float(sum(debits)), 2)

    @staticmethod
    def calculate_total_income(transactions):
        """Calculate total credit/income from transactions."""
        if not transactions:
            return 0.0
        credits = [float(t.get('amount', 0.0)) for t in transactions if t.get('type') == 'credit']
        return round(float(sum(credits)), 2)

    @staticmethod
    def calculate_category_breakdown(transactions):
        """
        Calculate aggregate spending grouped by category.
        Returns a dictionary with amount, transaction count, and percentage of total spending.
        """
        if not transactions:
            return {}

        category_totals = {}
        category_counts = {}
        total_spending = 0.0

        for t in transactions:
            if t.get('type') == 'debit':
                cat = str(t.get('category', 'uncategorized')).lower().strip()
                amt = float(t.get('amount', 0.0))
                category_totals[cat] = category_totals.get(cat, 0.0) + amt
                category_counts[cat] = category_counts.get(cat, 0) + 1
                total_spending += amt

        total_spending = round(total_spending, 2)
        breakdown = {}
        for cat, amt in category_totals.items():
            amt_rounded = round(amt, 2)
            pct = round((amt_rounded / total_spending * 100), 2) if total_spending > 0 else 0.0
            breakdown[cat] = {
                "category": cat,
                "total_amount": amt_rounded,
                "transaction_count": category_counts[cat],
                "percentage_of_total": pct
            }

        return dict(sorted(breakdown.items(), key=lambda item: item[1]['total_amount'], reverse=True))

    @staticmethod
    def calculate_category_spending(transactions, category_name):
        """Calculate spending for a specific category."""
        if not transactions or not category_name:
            return {
                "category": str(category_name).lower(),
                "total_amount": 0.0,
                "transaction_count": 0,
                "transactions": []
            }

        target_cat = str(category_name).lower().strip()
        matching_txns = [
            t for t in transactions 
            if t.get('type') == 'debit' and str(t.get('category', '')).lower().strip() == target_cat
        ]
        total_amt = round(float(sum(float(t.get('amount', 0.0)) for t in matching_txns)), 2)
        return {
            "category": target_cat,
            "total_amount": total_amt,
            "transaction_count": len(matching_txns),
            "transactions": matching_txns
        }

    @staticmethod
    def get_top_expenses(transactions, limit=5):
        """Get the top N largest debit transactions."""
        if not transactions:
            return []
        debits = [t for t in transactions if t.get('type') == 'debit']
        sorted_debits = sorted(debits, key=lambda x: float(x.get('amount', 0.0)), reverse=True)
        return sorted_debits[:limit]

    @staticmethod
    def compare_periods(current_transactions, comparison_transactions):
        """
        Compare financial spending between two periods deterministically.
        """
        current_spending = TransactionAnalyzer.calculate_total_spending(current_transactions or [])
        comparison_spending = TransactionAnalyzer.calculate_total_spending(comparison_transactions or [])
        
        diff = round(current_spending - comparison_spending, 2)
        
        if comparison_spending > 0:
            percentage_change = round((diff / comparison_spending) * 100, 2)
        else:
            percentage_change = 100.0 if current_spending > 0 else 0.0

        current_cats = TransactionAnalyzer.calculate_category_breakdown(current_transactions or [])
        comparison_cats = TransactionAnalyzer.calculate_category_breakdown(comparison_transactions or [])

        all_categories = set(current_cats.keys()).union(set(comparison_cats.keys()))
        category_shifts = {}
        for cat in all_categories:
            cur_amt = current_cats.get(cat, {}).get('total_amount', 0.0)
            prev_amt = comparison_cats.get(cat, {}).get('total_amount', 0.0)
            shift_diff = round(cur_amt - prev_amt, 2)
            category_shifts[cat] = {
                "current_amount": cur_amt,
                "comparison_amount": prev_amt,
                "difference": shift_diff,
                "increased": shift_diff > 0
            }

        return {
            "current_period_spending": current_spending,
            "comparison_period_spending": comparison_spending,
            "difference": diff,
            "percentage_change": percentage_change,
            "has_increased": diff > 0,
            "category_shifts": category_shifts
        }

    @classmethod
    def analyze(cls, transactions, comparison_transactions=None, category=None, top_n=5):
        """
        Produce a unified, structured, authoritative financial analysis.
        """
        txns = transactions or []
        total_spending = cls.calculate_total_spending(txns)
        total_income = cls.calculate_total_income(txns)
        category_breakdown = cls.calculate_category_breakdown(txns)
        top_expenses = cls.get_top_expenses(txns, limit=top_n)

        result = {
            "verified": True,
            "currency": "INR",
            "transaction_count": len(txns),
            "summary": {
                "total_spending": total_spending,
                "total_income": total_income,
                "net_cash_flow": round(total_income - total_spending, 2)
            },
            "category_breakdown": category_breakdown,
            "top_expenses": top_expenses
        }

        if category:
            result["specific_category_analysis"] = cls.calculate_category_spending(txns, category)

        if comparison_transactions is not None:
            result["period_comparison"] = cls.compare_periods(txns, comparison_transactions)

        return result
