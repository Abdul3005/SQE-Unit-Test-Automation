# Test Design Notes: expense_tracker.exports.csvutil

**Author:** Junaid Haider (24F-3122)  
**Module:** `expense_tracker/exports/csvutil.py`  
**Test File:** `sqe/tests/test_24F3122_csvutil.py`  
**Status:** 22 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Security Purpose
`csvutil.py` provides centralized, secure CSV streaming for the entire application. It prevents **CSV Formula Injection (CWE-1236)** while generating RFC 4180 compliant streams with UTF-8 Byte Order Marks (BOM).

---

## 2. Test Design Techniques Applied

### A. Security Injection & Neutralization Testing
* **Formula Prefixes:** Tests all 6 dangerous prefixes defined in `_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")`. Any cell beginning with these prefixes is neutralized by prepending a single quote (`'`).
* **Signed Numbers Exception (BVA / ECP):**
  * Legitimate numerical data such as `"+45.50"`, `"-120.00"`, and percentages `"+8%"`, `"-12.5%"` match `_SIGNED_NUMBER` regex and are **NOT** neutralized.
  * Formula commands like `"+cmd|' /C calc'!A0"` do not match the number regex and are successfully neutralized.

### B. Stream Encoding & Standards Compliance
* **UTF-8 BOM:** Verifies output byte sequence begins with `b"\xef\xbb\xbf"`, ensuring Microsoft Excel correctly parses UTF-8 characters without encoding corruption.
* **CRLF Terminators:** Validates rows terminate with standard `\r\n` (CRLF) characters per RFC 4180.
* **Unicode Preservation:** Confirms accented characters (`"Café"`, `"München"`) are preserved across the serialization pipeline.

---

## 3. Data-Driven Testing (Task 3 Requirement)
External CSV data file `sqe/tests/data/test_24F3122_data.csv` is loaded via `csv.DictReader` and parameterized through `@pytest.mark.parametrize` to execute 8 distinct formula injection, whitespace, and boundary cases (`JH-CSV-DD-01` through `JH-CSV-DD-08`), with each case validated under `@pytest.mark.security`.
