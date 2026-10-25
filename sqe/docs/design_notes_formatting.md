# Test Design Notes: expense_tracker.formatting

**Author:** Junaid Haider (24F-3122)  
**Module:** `expense_tracker/formatting.py`  
**Test File:** `sqe/tests/test_24F3122_formatting.py`  
**Status:** 27 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Formatting Functions
`formatting.py` provides presentation formatting across the user interface:
1. `format_currency(amount)`: Formats numbers as `"$X,XXX.XX"`.
2. `format_date(iso_date)`: Converts ISO strings (`"2026-10-15"`) to `"Oct 15, 2026"`.
3. `format_relative(moment, now)`: Computes relative time phrases (`"just now"`, `"X min ago"`, `"X hr ago"`, `"in X min"`, `"never"`).
4. `format_local(moment)`: Converts UTC datetimes to system local time with stripped leading zeros on the hour.

---

## 2. Test Design Techniques Applied

### A. Boundary Value Analysis (BVA) for Relative Time
* **0 to 44 seconds:** Evaluates to `"just now"` (past) or `"in a moment"` (future).
* **Exact 45 seconds:** Boundary transition to `"1 min ago"`.
* **3599 seconds:** Evaluates to `"60 min ago"`.
* **Exact 3600 seconds:** Boundary transition to `"1 hr ago"`.
* **Beyond 30 days:** Falls back to absolute date formatting using `format_date`.

### B. Defensive Handling & Internationalization
* `format_relative(None)` returns `"never"`.
* `format_local(None)` returns empty string `""`.
* Day pluralization logic correctly generates `"1 day ago"` vs `"3 days ago"`.
* Validates leap year dates (`"2024-02-29"` accepted) and rejects invalid formats (`"15-10-2026"` raises `ValueError`).
