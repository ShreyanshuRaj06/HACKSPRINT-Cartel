# AI-Powered Retail Banking Assistant - Mock Backend API

> **TCS Techsprint Hackathon** | Backend Mock Banking API

A deterministic, synthetic mock banking backend designed to serve as the authoritative financial source of truth for the AI-Powered Retail Banking Customer Query Assistant.

---

## 🎯 Architecture & Design Principle

```
Customer ──> Streamlit UI ──> Gemini (NLU / Intent) ──> investigate_transactions()
                                                               │
                                                               ▼
                                                    transaction_service.get_transactions()
                                                               │
                                                               ▼
                                                      TransactionAnalyzer
                                                               │
                                                               ▼
Customer <── Streamlit UI <── Gemini (Explanation) <── Verified Structured Result
```

- **Gemini Responsibility:** Natural language understanding, intent recognition, parameter extraction, and conversational explanation of verified financial results. *(Gemini NEVER performs financial math).*
- **Backend Responsibility:** Data retrieval, customer session scoping, and **100% authoritative deterministic financial calculations** (sums, percentages, category breakdowns, top expenses, period comparisons).

---

## 📁 Project Structure

```text
mock-banking-api/
├── backend/
│   ├── app.py                     # Flask entrypoint & route registration
│   ├── data/                      # Synthetic Mock Datasets (JSON)
│   │   ├── accounts.json
│   │   ├── customers.json
│   │   ├── loans.json
│   │   └── transactions.json
│   ├── routes/                    # API Route Handlers
│   │   ├── __init__.py
│   │   ├── accounts.py
│   │   ├── customers.py
│   │   ├── loans.py
│   │   └── transactions.py
│   ├── services/                  # Business Logic & Calculations
│   │   ├── __init__.py
│   │   ├── account_service.py     # Account & balance queries
│   │   ├── customer_service.py    # Customer profiling
│   │   ├── loan_service.py        # Loan information (read-only)
│   │   ├── transaction_service.py # Customer-scoped transaction queries
│   │   ├── transaction_analyzer.py# Pure-Python deterministic calculations
│   │   └── investigation_service.py# High-level pipeline entrypoint
│   └── tests/
│       └── test_backend.py        # 13 automated unit & integration tests
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart

### 1. Setup Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Backend API
```bash
cd backend
python app.py
```
The server will start at `http://127.0.0.1:5000`.

### 3. Run Automated Verification Tests
```bash
python backend/tests/test_backend.py
```

---

## 🔌 Available Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status & endpoint directory |
| `GET` | `/api/customers` | List all synthetic customers |
| `GET` | `/api/customer/<id>` | Customer details |
| `GET` | `/api/accounts` | Accounts for session customer (`X-Customer-Id`) |
| `GET` | `/api/account/<id>/balance` | Account balance |
| `GET` | `/api/loans` | Customer loans / product info |
| `GET` | `/api/transactions` | Filtered transaction history |
| `POST / GET` | `/api/transactions/investigate` | **Flagship Capability:** Runs transaction investigation pipeline |

---

## 🔍 Flagship Capability: Transaction Investigation

### Pipeline: `investigate_transactions()`
When a user asks questions such as:
- *"Why did I spend so much this month?"*
- *"Where did most of my money go?"*
- *"Did I spend more this month than last month?"*
- *"How much did I spend on food?"*
- *"Show me my biggest expenses."*

Gemini extracts the parameters and calls `investigate_transactions()`. The backend executes:
1. **Customer Scoping:** Validates customer session and restricts access to owned accounts only.
2. **Data Retrieval:** `transaction_service.get_transactions()` retrieves verified records for target and comparison periods.
3. **Deterministic Math:** `TransactionAnalyzer` computes spending totals, category breakdowns, differences, percentage changes, and top expenses.
4. **Structured Output:** Returns a JSON object with `"verified": true`.

#### Example Investigation Output:
```json
{
  "status": "success",
  "verified": true,
  "investigation_meta": {
    "customer_id": "CUST001",
    "customer_name": "Aarav Sharma",
    "account_id": "ALL_ACCOUNTS",
    "analysis_type": "comparison",
    "target_period": { "start_date": "2026-09-01", "end_date": "2026-09-30" },
    "comparison_period": { "start_date": "2026-08-01", "end_date": "2026-08-31" }
  },
  "data": {
    "verified": true,
    "currency": "INR",
    "summary": {
      "total_spending": 131970.00,
      "total_income": 110000.00,
      "net_cash_flow": -21970.00
    },
    "period_comparison": {
      "current_period_spending": 131970.00,
      "comparison_period_spending": 40750.00,
      "difference": 91220.00,
      "percentage_change": 223.85,
      "has_increased": true
    },
    "top_expenses": [
      { "description": "Apple Store - Smartwatch", "amount": 38900.00, "category": "shopping" },
      { "description": "Taj Hotels Goa Booking", "amount": 32000.00, "category": "travel" },
      { "description": "Apartment Rent Payment", "amount": 25000.00, "category": "housing" }
    ]
  }
}
```

---

## 🔒 Security & MVP Boundaries
1. **Synthetic Data Only:** Contains no real banking or customer data.
2. **Read-Only:** No funds transfer, payment processing, or account modifications.
3. **Session Scoping:** Enforces strict boundary checks to prevent cross-customer data leakage.
