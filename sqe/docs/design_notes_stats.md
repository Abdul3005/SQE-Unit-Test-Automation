# Test Design Notes: expense_tracker.stats

**Author:** Abdul-Rehman (24F-3056)  
**Module:** `expense_tracker/stats.py`  
**Test File:** `sqe/tests/test_24F3056_stats.py`  
**Status:** 30 Tests Implemented & Verified (100% Passed)

---

## 1. Scope & Mathematical Functions
`stats.py` calculates statistical summaries and geometric coordinates for SVG charts:
1. `total_of(expenses)`: Floating point sum of expense amounts.
2. `expenses_in_month(expenses, year, month)`: Filters transactions for a specific month.
3. `category_breakdown(expenses)`: Groups expenses by category, sorts descending, computes percentages, and determines SVG donut dash offsets.
4. `monthly_trend(expenses, months_back, chart_height)`: Generates 6-month rolling trend bars, scales heights, and clamps zero-spend bars.

---

## 2. Test Design Techniques Applied

### A. Boundary Value Analysis (BVA) & Extremes
* **Empty inputs:** `total_of([])` returns `0`; `expenses_in_month([])` returns `[]`; `category_breakdown([])` returns `[]` without triggering `ZeroDivisionError`.
* **Calendar month boundaries:** Transactions on the 1st day (`2026-10-01`) and the last day (`2026-10-31`) are correctly included.
* **Rolling Year Wrap:** In `monthly_trend`, bucketing backward from January rolls into December of the previous calendar year while decrementing the year counter.
* **Bar height clamping:** Months with zero transactions clamp to a minimum bar height of `3.0` px; maximum month scales to `chart_height - 24` px (`108.0` px for default `132`).

### B. Geometry & Dataclass Contracts
* Verified SVG Donut constants:
  $$\text{DONUT\_RADIUS} = \frac{200 - 28}{2} = 86.0$$
  $$\text{DONUT\_CIRCUMFERENCE} = 2 \times \pi \times 86 \approx 540.3539$$
* Verified cumulative negative `dash_offset` calculation for SVG multi-arc rendering.
