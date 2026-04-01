from abc import ABC, abstractmethod


class BaseFinancialClient(ABC):
    """Abstract base class for financial data API clients.

    Implement this interface to add support for a new data provider.
    """

    @abstractmethod
    def get_income_statement(self, ticker: str, quarters_back: int = 80) -> dict:
        """Return quarterly income-statement data keyed by date string."""

    @abstractmethod
    def get_balance_sheet(self, ticker: str, quarters_back: int = 80) -> dict:
        """Return quarterly balance-sheet data keyed by date string."""

    @abstractmethod
    def get_cash_flow(self, ticker: str, quarters_back: int = 80) -> dict:
        """Return quarterly cash-flow data keyed by date string."""

    @abstractmethod
    def get_dividends(self, ticker: str, quarters_back: int = 80) -> dict:
        """Return quarterly dividend data keyed by date string."""

    @abstractmethod
    def get_stock_price(self, ticker: str, years_back: int = 20) -> dict:
        """Return daily stock price data keyed by date string."""

    @abstractmethod
    def get_market_cap(self, ticker: str, years_back: int = 20) -> dict:
        """Return daily market cap data keyed by date string."""
