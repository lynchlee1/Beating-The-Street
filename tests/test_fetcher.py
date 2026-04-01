"""Unit tests for src/fetcher/ — base client interface and FMPClient setup.

Network calls are not made; these tests verify the class structure,
environment-variable handling, and data-parsing helpers.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.fetcher.base_client import BaseFinancialClient


# ── BaseFinancialClient interface tests ───────────────────────────────────────

class TestBaseFinancialClientInterface:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            BaseFinancialClient()

    def test_concrete_subclass_must_implement_all_methods(self):
        class Partial(BaseFinancialClient):
            def get_income_statement(self, ticker, quarters_back=80):
                return {}
            # Missing: get_balance_sheet, get_cash_flow, get_dividends,
            #          get_stock_price, get_market_cap

        with pytest.raises(TypeError):
            Partial()

    def test_full_concrete_subclass_is_instantiable(self):
        class Full(BaseFinancialClient):
            def get_income_statement(self, ticker, quarters_back=80): return {}
            def get_balance_sheet(self, ticker, quarters_back=80):    return {}
            def get_cash_flow(self, ticker, quarters_back=80):        return {}
            def get_dividends(self, ticker, quarters_back=80):        return {}
            def get_stock_price(self, ticker, years_back=20):         return {}
            def get_market_cap(self, ticker, years_back=20):          return {}

        client = Full()
        assert isinstance(client, BaseFinancialClient)


# ── FMPClient environment variable tests ──────────────────────────────────────

class TestFMPClientEnvVar:
    def test_raises_without_api_key(self):
        """FMPClient must raise EnvironmentError when FMP_API_KEY is unset."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the key if it exists
            os.environ.pop("FMP_API_KEY", None)
            from src.fetcher.fmp_client import FMPClient
            with pytest.raises(EnvironmentError, match="FMP_API_KEY"):
                FMPClient()

    def test_initialises_with_api_key(self):
        """FMPClient should not raise when FMP_API_KEY is set."""
        with patch.dict(os.environ, {"FMP_API_KEY": "test_key_12345"}):
            from src.fetcher.fmp_client import FMPClient
            client = FMPClient()
            assert client.api_key == "test_key_12345"

    def test_inherits_base_client(self):
        with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
            from src.fetcher.fmp_client import FMPClient
            client = FMPClient()
            assert isinstance(client, BaseFinancialClient)


# ── FMPClient.fetch_all sentinel tests ────────────────────────────────────────

class TestFMPClientFetchAll:
    """Test fetch_all error-sentinel returns without making real HTTP calls."""

    def _make_client(self):
        with patch.dict(os.environ, {"FMP_API_KEY": "fake_key"}):
            from src.fetcher.fmp_client import FMPClient
            return FMPClient()

    def test_fetch_all_returns_list_when_insufficient_quarters(self):
        client = self._make_client()

        # income-statement returns fewer than 52 quarters
        short_income = {f"2023-{i:02d}-30": {
            "revenue": 1e9, "operatingIncome": 1e8,
            "netIncomeFromContinuingOperations": 1e8,
            "netIncome": 1e8, "eps": 1.0, "epsDiluted": 1.0,
            "weightedAverageShsOut": 100e6, "weightedAverageShsOutDil": 101e6,
        } for i in range(1, 10)}

        with patch.object(client, "get_income_statement", return_value=short_income), \
             patch.object(client, "get_balance_sheet",    return_value={}), \
             patch.object(client, "get_cash_flow",        return_value={}), \
             patch.object(client, "get_dividends",        return_value={}), \
             patch.object(client, "get_stock_price",      return_value={}), \
             patch.object(client, "get_market_cap",       return_value={}):
            result = client.fetch_all("FAKE")
            assert isinstance(result, list)
            assert result[0] == "Error 52l"

    def test_fetch_all_returns_list_when_deficit(self):
        from tests.fixtures.sample_raw import build_sample_raw
        raw = build_sample_raw(ticker="FAKE")

        client = self._make_client()

        # Build income data with deficits in last 12 quarters
        deficit_income = {}
        dates = sorted(raw["netIncome"].keys(), reverse=True)
        for i, d in enumerate(dates):
            ni = -1_000_000 if i < 12 else raw["netIncome"][d]
            deficit_income[d] = {
                "revenue": raw["revenue"][d],
                "operatingIncome": ni,
                "netIncomeFromContinuingOperations": ni,
                "netIncome": ni,
                "eps": ni / 500e6,
                "epsDiluted": ni / 500e6,
                "weightedAverageShsOut": raw["weightedAverageShsOut"][d],
                "weightedAverageShsOutDil": raw["weightedAverageShsOutDil"][d],
            }

        with patch.object(client, "get_income_statement", return_value=deficit_income), \
             patch.object(client, "get_balance_sheet",    return_value={}), \
             patch.object(client, "get_cash_flow",        return_value={}), \
             patch.object(client, "get_dividends",        return_value={}), \
             patch.object(client, "get_stock_price",      return_value={}), \
             patch.object(client, "get_market_cap",       return_value={}):
            result = client.fetch_all("FAKE")
            assert isinstance(result, list)
            assert result[0] == "Error 12d"
