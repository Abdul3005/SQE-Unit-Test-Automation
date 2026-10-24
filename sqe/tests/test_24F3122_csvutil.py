from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from expense_tracker.exports.csvutil import (
    _FORMULA_PREFIXES,
    _SIGNED_NUMBER,
    csv_bytes,
    neutralize,
)

# FUNCTION-LEVEL TESTS: neutralize
# 3 unit tests + 8 data-driven CSV tests

@pytest.mark.csvutil
@pytest.mark.bva
def test_neutralize_preserves_signed_numbers():
    """JH-CSV-01: Signed positive and negative numbers are data, not formulas, so NOT neutralized."""
    assert neutralize("+45.50") == "+45.50"
    assert neutralize("-120.00") == "-120.00"
    assert neutralize("+1,000") == "+1,000"


@pytest.mark.csvutil
@pytest.mark.bva
def test_neutralize_preserves_signed_percentages():
    """JH-CSV-02: Signed percentages (e.g. '+8%', '-12.5%') are preserved without prepending quote."""
    assert neutralize("+8%") == "+8%"
    assert neutralize("-12.5%") == "-12.5%"


@pytest.mark.csvutil
def test_neutralize_passes_through_non_strings_and_normal_text():
    """JH-CSV-03: Normal strings without formula prefixes and non-string types pass through unaltered."""
    assert neutralize("Normal Description") == "Normal Description"
    assert neutralize(100) == 100
    assert neutralize(45.5) == 45.5
    assert neutralize(None) is None

# DATA-DRIVEN TEST: External CSV Loading (Task 3 Requirement)
# Loads sqe/tests/data/test_24F3122_data.csv using csv.DictReader

CSV_PATH = Path(__file__).parent / "data" / "test_24F3122_data.csv"


def load_csv_cases():
    cases = []
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["input"] = row["input"].replace("\\t", "\t").replace("\\r", "\r")
            row["expected"] = row["expected"].replace("\\t", "\t").replace("\\r", "\r")
            cases.append(row)
    return cases


@pytest.mark.csvutil
@pytest.mark.data_driven
@pytest.mark.security
@pytest.mark.parametrize("case", load_csv_cases(), ids=lambda c: c["test_id"])
def test_neutralize_data_driven_csv(case):
    """JH-CSV-DD: Data-driven test loading external CSV rows for formula injection defense."""
    raw_val = case["input"]
    expected_val = case["expected"]
    assert neutralize(raw_val) == expected_val

# FUNCTION-LEVEL TESTS: csv_bytes 
# 6 distinct tests

@pytest.mark.csvutil
def test_csv_bytes_starts_with_utf8_bom():
    """JH-CSV-04: csv_bytes output begins with exact 3-byte UTF-8 BOM."""
    res = csv_bytes([["ColA", "ColB"]])
    assert res.startswith(b"\xef\xbb\xbf")


@pytest.mark.csvutil
def test_csv_bytes_rfc4180_crlf_terminators():
    """JH-CSV-05: Emits RFC 4180 CRLF (\\r\\n) row terminators."""
    rows = [["Header1", "Header2"], ["Val1", "Val2"]]
    res = csv_bytes(rows)
    assert b"\r\n" in res
    assert res.count(b"\r\n") == 2


@pytest.mark.csvutil
def test_csv_bytes_empty_rows_returns_only_bom():
    """JH-CSV-06: Passing an empty iterable of rows returns only the UTF-8 BOM bytes."""
    res = csv_bytes([])
    assert res == b"\xef\xbb\xbf"


@pytest.mark.csvutil
def test_csv_bytes_multi_row_tabular_matrix():
    """JH-CSV-07: Multi-row matrix with headers and data converts correctly."""
    rows = [
        ["Date", "Amount", "Description"],
        ["2026-10-15", 25.50, "Lunch"],
        ["2026-10-16", 10.00, "Bus Fare"],
    ]
    res = csv_bytes(rows)
    decoded = res.decode("utf-8-sig")
    assert "Date,Amount,Description\r\n" in decoded
    assert "2026-10-15,25.5,Lunch\r\n" in decoded


@pytest.mark.csvutil
@pytest.mark.security
def test_csv_bytes_neutralizes_formulas_in_rows():
    """JH-CSV-08: Formulas embedded in rows are neutralized in output stream."""
    rows = [["=cmd|' /C calc'!A0", 50.0]]
    res = csv_bytes(rows)
    decoded = res.decode("utf-8-sig")
    assert "'=cmd" in decoded


@pytest.mark.csvutil
def test_csv_bytes_unicode_preservation():
    """JH-CSV-09: Non-ASCII Unicode characters (e.g. accented letters, symbols) are encoded correctly."""
    rows = [["Café", "München", "¥500"]]
    res = csv_bytes(rows)
    decoded = res.decode("utf-8-sig")
    assert "Café,München,¥500" in decoded

# MODULE / CLASS-LEVEL TESTS: csvutil Pipeline & Constants 
# 5 distinct tests

@pytest.mark.csvutil
def test_formula_prefixes_constant_integrity():
    """JH-CSV-CLS-01: _FORMULA_PREFIXES tuple contains all 6 dangerous prefixes."""
    expected = ("=", "+", "-", "@", "\t", "\r")
    assert _FORMULA_PREFIXES == expected


@pytest.mark.csvutil
def test_signed_number_regex_matching():
    """JH-CSV-CLS-02: _SIGNED_NUMBER regex correctly identifies valid signed numeric formats."""
    assert _SIGNED_NUMBER.fullmatch("+12")
    assert _SIGNED_NUMBER.fullmatch("-12.50")
    assert _SIGNED_NUMBER.fullmatch("+1,000.00%")
    assert not _SIGNED_NUMBER.fullmatch("+12abc")
    assert not _SIGNED_NUMBER.fullmatch("=12")


@pytest.mark.csvutil
def test_csv_bytes_generator_stream_support():
    """JH-CSV-CLS-03: csv_bytes supports generator expressions as rows."""
    def row_generator():
        yield ["Row", 1]
        yield ["Row", 2]
    res = csv_bytes(row_generator())
    decoded = res.decode("utf-8-sig")
    assert "Row,1\r\nRow,2\r\n" == decoded


@pytest.mark.csvutil
def test_csv_bytes_with_empty_cells():
    """JH-CSV-CLS-04: Emits empty cells correctly without skipping columns."""
    rows = [["A", "", "C"]]
    res = csv_bytes(rows)
    decoded = res.decode("utf-8-sig")
    assert "A,,C\r\n" == decoded


@pytest.mark.csvutil
def test_csvutil_pipeline_roundtrip():
    """JH-CSV-CLS-05: End-to-end pipeline: multiple types, formula neutralization, and BOM decode."""
    matrix = [
        ["Product", "Price", "Formula"],
        ["Keyboard", 75.0, "=1+1"],
        ["Mouse", 25.5, "+10%"],
    ]
    raw_bytes = csv_bytes(matrix)
    assert raw_bytes[:3] == b"\xef\xbb\xbf"
    text = raw_bytes.decode("utf-8-sig")
    lines = text.strip().split("\r\n")
    assert len(lines) == 3
    assert lines[1] == "Keyboard,75.0,'=1+1"
    assert lines[2] == "Mouse,25.5,+10%"
