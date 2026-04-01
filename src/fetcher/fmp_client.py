import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

from .base_client import BaseFinancialClient

load_dotenv()


class FMPClient(BaseFinancialClient):
    """Financial Modeling Prep API client."""

    BASE_URL_V3 = "https://financialmodelingprep.com/api/v3"
    BASE_URL_STABLE = "https://financialmodelingprep.com/stable"

    def __init__(self):
        self.api_key = os.getenv("FMP_API_KEY", "")
        if not self.api_key:
            raise EnvironmentError(
                "FMP_API_KEY is not set. "
                "Copy .env.example to .env and add your API key."
            )

    def _get(self, url: str) -> list | dict:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------ #
    # Income statement                                                      #
    # ------------------------------------------------------------------ #
    def get_income_statement(self, ticker: str, quarters_back: int = 80) -> dict:
        url = (
            f"{self.BASE_URL_STABLE}/income-statement"
            f"?symbol={ticker}&apikey={self.api_key}"
            f"&period=quarterly&limit={quarters_back}"
        )
        data = self._get(url)
        result = {}
        for item in data:
            date = item["date"]
            result[date] = {
                "revenue": item["revenue"],
                "operatingIncome": item["operatingIncome"],
                "netIncomeFromContinuingOperations": item["netIncomeFromContinuingOperations"],
                "netIncome": item["netIncome"],
                "eps": item["eps"],
                "epsDiluted": item["epsDiluted"],
                "weightedAverageShsOut": item["weightedAverageShsOut"],
                "weightedAverageShsOutDil": item["weightedAverageShsOutDil"],
            }
        return result

    # ------------------------------------------------------------------ #
    # Balance sheet                                                         #
    # ------------------------------------------------------------------ #
    def get_balance_sheet(self, ticker: str, quarters_back: int = 80) -> dict:
        url = (
            f"{self.BASE_URL_STABLE}/balance-sheet-statement"
            f"?symbol={ticker}&apikey={self.api_key}"
            f"&period=quarterly&limit={quarters_back}"
        )
        data = self._get(url)
        result = {}
        for item in data:
            date = item["date"]
            result[date] = {
                "cashAndShortTermInvestments": item["cashAndShortTermInvestments"],
                "inventory": item["inventory"],
                "totalCurrentAssets": item["totalCurrentAssets"],
                "totalAssets": item["totalAssets"],
                "shortTermDebt": item["shortTermDebt"],
                "totalCurrentLiabilities": item["totalCurrentLiabilities"],
                "longTermDebt": item["longTermDebt"],
                "totalLiabilities": item["totalLiabilities"],
                "totalStockholdersEquity": item["totalStockholdersEquity"],
                "totalEquity": item["totalEquity"],
                "totalDebt": item["totalDebt"],
                "netDebt": item["netDebt"],
            }
        return result

    # ------------------------------------------------------------------ #
    # Cash flow                                                             #
    # ------------------------------------------------------------------ #
    def get_cash_flow(self, ticker: str, quarters_back: int = 80) -> dict:
        url = (
            f"{self.BASE_URL_STABLE}/cash-flow-statement"
            f"?symbol={ticker}&apikey={self.api_key}"
            f"&period=quarterly&limit={quarters_back}"
        )
        data = self._get(url)
        result = {}
        for item in data:
            date = item["date"]
            result[date] = {
                "CFO": item["netCashProvidedByOperatingActivities"],
                "CFI": item["netCashProvidedByInvestingActivities"],
                "CFF": item["netCashProvidedByFinancingActivities"],
                "freeCF": item["freeCashFlow"],
                "netStockIssuance": item["netStockIssuance"],
            }
        return result

    # ------------------------------------------------------------------ #
    # Dividends                                                             #
    # ------------------------------------------------------------------ #
    def get_dividends(self, ticker: str, quarters_back: int = 80) -> dict:
        url = (
            f"{self.BASE_URL_STABLE}/dividends"
            f"?symbol={ticker}&apikey={self.api_key}"
            f"&period=quarterly&limit={quarters_back}"
        )
        data = self._get(url)
        result = {}
        for item in data:
            date = item["date"]
            result[date] = item["adjDividend"]
        return result

    # ------------------------------------------------------------------ #
    # Stock price                                                           #
    # ------------------------------------------------------------------ #
    def get_stock_price(self, ticker: str, years_back: int = 20) -> dict:
        today = datetime.now()
        end_date = today.strftime("%Y-%m-%d")
        begin_date = (today - timedelta(days=365 * years_back)).strftime("%Y-%m-%d")
        url = (
            f"{self.BASE_URL_V3}/historical-price-full/{ticker}"
            f"?from={begin_date}&to={end_date}&apikey={self.api_key}"
        )
        data = self._get(url)
        result = {}
        for item in data.get("historical", []):
            date = item["date"]
            result[date] = {"close": item["close"], "volume": item["volume"]}
        return result

    # ------------------------------------------------------------------ #
    # Market cap                                                            #
    # ------------------------------------------------------------------ #
    def get_market_cap(self, ticker: str, years_back: int = 20) -> dict:  # noqa: D401
        today = datetime.now()
        begin_date = (today - timedelta(days=365 * years_back)).strftime("%Y-%m-%d")
        url = (
            f"{self.BASE_URL_STABLE}/historical-market-capitalization"
            f"?symbol={ticker}&from={begin_date}&apikey={self.api_key}"
        )
        data = self._get(url)
        result = {}
        for item in data:
            date = item["date"]
            result[date] = item["marketCap"]
        return result

    # ------------------------------------------------------------------ #
    # Convenience: fetch all data for a ticker                              #
    # ------------------------------------------------------------------ #
    def fetch_all(
        self,
        ticker: str,
        years_back: int = 20,
        quarters_back: int = 80,
    ) -> dict:
        """Fetch and merge all financial data for *ticker*.

        Returns a flat dict with every metric keyed by date, plus
        ``fiscalDates`` (sorted list) and ``ticker``.  Raises or
        returns an error-list sentinel when data quality checks fail.
        """
        data: dict = {"ticker": ticker}

        # --- Income statement ---
        income = self.get_income_statement(ticker, quarters_back)
        for date, metrics in income.items():
            for key, val in metrics.items():
                if key not in data:
                    data[key] = {}
                data[key][date] = val

        # Quality gate: need at least 52 quarters, no recent deficits
        if len(data.get("netIncome", {})) < 52:
            count = len(data.get("netIncome", {}))
            print(
                f"Stock {ticker} has less than 13 years of data: {count} quarters found"
            )
            return ["Error 52l", count]

        income_dates = sorted(income.keys(), reverse=True)
        deficit = sum(1 for d in income_dates[:12] if data["netIncome"].get(d, 0) < 0)
        if deficit > 0:
            print(
                f"Stock {ticker} has deficit in recent 3 years: "
                f"total deficit of {deficit} quarters"
            )
            return ["Error 12d", deficit]

        # --- Balance sheet ---
        balance = self.get_balance_sheet(ticker, quarters_back)
        for date, metrics in balance.items():
            for key, val in metrics.items():
                if key not in data:
                    data[key] = {}
                data[key][date] = val

        # --- Cash flow ---
        cash_flow = self.get_cash_flow(ticker, quarters_back)
        for date, metrics in cash_flow.items():
            for key, val in metrics.items():
                if key not in data:
                    data[key] = {}
                data[key][date] = val

        # Build fiscal dates list
        all_dates: set = set()
        for key, val in data.items():
            if isinstance(val, dict):
                all_dates.update(val.keys())
        data["fiscalDates"] = sorted(all_dates)

        # --- Market data ---
        data["dividends"]  = self.get_dividends(ticker, quarters_back)
        data["stockPrice"] = self.get_stock_price(ticker, years_back)
        data["marketCap"]  = self.get_market_cap(ticker, years_back)

        return data
