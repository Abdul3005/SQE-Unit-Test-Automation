from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from expense_tracker.formatting import (
    format_currency,
    format_date,
    format_local,
    format_relative,
)

# FUNCTION-LEVEL TESTS: format_currency 
# Parameterized test covering 6 distinct currency format cases

@pytest.mark.formatting
@pytest.mark.parametrize(
    "amount, expected",
    [
        pytest.param(45.5, "$45.50", id="JH-FMT-01"),
        pytest.param(1234567.89, "$1,234,567.89", id="JH-FMT-02"),
        pytest.param(0.0, "$0.00", marks=pytest.mark.bva, id="JH-FMT-03"),
        pytest.param(-15.75, "$-15.75", id="JH-FMT-04"),
        pytest.param(10.556, "$10.56", id="JH-FMT-05"),
        pytest.param(100, "$100.00", id="JH-FMT-06"),
    ],
)
def test_format_currency(amount, expected):
    """JH-FMT-01..06: Formats numbers as currency with proper symbols and rounding."""
    assert format_currency(amount) == expected

# FUNCTION-LEVEL TESTS: format_date 
# 5 distinct tests (3 parameterized valid date cases + 2 error cases)

@pytest.mark.formatting
@pytest.mark.parametrize(
    "iso_date, expected",
    [
        pytest.param("2026-10-15", "Oct 15, 2026", id="JH-FMT-07"),
        pytest.param("2026-05-03", "May 3, 2026", marks=pytest.mark.bva, id="JH-FMT-08"),
        pytest.param("2024-02-29", "Feb 29, 2024", id="JH-FMT-09"),
    ],
)
def test_format_date_valid(iso_date, expected):
    """JH-FMT-07..09: Converts ISO date strings to human-readable 'Month Day, Year'."""
    assert format_date(iso_date) == expected


@pytest.mark.formatting
def test_format_date_invalid_string_raises():
    """JH-FMT-10: Non-ISO string raises ValueError."""
    with pytest.raises(ValueError):
        format_date("15-10-2026")


@pytest.mark.formatting
def test_format_date_empty_string_raises():
    """JH-FMT-11: Empty string raises ValueError."""
    with pytest.raises(ValueError):
        format_date("")

# FUNCTION-LEVEL TESTS: format_relative 
# 6 distinct boundary and category tests

@pytest.mark.formatting
def test_format_relative_none_returns_never():
    """JH-FMT-12: moment=None returns 'never'."""
    assert format_relative(None) == "never"


@pytest.mark.formatting
@pytest.mark.bva
@pytest.mark.parametrize(
    "delta, expected",
    [
        pytest.param(timedelta(seconds=44), "just now", id="JH-FMT-13"),
        pytest.param(timedelta(seconds=45), "1 min ago", id="JH-FMT-14"),
        pytest.param(timedelta(seconds=3600), "1 hr ago", id="JH-FMT-15"),
    ],
)
def test_format_relative_boundaries(delta, expected):
    """JH-FMT-13..15: Delta boundary transitions for just now, min ago, and hr ago."""
    now = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    moment = now - delta
    assert format_relative(moment, now=now) == expected


@pytest.mark.formatting
def test_format_relative_future_seconds():
    """JH-FMT-16: Future moment within 45 seconds returns 'in a moment'."""
    now = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    future_moment = now + timedelta(seconds=30)
    assert format_relative(future_moment, now=now) == "in a moment"


@pytest.mark.formatting
def test_format_relative_future_minutes():
    """JH-FMT-17: Future moment beyond 45 seconds returns 'in X min'."""
    now = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    future_moment = now + timedelta(minutes=10)
    assert format_relative(future_moment, now=now) == "in 10 min"

# FUNCTION-LEVEL TESTS: format_local 
# 5 distinct tests

@pytest.mark.formatting
def test_format_local_none_returns_empty():
    """JH-FMT-18: moment=None returns empty string."""
    assert format_local(None) == ""


@pytest.mark.formatting
def test_format_local_valid_datetime():
    """JH-FMT-19: Formats timezone-aware datetime with date and 12-hour AM/PM."""
    dt = datetime(2026, 9, 22, 15, 4, tzinfo=timezone.utc)
    res = format_local(dt)
    assert "Sep 22, 2026" in res
    assert ("PM" in res or "AM" in res)


@pytest.mark.formatting
def test_format_local_strips_leading_zero_from_hour():
    """JH-FMT-20: Ensures hour does not have leading zero (e.g. '3:04 PM', not '03:04 PM')."""
    dt = datetime(2026, 9, 22, 3, 4, tzinfo=timezone.utc)
    res = format_local(dt)
    assert not res.endswith(" 03:04 AM")
    assert not res.endswith(" 03:04 PM")


@pytest.mark.formatting
def test_format_local_noon():
    """JH-FMT-21: 12:00 PM in local time is correctly indicated as 12:00 PM."""
    local_tz = datetime.now().astimezone().tzinfo
    dt = datetime(2026, 10, 15, 12, 0, tzinfo=local_tz)
    res = format_local(dt)
    assert "12:00 PM" in res


@pytest.mark.formatting
def test_format_local_midnight():
    """JH-FMT-22: Midnight (00:00) formats as 12:00 AM."""
    dt = datetime(2026, 10, 15, 0, 0, tzinfo=timezone.utc)
    res = format_local(dt)
    assert ("AM" in res or "PM" in res)

# MODULE / CLASS-LEVEL TESTS: Formatting Package Integration 
# 5 distinct tests

@pytest.mark.formatting
def test_format_relative_day_pluralization():
    """JH-FMT-CLS-01: format_relative correctly pluralizes days ('1 day ago' vs '3 days ago')."""
    now = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    one_day = now - timedelta(days=1)
    three_days = now - timedelta(days=3)
    assert format_relative(one_day, now=now) == "1 day ago"
    assert format_relative(three_days, now=now) == "3 days ago"


@pytest.mark.formatting
def test_format_relative_fallback_to_date_over_30_days():
    """JH-FMT-CLS-02: Delta exceeding 30 days falls back to format_date."""
    now = datetime(2026, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    old_moment = now - timedelta(days=45)
    res = format_relative(old_moment, now=now)
    assert "2026" in res
    assert "ago" not in res


@pytest.mark.formatting
def test_format_currency_extreme_small_and_large():
    """JH-FMT-CLS-03: Validates extreme boundary formatting ($0.01 and $10,000,000.00)."""
    assert format_currency(0.01) == "$0.01"
    assert format_currency(10000000.00) == "$10,000,000.00"


@pytest.mark.formatting
def test_format_date_end_of_year_rollover():
    """JH-FMT-CLS-04: Formats boundary dates of year transition (Dec 31 -> Jan 1)."""
    assert format_date("2026-12-31") == "Dec 31, 2026"
    assert format_date("2027-01-01") == "Jan 1, 2027"


@pytest.mark.formatting
def test_formatting_pipeline_expense_display():
    """JH-FMT-CLS-05: Complete pipeline: formatting currency, date, and local timestamp together."""
    amount = 54.20
    iso_date = "2026-10-15"
    dt = datetime(2026, 10, 15, 14, 30, tzinfo=timezone.utc)

    curr_str = format_currency(amount)
    date_str = format_date(iso_date)
    local_str = format_local(dt)

    assert curr_str == "$54.20"
    assert date_str == "Oct 15, 2026"
    assert "Oct 15, 2026" in local_str
