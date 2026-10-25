from __future__ import annotations

from datetime import date

import pytest

from expense_tracker.exports.options import (
    FILENAME_MAX_LENGTH,
    ExportOptions,
    default_filename_stem,
    parse_export_options,
    sanitize_filename,
)
from expense_tracker.models import CATEGORIES

VALID_FORMATS = {"csv", "json", "pdf"}

# FUNCTION-LEVEL TESTS: sanitize_filename 
# 6 distinct tests

@pytest.mark.options
def test_sanitize_filename_standard_clean():
    """JH-OPT-01: Standard alphanumeric name with spaces remains intact."""
    assert sanitize_filename("q3 report 2026") == "q3 report 2026"


@pytest.mark.options
def test_sanitize_filename_strips_extensions():
    """JH-OPT-02: Strips known extensions (.csv, .json, .pdf) case-insensitively."""
    assert sanitize_filename("my_report.csv") == "my_report"
    assert sanitize_filename("TAX_DOC.PDF") == "TAX_DOC"
    assert sanitize_filename("backup.JSON") == "backup"


@pytest.mark.options
@pytest.mark.security
def test_sanitize_filename_replaces_unsafe_characters():
    """JH-OPT-03: Replaces unsafe filesystem characters (<>:\"/\\|?*) with dashes."""
    assert sanitize_filename("bad<file>name:test?*") == "bad-file-name-test"


@pytest.mark.options
def test_sanitize_filename_collapses_dashes():
    """JH-OPT-04: Collapses multiple consecutive dashes into a single dash."""
    assert sanitize_filename("a---b----c") == "a-b-c"


@pytest.mark.options
@pytest.mark.bva
def test_sanitize_filename_length_limit_80_chars():
    """JH-OPT-05: Truncates long filenames to maximum length of 80 characters."""
    long_input = "a" * 100
    res = sanitize_filename(long_input)
    assert len(res) == FILENAME_MAX_LENGTH
    assert res == "a" * 80


@pytest.mark.options
@pytest.mark.bva
def test_sanitize_filename_empty_and_whitespace():
    """JH-OPT-06: Empty, whitespace, or only-punctuation inputs return empty string."""
    assert sanitize_filename("") == ""
    assert sanitize_filename("    ") == ""
    assert sanitize_filename("...---...") == ""

# FUNCTION-LEVEL TESTS: parse_export_options 
# 6 distinct tests

@pytest.mark.options
def test_parse_export_options_defaults():
    """JH-OPT-07: Default parameters produce csv format and all canonical categories."""
    options, errors = parse_export_options({}, VALID_FORMATS)
    assert errors == {}
    assert options.format == "csv"
    assert options.categories == tuple(CATEGORIES)
    assert options.all_categories is True
    assert options.sort == "date-desc"


@pytest.mark.options
@pytest.mark.ecp
def test_parse_export_options_invalid_format():
    """JH-OPT-08: Invalid format returns an appropriate error message."""
    options, errors = parse_export_options({"format": "xml"}, VALID_FORMATS)
    assert "format" in errors
    assert "Choose one of:" in errors["format"]


@pytest.mark.options
@pytest.mark.bva
def test_parse_export_options_date_range_validation():
    """JH-OPT-09: End date strictly before start date returns an error."""
    args = {"from": "2026-10-15", "to": "2026-10-10"}
    options, errors = parse_export_options(args, VALID_FORMATS)
    assert "to" in errors
    assert errors["to"] == "End date must be on or after the start date."


@pytest.mark.options
def test_parse_export_options_valid_category_filtering():
    """JH-OPT-10: Subsetting categories parses only requested valid categories."""
    args = {"categories": "Food, Bills"}
    options, errors = parse_export_options(args, VALID_FORMATS)
    assert errors == {}
    assert set(options.categories) == {"Food", "Bills"}
    assert options.all_categories is False


@pytest.mark.options
def test_parse_export_options_unknown_category_rejection():
    """JH-OPT-11: Supplying an unrecognized category reports an error."""
    args = {"categories": "Food, Crypto"}
    options, errors = parse_export_options(args, VALID_FORMATS)
    assert "categories" in errors
    assert "Unknown category: Crypto" in errors["categories"]


@pytest.mark.options
def test_parse_export_options_invalid_sort():
    """JH-OPT-12: Unrecognized sort order reports an error."""
    args = {"sort": "random-sort"}
    options, errors = parse_export_options(args, VALID_FORMATS)
    assert "sort" in errors
    assert errors["sort"] == "Choose a valid sort order."

# MODULE / CLASS-LEVEL TESTS: ExportOptions Dataclass & Stems 
# 5 distinct tests

@pytest.mark.options
def test_export_options_dataclass_defaults():
    """JH-OPT-CLS-01: Direct instantiation of ExportOptions reflects correct defaults."""
    opts = ExportOptions()
    assert opts.format == "csv"
    assert opts.date_from == ""
    assert opts.date_to == ""
    assert opts.categories == tuple(CATEGORIES)
    assert opts.sort == "date-desc"
    assert opts.filename == ""


@pytest.mark.options
def test_export_options_all_categories_boolean_logic():
    """JH-OPT-CLS-02: all_categories property evaluates full vs subset category tuples."""
    all_cats = ExportOptions(categories=tuple(CATEGORIES))
    assert all_cats.all_categories is True

    subset = ExportOptions(categories=("Food", "Bills"))
    assert subset.all_categories is False


@pytest.mark.options
def test_export_options_filename_for_custom():
    """JH-OPT-CLS-03: filename_for appends requested extension to custom sanitized stem."""
    opts = ExportOptions(filename="custom-report")
    assert opts.filename_for("csv") == "custom-report.csv"
    assert opts.filename_for("pdf") == "custom-report.pdf"


@pytest.mark.options
def test_export_options_filename_for_fallback_default():
    """JH-OPT-CLS-04: filename_for falls back to default stem with today's date when filename is empty."""
    opts = ExportOptions(filename="")
    res = opts.filename_for("json")
    assert res.startswith("expenses-")
    assert date.today().isoformat() in res
    assert res.endswith(".json")


@pytest.mark.options
def test_export_options_frozen_immutability():
    """JH-OPT-CLS-05: ExportOptions dataclass is frozen and prevents attribute assignment."""
    opts = ExportOptions()
    with pytest.raises(AttributeError):
        opts.format = "pdf"  # type: ignore
