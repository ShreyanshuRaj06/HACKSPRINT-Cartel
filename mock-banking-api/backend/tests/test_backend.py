import sys
import os
import unittest

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

from services.customer_service import get_customer_by_id, get_all_customers
from services.account_service import get_accounts_by_customer_id, get_account_by_id, get_balance_by_id
from services.transaction_service import get_transactions
from services.transaction_analyzer import TransactionAnalyzer
from services.investigation_service import investigate_transactions
from services.loan_service import get_loans_by_customer_id

class TestMockBankingBackend(unittest.TestCase):

    def test_01_customer_retrieval(self):
        customer = get_customer_by_id("CUST001")
        self.assertIsNotNone(customer)
        self.assertEqual(customer["id"], "CUST001")
        self.assertEqual(customer["name"], "Aarav Sharma")

    def test_02_account_retrieval(self):
        accounts = get_accounts_by_customer_id("CUST001")
        self.assertTrue(len(accounts) >= 1)
        account_ids = [acc["id"] for acc in accounts]
        self.assertIn("ACC001", account_ids)

    def test_03_balance_retrieval(self):
        balance = get_balance_by_id("ACC001", customer_id="CUST001")
        self.assertIsNotNone(balance)
        self.assertEqual(balance["account_id"], "ACC001")
        self.assertEqual(balance["balance"], 68420.50)

    def test_04_transaction_retrieval(self):
        txns = get_transactions(customer_id="CUST001", account_id="ACC001")
        self.assertIsNotNone(txns)
        self.assertTrue(len(txns) > 0)
        for t in txns:
            self.assertEqual(t["account_id"], "ACC001")

    def test_05_date_filtering(self):
        aug_txns = get_transactions(customer_id="CUST001", start_date="2026-08-01", end_date="2026-08-31")
        for t in aug_txns:
            self.assertTrue("2026-08-01" <= t["date"] <= "2026-08-31")

        sep_txns = get_transactions(customer_id="CUST001", start_date="2026-09-01", end_date="2026-09-30")
        for t in sep_txns:
            self.assertTrue("2026-09-01" <= t["date"] <= "2026-09-30")

    def test_06_transaction_analyzer_totals(self):
        sep_txns = get_transactions(customer_id="CUST001", start_date="2026-09-01", end_date="2026-09-30")
        spending = TransactionAnalyzer.calculate_total_spending(sep_txns)
        income = TransactionAnalyzer.calculate_total_income(sep_txns)
        # 25000 (rent) + 24500 (travel) + 32000 (travel) + 2850 (food) + 38900 (shopping) + 4200 (groceries) + 3600 (utilities) + 920 (food) = 131970.0
        self.assertEqual(spending, 131970.00)
        self.assertEqual(income, 110000.00)

    def test_07_category_analysis(self):
        sep_txns = get_transactions(customer_id="CUST001", start_date="2026-09-01", end_date="2026-09-30")
        food_analysis = TransactionAnalyzer.calculate_category_spending(sep_txns, "food")
        self.assertEqual(food_analysis["category"], "food")
        # 2850 + 920 = 3770
        self.assertEqual(food_analysis["total_amount"], 3770.00)
        self.assertEqual(food_analysis["transaction_count"], 2)

    def test_08_month_comparison(self):
        aug_txns = get_transactions(customer_id="CUST001", start_date="2026-08-01", end_date="2026-08-31")
        sep_txns = get_transactions(customer_id="CUST001", start_date="2026-09-01", end_date="2026-09-30")
        comparison = TransactionAnalyzer.compare_periods(sep_txns, aug_txns)
        
        self.assertTrue(comparison["has_increased"])
        self.assertGreater(comparison["current_period_spending"], comparison["comparison_period_spending"])
        self.assertEqual(comparison["current_period_spending"], 131970.00)
        # August spending: 25000 + 650 + 2450 + 3200 + 4800 + 1200 + 1850 + 1600 = 40750.00
        self.assertEqual(comparison["comparison_period_spending"], 40750.00)
        self.assertEqual(comparison["difference"], 91220.00)

    def test_09_top_expenses(self):
        sep_txns = get_transactions(customer_id="CUST001", start_date="2026-09-01", end_date="2026-09-30")
        top_expenses = TransactionAnalyzer.get_top_expenses(sep_txns, limit=3)
        self.assertEqual(len(top_expenses), 3)
        # Highest expense: Apple Store (38900)
        self.assertEqual(top_expenses[0]["description"], "Apple Store - Smartwatch")
        self.assertEqual(top_expenses[0]["amount"], 38900.00)
        # 2nd highest: Taj Hotels (32000)
        self.assertEqual(top_expenses[1]["description"], "Taj Hotels Goa Booking")

    def test_10_no_transactions_period(self):
        future_txns = get_transactions(customer_id="CUST001", start_date="2028-01-01", end_date="2028-01-31")
        self.assertEqual(len(future_txns), 0)
        spending = TransactionAnalyzer.calculate_total_spending(future_txns)
        self.assertEqual(spending, 0.0)

    def test_11_invalid_customer_rejected(self):
        res = investigate_transactions(customer_id="NON_EXISTENT_CUST")
        self.assertFalse(res["verified"])
        self.assertEqual(res["error_code"], "CUSTOMER_NOT_FOUND")

    def test_12_cross_customer_access_prevented(self):
        # CUST001 attempts to access ACC002 (owned by CUST002)
        res_txns = get_transactions(customer_id="CUST001", account_id="ACC002")
        self.assertIsNone(res_txns)

        res_investigate = investigate_transactions(customer_id="CUST001", account_id="ACC002")
        self.assertFalse(res_investigate["verified"])
        self.assertEqual(res_investigate["error_code"], "UNAUTHORIZED_ACCOUNT_ACCESS")

    def test_13_investigate_transactions_pipeline(self):
        result = investigate_transactions(
            customer_id="CUST001",
            time_period="september",
            comparison_period="august",
            analysis_type="comparison"
        )
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["verified"])
        self.assertEqual(result["data"]["summary"]["total_spending"], 131970.00)
        self.assertIn("period_comparison", result["data"])
        self.assertEqual(result["data"]["period_comparison"]["difference"], 91220.00)
        self.assertTrue(len(result["data"]["top_expenses"]) > 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
