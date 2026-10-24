# Test Design Notes: expense_tracker.models

**Author:** Abdul-Rehman (24F-3056)  
**Module:** `expense_tracker/models.py`  
**Test File:** `sqe/tests/test_24F3056_models.py`  
**Status:** 20 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Architectural Role
`models.py` contains the core business validation logic and data transfer definitions for the Expense Tracker. While database helpers communicate with SQLite, `validate_expense` and the dataclasses `Expense` and `Filters` are entirely pure in-memory constructs, allowing complete unit test isolation.

---

## 2. Test Design Techniques Applied

### A. Equivalence Class Partitioning (ECP)
* **Valid Inputs:** Alphanumeric description, positive float amount, category in canonical list `["Food", "Transportation", "Entertainment", "Shopping", "Bills", "Other"]`, and ISO date format `YYYY-MM-DD`.
* **Invalid Inputs:**
  * Empty or whitespace-only description -> Rejection: `"Description is required."`
  * Non-numeric amount string (`"abc"`, `"$25"`) -> Rejection: `"Enter a valid amount."`
  * Category not in `CATEGORIES` list -> Rejection: `"Choose a valid category."`
  * Malformed or non-existent calendar date (`"2026-02-30"`) -> Rejection: `"Enter a valid date."`

### B. Boundary Value Analysis (BVA)
* **Description Length:**
  * Bound: 120 characters max (`len(description) > 120`).
  * On-boundary ($120$ chars): Valid (`AR-MOD-02`).
  * Off-boundary ($121$ chars): Invalid, error `"Keep it under 120 characters."` (`AR-MOD-03`).
* **Amount Boundaries:**
  * Lower bound: $0$ and negative rejected (`"Amount must be greater than $0."`).
  * Smallest valid amount: $0.01$ accepted (`AR-MOD-04`).
  * Upper bound: $1,000,000.00$ accepted (`AR-MOD-05`).
  * Off-boundary: $1,000,000.01$ rejected with `"That amount looks too large."` (`AR-MOD-05`).

---

## 3. Data-Driven Testing (Task 3 Requirement)
External CSV data file `tests/data/test_expenses_data.csv` is loaded via `csv.DictReader` and parameterized through `@pytest.mark.parametrize` to execute 8 distinct boundary and error cases (`CSV-01` through `CSV-08`).

---

## 4. Module & Class-Level Integration
* Validates `Expense` dataclass instantiation and field preservation.
* Validates `Expense.from_row` sqlite3 dict-like row mapping.
* Validates `Filters` dataclass default query state (`search=""`, `category="All"`, `sort="date-desc"`).
* Verifies immutability and exact membership of `CATEGORIES` (6 canonical items) and `SORT_OPTIONS` (4 sort keys).
