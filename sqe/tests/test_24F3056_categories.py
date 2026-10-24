"""Automated Unit Tests for expense_tracker.categories

Author: Abdul-Rehman (Roll: 24F-3056)
File: test_24F3056_categories.py
Assignment: SQE Assignment 3
Scope:
  - Function-level tests for category_color
  - Module/Class-level tests for CATEGORY_COLOR_VAR, CATEGORY_PRINT_RGB, and palette parity
"""

from __future__ import annotations

import pytest

from expense_tracker.categories import (
    CATEGORY_COLOR_VAR,
    CATEGORY_PRINT_RGB,
    category_color,
)
from expense_tracker.models import CATEGORIES

# ============================================================================
# FUNCTION-LEVEL TESTS: category_color (Abdul-Rehman)
# Parameterized test covering 6 distinct category color resolution cases
# ============================================================================


@pytest.mark.categories
@pytest.mark.parametrize(
    "pairs",
    [
        pytest.param([("Food", "var(--cat-food)"), ("Bills", "var(--cat-bills)")], id="AR-CAT-01"),
        pytest.param([("Transportation", "var(--cat-transportation)"), ("Shopping", "var(--cat-shopping)")], id="AR-CAT-02"),
        pytest.param([("Entertainment", "var(--cat-entertainment)"), ("Other", "var(--cat-other)")], id="AR-CAT-03"),
        pytest.param([("Cryptocurrency", "var(--cat-other)"), ("Luxury", "var(--cat-other)")], id="AR-CAT-04"),
        pytest.param([("", "var(--cat-other)")], marks=pytest.mark.bva, id="AR-CAT-05"),
        pytest.param([("food", "var(--cat-other)"), ("BILLS", "var(--cat-other)")], id="AR-CAT-06"),
    ],
)
def test_category_color(pairs):
    """AR-CAT-01..06: Resolves CSS variables for canonical categories and fallback for invalid/case-mismatched."""
    for cat_input, expected_var in pairs:
        assert category_color(cat_input) == expected_var


# ============================================================================
# MODULE / CLASS-LEVEL TESTS: Category System Constants & Mapping (Abdul-Rehman)
# 6 distinct tests
# ============================================================================


@pytest.mark.categories
def test_category_color_var_keys_match_canonical_categories():
    """AR-CAT-CLS-01: CATEGORY_COLOR_VAR dictionary contains exactly the 6 canonical categories."""
    assert set(CATEGORY_COLOR_VAR.keys()) == set(CATEGORIES)
    assert len(CATEGORY_COLOR_VAR) == 6


@pytest.mark.categories
def test_category_print_rgb_keys_match_canonical_categories():
    """AR-CAT-CLS-02: CATEGORY_PRINT_RGB dictionary contains exactly the 6 canonical categories."""
    assert set(CATEGORY_PRINT_RGB.keys()) == set(CATEGORIES)
    assert len(CATEGORY_PRINT_RGB) == 6


@pytest.mark.categories
def test_category_color_and_rgb_parity():
    """AR-CAT-CLS-03: Keys of CATEGORY_COLOR_VAR and CATEGORY_PRINT_RGB are identical."""
    assert CATEGORY_COLOR_VAR.keys() == CATEGORY_PRINT_RGB.keys()


@pytest.mark.categories
def test_category_print_rgb_tuple_structure():
    """AR-CAT-CLS-04: Every entry in CATEGORY_PRINT_RGB is a 3-tuple with values between 0 and 255."""
    for cat, rgb in CATEGORY_PRINT_RGB.items():
        assert isinstance(rgb, tuple)
        assert len(rgb) == 3
        for val in rgb:
            assert isinstance(val, int)
            assert 0 <= val <= 255


@pytest.mark.categories
def test_all_canonical_categories_resolve_unique_css_vars():
    """AR-CAT-CLS-05: Each canonical category resolves to a distinct, unique CSS variable name."""
    resolved_vars = [category_color(c) for c in CATEGORIES]
    assert len(resolved_vars) == len(set(resolved_vars))


@pytest.mark.categories
def test_category_color_non_string_types():
    """AR-CAT-CLS-06: Robustness: non-string inputs (None, int) safely return fallback var."""
    assert category_color(None) == "var(--cat-other)"  # type: ignore
    assert category_color(123) == "var(--cat-other)"  # type: ignore
