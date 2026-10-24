"""Automated Unit Tests for expense_tracker.models

Author: Abdul-Rehman (Roll: 24F-3056)
File: test_24F3056_models.py
Assignment: SQE Assignment 3
Scope:
  - Function-level tests for validate_expense (ECP, BVA, Error handling)
  - Data-driven tests loading sqe/tests/data/test_24F3056_expenses_data.csv
  - Module/Class-level tests for Expense dataclass, Filters, and module constants
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from expense_tracker.models import (
    CATEGORIES,
    SORT_OPTIONS,
    Expense,
    Filters,
    validate_expense,
)

# ============================================================================
# FUNCTION-LEVEL TESTS: validate_expense (Abdul-Rehman)
# 6 distinct, source-grounded function tests
# ============================================================================


@pytest.mark.models
@pytest.mark.ecp
def test_validate_expense_valid_typical():
    """AR-MOD-01: Valid typical expense returns empty errors dict and parsed float."""
    errors, amount = validate_expense("Groceries", "45.50", "Food", "2026-10-15")
    assert errors == {}
    assert amount == 45.50


@pytest.mark.models
@pytest.mark.bva
def test_validate_expense_description_boundary_120_chars():
    """AR-MOD-02: Description of exact maximum length (120 characters) is valid."""
    desc_120 = "A" * 120
    errors, amount = validate_expense(desc_120, "10.00", "Bills", "2026-10-15")
    assert "description" not in errors
    assert amount == 10.00


@pytest.mark.models
@pytest.mark.bva
def test_validate_expense_description_boundary_121_chars():
    """AR-MOD-03: Description exceeding 120 chars (121 characters) is rejected."""
    desc_121 = "A" * 121
    errors, amount = validate_expense(desc_121, "10.00", "Bills", "2026-10-15")
    assert "description" in errors
    assert errors["description"] == "Keep it under 120 characters."


@pytest.mark.models
@pytest.mark.bva
def test_validate_expense_amount_lower_boundary_one_cent():
    """AR-MOD-04: Minimum positive amount ($0.01) is accepted."""
    errors, amount = validate_expense("Penny item", "0.01", "Other", "2026-10-15")
    assert "amount" not in errors
    assert amount == 0.01


@pytest.mark.models
@pytest.mark.bva
def test_validate_expense_amount_upper_boundaries():
    """AR-MOD-05: Upper amount boundary checks ($1,000,000 accepted, $1,000,000.01 rejected)."""
    # Exactly 1,000,000 is allowed
    errors_max, amt_max = validate_expense("Max Amount", "1000000", "Other", "2026-10-15")
    assert "amount" not in errors_max
    assert amt_max == 1000000.0

    # 1,000,000.01 exceeds upper limit
    errors_over, _ = validate_expense("Over Max", "1000000.01", "Other", "2026-10-15")
    assert "amount" in errors_over
    assert errors_over["amount"] == "That amount looks too large."


@pytest.mark.models
@pytest.mark.ecp
def test_validate_expense_date_invalid_calendar():
    """AR-MOD-06: Malformed or non-existent calendar date (e.g. Feb 30) is rejected."""
    errors, _ = validate_expense("Dinner", "30.00", "Food", "2026-02-30")
    assert "date" in errors
    assert errors["date"] == "Enter a valid date."


# ============================================================================
# DATA-DRIVEN TEST: External CSV Loading (Task 3 Requirement)
# Loads sqe/tests/data/test_24F3056_expenses_data.csv using csv.DictReader
# ============================================================================

CSV_PATH = Path(__file__).parent / "data" / "test_24F3056_expenses_data.csv"


def load_csv_cases():
    cases = []
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(row)
    return cases


@pytest.mark.models
@pytest.mark.data_driven
@pytest.mark.parametrize("case", load_csv_cases(), ids=lambda c: c["test_id"])
def test_validate_expense_data_driven_csv(case):
    """Data-driven test loading external CSV rows for comprehensive validation."""
    desc = case["description"]
    amt = case["amount"]
    cat = case["category"]
    dt = case["date"]
    expected_valid = case["expected_valid"].lower() == "true"

    errors, parsed_amt = validate_expense(desc, amt, cat, dt)

    if expected_valid:
        assert errors == {}
        assert parsed_amt == float(amt)
    else:
        err_field = case["error_field"]
        assert err_field in errors
        assert errors[err_field] == case["error_message"]


# ============================================================================
# MODULE / CLASS-LEVEL TESTS: Models & Dataclasses (Abdul-Rehman)
# 6 distinct tests targeting Expense, Filters, and Module Constants
# ============================================================================


@pytest.mark.models
def test_expense_dataclass_direct_instantiation():
    """AR-MOD-CLS-01: Direct instantiation of Expense dataclass retains field integrity."""
    exp = Expense(
        id=101,
        description="Monitor Stand",
        amount=29.99,
        category="Shopping",
        date="2026-10-18",
        created_at="2026-10-18T10:00:00",
    )
    assert exp.id == 101
    assert exp.description == "Monitor Stand"
    assert exp.amount == 29.99
    assert exp.category == "Shopping"
    assert exp.date == "2026-10-18"
    assert exp.created_at == "2026-10-18T10:00:00"


@pytest.mark.models
def test_expense_from_row_mapping():
    """AR-MOD-CLS-02: Expense.from_row correctly maps sqlite3-like dictionary row."""
    fake_row = {
        "id": 42,
        "description": "Subway Ride",
        "amount": 2.75,
        "category": "Transportation",
        "date": "2026-10-19",
        "created_at": "2026-10-19T08:30:00",
    }
    exp = Expense.from_row(fake_row)
    assert exp.id == 42
    assert exp.description == "Subway Ride"
    assert exp.amount == 2.75
    assert exp.category == "Transportation"


@pytest.mark.models
def test_filters_dataclass_defaults():
    """AR-MOD-CLS-03: Filters dataclass initializes with default query values."""
    f = Filters()
    assert f.search == ""
    assert f.category == "All"
    assert f.date_from == ""
    assert f.date_to == ""
    assert f.sort == "date-desc"


@pytest.mark.models
def test_categories_constant_integrity():
    """AR-MOD-CLS-04: CATEGORIES constant contains exactly the 6 canonical categories."""
    expected = ["Food", "Transportation", "Entertainment", "Shopping", "Bills", "Other"]
    assert CATEGORIES == expected
    assert len(CATEGORIES) == 6


@pytest.mark.models
def test_sort_options_constant_mapping():
    """AR-MOD-CLS-05: SORT_OPTIONS dictionary maps all 4 supported sort keys to SQL clauses."""
    assert "date-desc" in SORT_OPTIONS
    assert "date-asc" in SORT_OPTIONS
    assert "amount-desc" in SORT_OPTIONS
    assert "amount-asc" in SORT_OPTIONS
    assert SORT_OPTIONS["date-desc"] == "date DESC, created_at DESC"
    assert SORT_OPTIONS["amount-asc"] == "amount ASC"


@pytest.mark.models
def test_validation_and_dataclass_pipeline():
    """AR-MOD-CLS-06: End-to-end pipeline: validating raw strings then instantiating Expense."""
    raw_desc = "  Coffee Bean  "
    raw_amt = " 14.50 "
    raw_cat = "Food"
    raw_dt = "2026-10-19"

    errors, parsed_amt = validate_expense(raw_desc, raw_amt, raw_cat, raw_dt)
    assert errors == {}
    assert parsed_amt is not None

    exp = Expense(
        id=1,
        description=raw_desc.strip(),
        amount=parsed_amt,
        category=raw_cat,
        date=raw_dt,
        created_at="2026-10-19T12:00:00",
    )
    assert exp.description == "Coffee Bean"
    assert exp.amount == 14.50
