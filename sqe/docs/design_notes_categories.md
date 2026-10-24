# Test Design Notes: expense_tracker.categories

**Author:** Abdul-Rehman (24F-3056)  
**Module:** `expense_tracker/categories.py`  
**Test File:** `sqe/tests/test_24F3056_categories.py`  
**Status:** 12 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Theme Integrity
`categories.py` manages UI color variables and print RGB tuples across the application:
1. `CATEGORY_COLOR_VAR`: Maps category names to CSS variables (`--cat-food`, `--cat-bills`, etc.).
2. `CATEGORY_PRINT_RGB`: Maps category names to RGB 3-tuples for PDF report drawing.
3. `category_color(category)`: Resolves CSS `var(--...)` syntax with safe fallback.

---

## 2. Test Design Techniques Applied

### A. Equivalence Partitioning & Fallback Handling
* Canonical categories (`Food`, `Transportation`, `Entertainment`, `Shopping`, `Bills`, `Other`) resolve to their dedicated CSS variables.
* Unrecognized strings (e.g. `"Cryptocurrency"`), empty strings, and non-string types safely return the fallback `var(--cat-other)`.
* Case-sensitivity check confirms lowercase `"food"` does not match `"Food"`, correctly falling back to `"Other"`.

### B. System Palette Parity & Contract Verification
* **Key Parity:** Verified that `CATEGORY_COLOR_VAR.keys()` strictly equals `CATEGORY_PRINT_RGB.keys()`.
* **RGB Tuple Boundaries:** Validates every RGB value is an integer between $0$ and $255$.
* **Uniqueness:** Validates each canonical category resolves to a unique, distinct CSS variable.
