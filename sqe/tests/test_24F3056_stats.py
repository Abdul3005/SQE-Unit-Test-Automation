"""Automated Unit Tests for expense_tracker.stats

Author: Abdul-Rehman (Roll: 24F-3056)
File: test_24F3056_stats.py
Assignment: SQE Assignment 3
Scope:
  - Function-level tests for total_of, expenses_in_month, category_breakdown, monthly_trend
  - Module/Class-level tests for CategoryTotal, MonthTotal, and Donut SVG geometry constants
"""

from __future__ import annotations

import math
from datetime import date

import pytest

from expense_tracker.models import CATEGORIES, Expense
from expense_tracker.stats import (
    DONUT_CIRCUMFERENCE,
    DONUT_RADIUS,
    DONUT_SIZE,
    DONUT_STROKE,
    CategoryTotal,
    MonthTotal,
    category_breakdown,
    expenses_in_month,
    monthly_trend,
    total_of,
)


def make_test_expense(id_: int, amount: float, category: str = "Food", expense_date: str = "2026-10-15") -> Expense:
    return Expense(
        id=id_,
        description=f"Item {id_}",
        amount=amount,
        category=category,
        date=expense_date,
        created_at="2026-10-15T12:00:00",
    )


# ============================================================================
# FUNCTION-LEVEL TESTS: total_of (Abdul-Rehman)
# 6 distinct tests
# ============================================================================


@pytest.mark.stats
def test_total_of_multi_items_sum():
    """AR-STA-01: Summing multiple items with fractional float cents."""
    expenses = [
        make_test_expense(1, 10.25),
        make_test_expense(2, 5.50),
        make_test_expense(3, 4.25),
    ]
    assert total_of(expenses) == 20.00


@pytest.mark.stats
@pytest.mark.bva
def test_total_of_empty_list():
    """AR-STA-02: Empty list returns zero float/int without error."""
    assert total_of([]) == 0


@pytest.mark.stats
def test_total_of_single_item():
    """AR-STA-03: Single item list returns the exact amount of that item."""
    assert total_of([make_test_expense(1, 99.95)]) == 99.95


@pytest.mark.stats
def test_total_of_large_numbers():
    """AR-STA-04: Summing large amounts preserves floating point precision."""
    expenses = [
        make_test_expense(1, 500000.0),
        make_test_expense(2, 500000.0),
    ]
    assert total_of(expenses) == 1000000.0


@pytest.mark.stats
def test_total_of_small_cent_increments():
    """AR-STA-05: Summing small fractions (0.01, 0.02) computes correctly."""
    expenses = [
        make_test_expense(1, 0.01),
        make_test_expense(2, 0.02),
    ]
    assert round(total_of(expenses), 2) == 0.03


@pytest.mark.stats
def test_total_of_all_zero_amounts():
    """AR-STA-06: Summing zero amounts returns zero."""
    expenses = [
        make_test_expense(1, 0.0),
        make_test_expense(2, 0.0),
    ]
    assert total_of(expenses) == 0.0


# ============================================================================
# FUNCTION-LEVEL TESTS: expenses_in_month (Abdul-Rehman)
# 6 distinct tests
# ============================================================================


@pytest.mark.stats
def test_expenses_in_month_matching_month():
    """AR-STA-07: Filters expenses matching target year and month."""
    expenses = [
        make_test_expense(1, 10.0, "Food", "2026-10-05"),
        make_test_expense(2, 20.0, "Food", "2026-10-25"),
        make_test_expense(3, 30.0, "Food", "2026-09-30"),
    ]
    result = expenses_in_month(expenses, 2026, 10)
    assert [e.id for e in result] == [1, 2]


@pytest.mark.stats
@pytest.mark.bva
def test_expenses_in_month_first_day_boundary():
    """AR-STA-08: Expense occurring on the first day of the month is included."""
    expenses = [make_test_expense(1, 15.0, "Bills", "2026-10-01")]
    result = expenses_in_month(expenses, 2026, 10)
    assert len(result) == 1
    assert result[0].id == 1


@pytest.mark.stats
@pytest.mark.bva
def test_expenses_in_month_last_day_boundary():
    """AR-STA-09: Expense occurring on the last day of the month is included."""
    expenses = [make_test_expense(1, 15.0, "Bills", "2026-10-31")]
    result = expenses_in_month(expenses, 2026, 10)
    assert len(result) == 1
    assert result[0].id == 1


@pytest.mark.stats
def test_expenses_in_month_different_year_same_month():
    """AR-STA-10: Excludes expenses with matching month number but different year."""
    expenses = [
        make_test_expense(1, 10.0, "Food", "2025-10-15"),
        make_test_expense(2, 20.0, "Food", "2026-10-15"),
    ]
    result = expenses_in_month(expenses, 2026, 10)
    assert len(result) == 1
    assert result[0].id == 2


@pytest.mark.stats
def test_expenses_in_month_different_month_same_year():
    """AR-STA-11: Excludes expenses with matching year but adjacent month."""
    expenses = [
        make_test_expense(1, 10.0, "Food", "2026-09-30"),
        make_test_expense(2, 20.0, "Food", "2026-11-01"),
    ]
    result = expenses_in_month(expenses, 2026, 10)
    assert result == []


@pytest.mark.stats
def test_expenses_in_month_empty_input():
    """AR-STA-12: Empty input list returns empty result."""
    assert expenses_in_month([], 2026, 10) == []


# ============================================================================
# FUNCTION-LEVEL TESTS: category_breakdown (Abdul-Rehman)
# 6 distinct tests
# ============================================================================


@pytest.mark.stats
def test_category_breakdown_single_category_100_percent():
    """AR-STA-13: Single category receives 100.0% and exact circumference dash array."""
    expenses = [make_test_expense(1, 50.0, "Shopping")]
    breakdown = category_breakdown(expenses)
    assert len(breakdown) == 1
    item = breakdown[0]
    assert item.category == "Shopping"
    assert item.percent == 100.0
    assert item.dash_offset == 0.0
    assert item.dash_array == f"{DONUT_CIRCUMFERENCE:.4f} {DONUT_CIRCUMFERENCE:.4f}"


@pytest.mark.stats
def test_category_breakdown_descending_sort_order():
    """AR-STA-14: Breakdown entries are sorted strictly in descending order of total spend."""
    expenses = [
        make_test_expense(1, 10.0, "Food"),
        make_test_expense(2, 90.0, "Bills"),
        make_test_expense(3, 40.0, "Entertainment"),
    ]
    breakdown = category_breakdown(expenses)
    assert [b.category for b in breakdown] == ["Bills", "Entertainment", "Food"]
    assert breakdown[0].total == 90.0
    assert breakdown[1].total == 40.0
    assert breakdown[2].total == 10.0


@pytest.mark.stats
def test_category_breakdown_excludes_zero_spend_categories():
    """AR-STA-15: Categories with zero transactions are not present in breakdown."""
    expenses = [make_test_expense(1, 25.0, "Food")]
    breakdown = category_breakdown(expenses)
    categories_present = [b.category for b in breakdown]
    assert "Food" in categories_present
    assert "Transportation" not in categories_present
    assert len(breakdown) == 1


@pytest.mark.stats
def test_category_breakdown_empty_input():
    """AR-STA-16: Empty input returns empty list without ZeroDivisionError."""
    assert category_breakdown([]) == []


@pytest.mark.stats
def test_category_breakdown_equal_amounts_equal_percentages():
    """AR-STA-17: Categories with identical spending split percentage equally."""
    expenses = [
        make_test_expense(1, 50.0, "Food"),
        make_test_expense(2, 50.0, "Bills"),
    ]
    breakdown = category_breakdown(expenses)
    assert len(breakdown) == 2
    assert breakdown[0].percent == 50.0
    assert breakdown[1].percent == 50.0


@pytest.mark.stats
def test_category_breakdown_cumulative_dash_offset():
    """AR-STA-18: Multiple categories accumulate negative dash offsets for SVG rendering."""
    expenses = [
        make_test_expense(1, 60.0, "Bills"),
        make_test_expense(2, 40.0, "Food"),
    ]
    breakdown = category_breakdown(expenses)
    assert breakdown[0].dash_offset == 0.0
    expected_offset = -0.60 * DONUT_CIRCUMFERENCE
    assert math.isclose(breakdown[1].dash_offset, expected_offset, rel_tol=1e-4)


# ============================================================================
# FUNCTION-LEVEL TESTS: monthly_trend (Abdul-Rehman)
# 6 distinct tests
# ============================================================================


@pytest.mark.stats
def test_monthly_trend_default_six_buckets():
    """AR-STA-19: Default call produces exactly 6 monthly trend buckets."""
    trend = monthly_trend([])
    assert len(trend) == 6
    today = date.today()
    assert trend[-1].year == today.year
    assert trend[-1].month == today.month


@pytest.mark.stats
def test_monthly_trend_year_rollover():
    """AR-STA-20: Bucketing rolls over year boundary backwards (e.g. 12 months back)."""
    trend = monthly_trend([], months_back=12)
    assert len(trend) == 12
    # Verify months are in sequential 1..12 calendar cycle
    months = [b.month for b in trend]
    for i in range(len(months) - 1):
        expected_next = 1 if months[i] == 12 else months[i] + 1
        assert months[i + 1] == expected_next


@pytest.mark.stats
def test_monthly_trend_english_abbreviations():
    """AR-STA-21: Labels are valid 3-letter English month abbreviations."""
    trend = monthly_trend([])
    valid_labels = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}
    for bucket in trend:
        assert bucket.label in valid_labels


@pytest.mark.stats
def test_monthly_trend_max_bar_height():
    """AR-STA-22: Month with maximum spend receives full available height (chart_height - 24)."""
    today = date.today()
    expenses = [make_test_expense(1, 100.0, "Food", today.isoformat())]
    trend = monthly_trend(expenses, chart_height=132)
    current_bucket = trend[-1]
    assert current_bucket.bar_height == 108.0  # 132 - 24


@pytest.mark.stats
def test_monthly_trend_zero_spend_minimum_height():
    """AR-STA-23: Month with zero spend is clamped to minimum bar height of 3.0."""
    trend = monthly_trend([], chart_height=132)
    for bucket in trend:
        assert bucket.total == 0.0
        assert bucket.bar_height == 3.0


@pytest.mark.stats
def test_monthly_trend_custom_months_count():
    """AR-STA-24: Custom months_back parameter produces exact number of buckets."""
    trend_3 = monthly_trend([], months_back=3)
    assert len(trend_3) == 3
    trend_9 = monthly_trend([], months_back=9)
    assert len(trend_9) == 9


# ============================================================================
# MODULE / CLASS-LEVEL TESTS: Stats Module Constants & Dataclasses (Abdul-Rehman)
# 6 distinct tests targeting CategoryTotal, MonthTotal, and Donut Geometry
# ============================================================================


@pytest.mark.stats
def test_category_total_dataclass_defaults():
    """AR-STA-CLS-01: CategoryTotal dataclass defaults dash_array and dash_offset."""
    ct = CategoryTotal(category="Food", total=50.0, count=2, percent=25.0)
    assert ct.dash_array == ""
    assert ct.dash_offset == 0.0


@pytest.mark.stats
def test_month_total_dataclass_defaults():
    """AR-STA-CLS-02: MonthTotal dataclass initializes bar_height to 0.0."""
    mt = MonthTotal(year=2026, month=10, total=150.0, label="Oct")
    assert mt.bar_height == 0.0


@pytest.mark.stats
def test_donut_geometry_constants():
    """AR-STA-CLS-03: Donut geometry dimensions adhere to layout design."""
    assert DONUT_SIZE == 200
    assert DONUT_STROKE == 28
    assert DONUT_RADIUS == (200 - 28) / 2
    assert DONUT_RADIUS == 86.0


@pytest.mark.stats
def test_donut_circumference_formula():
    """AR-STA-CLS-04: DONUT_CIRCUMFERENCE exactly equals 2 * pi * radius."""
    expected_c = 2 * math.pi * 86.0
    assert math.isclose(DONUT_CIRCUMFERENCE, expected_c, rel_tol=1e-9)


@pytest.mark.stats
def test_all_categories_in_breakdown_sum_to_100():
    """AR-STA-CLS-05: When all 6 categories have expenses, total percent sums to 100.0%."""
    expenses = [make_test_expense(i, 10.0, cat) for i, cat in enumerate(CATEGORIES, 1)]
    breakdown = category_breakdown(expenses)
    assert len(breakdown) == 6
    total_pct = sum(b.percent for b in breakdown)
    assert math.isclose(total_pct, 100.0, rel_tol=1e-4)


@pytest.mark.stats
def test_monthly_trend_chronological_ordering():
    """AR-STA-CLS-06: Buckets in monthly_trend are chronologically ordered from oldest to newest."""
    trend = monthly_trend([], months_back=6)
    dates = [date(b.year, b.month, 1) for b in trend]
    assert dates == sorted(dates)
