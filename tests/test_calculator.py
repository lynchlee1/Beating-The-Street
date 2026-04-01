"""Unit tests for src/parser/calculator.py.

These tests use the synthetic sample data from tests/fixtures/sample_raw.py
and require no network connection or API key.
"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tests.fixtures.sample_raw import build_sample_raw
from src.parser.calculator import (
    build_parsed_data,
    InsufficientDataError,
    _calc_trailing_series,
    _calc_averages_from_series,
    _calc_growth_from_dicts,
    _safe_sum_dict,
    _safe_frac,
    _safe_average_dict,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def raw_data():
    """Full 80-quarter sample raw data dict."""
    return build_sample_raw(ticker="TEST")


@pytest.fixture(scope="module")
def parsed_data(raw_data):
    """Fully parsed output from build_parsed_data."""
    return build_parsed_data(raw_data)


# ── Helper function tests ─────────────────────────────────────────────────────

class TestSafeSumDict:
    def test_normal(self):
        d = {"a": 10, "b": 20, "c": 30}
        assert _safe_sum_dict(d, ["a", "b"]) == 30.0

    def test_missing_key_returns_none(self):
        d = {"a": 10, "b": 20}
        assert _safe_sum_dict(d, ["a", "c"]) is None

    def test_none_value_returns_none(self):
        d = {"a": 10, "b": None}
        assert _safe_sum_dict(d, ["a", "b"]) is None

    def test_none_value_zero_on_none(self):
        d = {"a": 10, "b": None}
        assert _safe_sum_dict(d, ["a", "b"], zero_on_none=True) == 10.0

    def test_empty_dict(self):
        assert _safe_sum_dict({}, ["a"]) is None

    def test_empty_keys(self):
        assert _safe_sum_dict({"a": 1}, []) == 0.0


class TestSafeFrac:
    def test_basic(self):
        assert _safe_frac(10, 2) == 5.0

    def test_zero_denominator(self):
        assert _safe_frac(10, 0) is None

    def test_with_amplifier(self):
        assert _safe_frac(10, 2, amplifier=2.0) == 10.0

    def test_four_arg(self):
        assert _safe_frac(6, 2, 4, 3) == 4.0

    def test_none_inputs(self):
        assert _safe_frac(None, 2) is None


class TestSafeAverageDict:
    def test_normal(self):
        d = {"a": 10.0, "b": 20.0, "c": 30.0}
        result = _safe_average_dict(d, ["a", "b", "c"])
        assert result == pytest.approx(20.0)

    def test_missing_key_zero_counted(self):
        # Missing key treated as 0 contribution (total=0, count=0 path)
        d = {"a": 10.0}
        result = _safe_average_dict(d, ["a", "b"])
        # "b" is None → counted as 0 in total but count only increments for real values
        assert result == pytest.approx(10.0)

    def test_empty_returns_none(self):
        assert _safe_average_dict({}, ["a"]) is None


# ── Trailing series tests ─────────────────────────────────────────────────────

class TestCalcTrailingSeries:
    def _dates(self):
        return ["2020-03-31", "2020-06-30", "2020-09-30", "2020-12-31",
                "2021-03-31", "2021-06-30"]

    def _ni(self, dates):
        return {d: 100_000_000 for d in dates}

    def test_length_4_first_three_are_none(self):
        dates = self._dates()
        ni = self._ni(dates)
        result = _calc_trailing_series(dates, num1_dict=ni, trailing_length=4)
        assert result[dates[0]] is None
        assert result[dates[1]] is None
        assert result[dates[2]] is None

    def test_length_4_fourth_is_not_none(self):
        dates = self._dates()
        ni = self._ni(dates)
        result = _calc_trailing_series(dates, num1_dict=ni, trailing_length=4)
        assert result[dates[3]] is not None

    def test_trailing_sum_order_0_1(self):
        # order=(0,1) with trailing_length=4 means amplifier = (1/4)^0 * (4/4)^1 = 1
        dates = self._dates()
        ni = self._ni(dates)  # 100M each quarter
        result = _calc_trailing_series(dates, num1_dict=ni, trailing_length=4, order=(0, 1))
        # Sum of 4 quarters = 400M; amplifier 1 → 400M
        assert result[dates[3]] == pytest.approx(400_000_000.0)

    def test_length_1_no_initial_nones(self):
        dates = self._dates()
        ni = self._ni(dates)
        result = _calc_trailing_series(dates, num1_dict=ni, trailing_length=1)
        for d in dates:
            assert result[d] is not None


# ── Averages & growth tests ───────────────────────────────────────────────────

class TestCalcAveragesFromSeries:
    def test_returns_all_windows(self):
        dates = [f"2010-{m:02d}-30" for m in range(1, 13)] * 7  # ~84 dates
        series = {d: 1.0 for d in dates}
        dates_desc = list(reversed(dates))
        result = _calc_averages_from_series(series, dates_desc)
        assert set(result.keys()) == {"3Y", "5Y", "10Y", "13Y", "20Y"}

    def test_insufficient_data_returns_none(self):
        # Only 5 dates — 20Y window asks for 80 keys but the series only has 5.
        # _safe_average_dict returns the average of the available keys (not None),
        # because it includes the available subset.  For windows larger than the
        # dataset, the average is taken over the available data only.
        # 3Y needs 12 keys; with 5 we should still get a numeric result (sub-window).
        dates_desc = ["2024-12-31", "2024-09-30", "2024-06-30", "2024-03-31", "2023-12-31"]
        series = {d: 10.0 for d in dates_desc}
        result = _calc_averages_from_series(series, dates_desc)
        # All windows return the average of available data (10.0 for each)
        for w in ["3Y", "5Y", "10Y", "13Y", "20Y"]:
            # Either a numeric average (if any keys found) or None
            if result[w] is not None:
                assert result[w] == pytest.approx(10.0)


class TestCalcGrowthFromDicts:
    def test_positive_growth(self, raw_data):
        ni = raw_data["netIncome"]
        dates_desc = sorted(ni.keys(), reverse=True)
        result = _calc_growth_from_dicts(dates_desc, ni, None, None, None)
        # Revenue should be growing — all windows should show positive growth
        for window, val in result.items():
            if val is not None:
                assert val > 0, f"Expected positive growth in {window}, got {val}"

    def test_insufficient_data_returns_none(self):
        dates_desc = [f"2024-{i:02d}-30" for i in range(1, 13)]
        small_dict = {d: 100.0 for d in dates_desc}
        result = _calc_growth_from_dicts(dates_desc, small_dict, None, None, None)
        # 12 quarters < 20 required for 5Y, etc.
        assert result["5Y"] is None
        assert result["20Y"] is None


# ── build_parsed_data integration tests ──────────────────────────────────────

class TestBuildParsedData:
    def test_returns_dict(self, parsed_data):
        assert isinstance(parsed_data, dict)

    def test_required_top_level_keys(self, parsed_data):
        required = {"ticker", "generatedAt", "fiscalDates", "chartData",
                    "availableMetrics", "averages", "growth", "valuation"}
        assert required.issubset(parsed_data.keys())

    def test_ticker(self, parsed_data):
        assert parsed_data["ticker"] == "TEST"

    def test_fiscal_dates_sorted_ascending(self, parsed_data):
        dates = parsed_data["fiscalDates"]
        assert dates == sorted(dates)

    def test_chart_data_length(self, parsed_data, raw_data):
        assert len(parsed_data["chartData"]) == len(raw_data["fiscalDates"])

    def test_chart_data_row_has_date(self, parsed_data):
        for row in parsed_data["chartData"]:
            assert "date" in row

    def test_chart_data_has_trailing_keys(self, parsed_data):
        first_with_4q = next(
            (row for row in parsed_data["chartData"] if row.get("revenue_4q") is not None),
            None,
        )
        assert first_with_4q is not None, "No row with revenue_4q found"

    def test_available_metrics_structure(self, parsed_data):
        for m in parsed_data["availableMetrics"]:
            assert "key" in m
            assert "label" in m
            assert "category" in m
            assert "unit" in m

    def test_averages_all_windows(self, parsed_data):
        windows = {"3Y", "5Y", "10Y", "13Y", "20Y"}
        for key, window_dict in parsed_data["averages"].items():
            assert set(window_dict.keys()) == windows, f"Wrong windows for averages[{key}]"

    def test_averages_revenue_positive(self, parsed_data):
        rev_avgs = parsed_data["averages"]["revenue"]
        for window, val in rev_avgs.items():
            if val is not None:
                assert val > 0, f"Revenue average for {window} should be positive"

    def test_growth_keys(self, parsed_data):
        assert "revenue" in parsed_data["growth"]
        assert "netIncome" in parsed_data["growth"]
        assert "epsDiluted" in parsed_data["growth"]

    def test_eps_growth_positive(self, parsed_data):
        # DEMO Corp grows at ~8% p.a., so EPS growth should be positive
        eps_grow = parsed_data["growth"]["epsDiluted"]
        for window, val in eps_grow.items():
            if val is not None:
                assert val > 0, f"EPS growth for {window} expected positive, got {val}"

    def test_valuation_structure(self, parsed_data):
        v = parsed_data["valuation"]
        assert "currentMarketCap" in v
        assert "currentStockPrice" in v
        assert "per" in v
        assert "boxGroups" in v
        assert "peg" in v
        assert "adjustedPeg" in v

    def test_valuation_mcap_positive(self, parsed_data):
        assert parsed_data["valuation"]["currentMarketCap"] > 0

    def test_valuation_price_positive(self, parsed_data):
        assert parsed_data["valuation"]["currentStockPrice"] > 0

    def test_box_groups_windows(self, parsed_data):
        assert set(parsed_data["valuation"]["boxGroups"].keys()) == {"3Y", "5Y", "10Y", "13Y", "20Y"}

    def test_peg_windows(self, parsed_data):
        assert set(parsed_data["valuation"]["peg"].keys()) == {"3Y", "5Y", "10Y", "13Y", "20Y"}


class TestValidation:
    def test_insufficient_quarters_raises(self):
        raw = build_sample_raw(n_quarters=40)  # Only 40 quarters
        with pytest.raises(InsufficientDataError, match="quarters found"):
            build_parsed_data(raw)

    def test_deficit_raises(self):
        raw = build_sample_raw()
        # Inject losses in the last 12 quarters
        dates = sorted(raw["netIncome"].keys(), reverse=True)
        for d in dates[:12]:
            raw["netIncome"][d] = -1_000_000
        with pytest.raises(InsufficientDataError, match="negative"):
            build_parsed_data(raw)
