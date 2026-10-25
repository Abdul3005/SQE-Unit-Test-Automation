# Test Design Notes: expense_tracker.exports.options

**Author:** Junaid Haider (24F-3122)  
**Module:** `expense_tracker/exports/options.py`  
**Test File:** `sqe/tests/test_24F3122_options.py`  
**Status:** 17 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Export Validation
`options.py` parses and validates user query parameters for all export formats (CSV, JSON, PDF) and sanitizes user-provided filenames to prevent directory traversal and filesystem errors.

---

## 2. Test Design Techniques Applied

### A. Filename Sanitization & Security Testing
* **Extension Stripping:** Strips `.csv`, `.json`, `.pdf` case-insensitively so extensions are not duplicated when rendered.
* **Path Traversal & Unsafe Characters:** Replaces `< > : " / \ | ? *` with single dashes.
* **Consecutive Dash Normalization:** Collapses runs of dashes (`---` -> `-`).
* **Boundary Length Limit:** Truncates stems exceeding 80 characters (`FILENAME_MAX_LENGTH = 80`) and trims trailing punctuation.

### B. Query Option Parsing & Equivalence Partitioning
* **Default Values:** Empty input query defaults to `csv` format, all categories, and `date-desc` sorting.
* **Date Range Consistency:** Rejects requests where start date occurs after end date (`"End date must be on or after the start date."`).
* **Category Filtering:** Rejects unrecognized categories (`"Unknown category: Crypto"`).
* **Frozen Immutability:** Tests that `ExportOptions` dataclass is frozen and raises `AttributeError` upon attempted mutation.
