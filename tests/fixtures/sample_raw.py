"""Realistic sample financial data for a fictional company "DEMO Corp".

This data covers 20 years (80 quarters) of quarterly financials with
plausible growth trends, suitable for testing the full pipeline without
an API key.

Usage::

    from tests.fixtures.sample_raw import build_sample_raw
    raw = build_sample_raw()          # full 80-quarter dataset
    raw = build_sample_raw(ticker="ACME")  # custom ticker
"""

from __future__ import annotations

import math
from datetime import date, timedelta


# ── Calendar helpers ─────────────────────────────────────────────────────────

def _quarter_end_dates(n_quarters: int = 80, end_year: int = 2024) -> list[str]:
    """Return *n_quarters* quarterly fiscal-end dates ending at Q4 of *end_year*."""
    # Work backwards from 2024-12-31
    anchor = date(end_year, 12, 31)
    dates = []
    d = anchor
    for _ in range(n_quarters):
        dates.append(d.strftime("%Y-%m-%d"))
        # Step back one quarter
        m = d.month - 3
        y = d.year
        if m <= 0:
            m += 12
            y -= 1
        # Last day of that month
        # Quarters end on 31-Mar, 30-Jun, 30-Sep, 31-Dec
        quarter_end_day = {3: 31, 6: 30, 9: 30, 12: 31}[m]
        d = date(y, m, quarter_end_day)
    return list(reversed(dates))  # oldest first


def _daily_dates(start: str, end: str) -> list[str]:
    """Return every calendar day from *start* to *end* inclusive."""
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    result = []
    cur = s
    while cur <= e:
        result.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return result


# ── DEMO Corp financial model ────────────────────────────────────────────────
# Growth assumptions (annualised):
#  - Revenue: +8 % p.a.
#  - Net-income margin: 12 % of revenue (stable)
#  - Shares gradually bought back: -1 % p.a.
#  - Dividends: 30 % payout, growing with EPS
#  - Debt: modest long-term debt, slowly paid down
#  - Stock price: implied PER ≈ 18×

_REVENUE_Q1 = 2_000_000_000        # $2B in first quarter (annualised $8B)
_GROWTH_ANNUAL = 0.08               # 8 % revenue growth per year
_NET_MARGIN = 0.12                  # 12 % net margin
_SHARES_Q1 = 500_000_000           # 500M shares
_SHARE_BUYBACK = -0.0025           # -1 % per year = -0.25 % per quarter
_DIV_PAYOUT = 0.30                 # 30 % payout ratio on net income
_INITIAL_STOCK_PRICE = 30.0        # $30 in Q1 2005


def build_sample_raw(
    ticker: str = "DEMO",
    n_quarters: int = 80,
    end_year: int = 2024,
) -> dict:
    """Build a complete raw data dict for *ticker* covering *n_quarters* quarters.

    The data is deterministic and intentionally free of any API calls,
    so it works in unit tests without a network connection or API key.

    Returns
    -------
    dict
        Matches the exact schema expected by ``src.parser.calculator.build_parsed_data``.
    """
    fiscal_dates = _quarter_end_dates(n_quarters, end_year)
    n = len(fiscal_dates)

    # ── quarterly growth factor ───────────────────────────────────────────────
    qg = (1.0 + _GROWTH_ANNUAL) ** (1 / 4)  # ≈ 1.0194

    # ── Income statement ──────────────────────────────────────────────────────
    revenue:                 dict = {}
    netIncome:               dict = {}
    netIncomeFromContinuing: dict = {}
    weightedAverageShsOut:   dict = {}
    weightedAverageShsOutDil:dict = {}

    for i, d in enumerate(fiscal_dates):
        rev = _REVENUE_Q1 * (qg ** i)
        ni  = rev * _NET_MARGIN
        shs = _SHARES_Q1 * ((1.0 + _SHARE_BUYBACK) ** i)

        revenue[d]                  = round(rev)
        netIncome[d]                = round(ni)
        netIncomeFromContinuing[d]  = round(ni * 0.99)  # slight discount
        weightedAverageShsOut[d]    = round(shs)
        weightedAverageShsOutDil[d] = round(shs * 1.01)  # ~1 % dilution

    # ── Balance sheet ─────────────────────────────────────────────────────────
    cashAndShortTermInvestments: dict = {}
    inventory:                   dict = {}
    totalAssets:                 dict = {}
    totalStockholdersEquity:     dict = {}
    totalDebt:                   dict = {}
    longTermDebt:                dict = {}
    netDebt:                     dict = {}

    for i, d in enumerate(fiscal_dates):
        ni = netIncome[d]
        # Cash grows at roughly retained earnings (70 % of NI ÷ 4 quarters)
        cash = round(5_000_000_000 + ni * 0.70 * i / 4)
        ltd  = round(max(0, 8_000_000_000 - ni * i * 0.05))
        debt = round(ltd * 1.05)  # includes short-term portion
        eq   = round(15_000_000_000 + ni * 0.60 * i / 4)
        ta   = round(eq + debt + 2_000_000_000)
        inv  = round(500_000_000 + ni * 0.02 * i / 4)

        cashAndShortTermInvestments[d] = cash
        inventory[d]                   = inv
        totalAssets[d]                 = ta
        totalStockholdersEquity[d]     = eq
        totalDebt[d]                   = debt
        longTermDebt[d]                = ltd
        netDebt[d]                     = debt - cash

    # ── Cash flow ─────────────────────────────────────────────────────────────
    CFO:     dict = {}
    CFF:     dict = {}
    freeCF:  dict = {}

    for i, d in enumerate(fiscal_dates):
        ni = netIncome[d]
        cfo = round(ni * 1.15)   # OCF typically higher than net income
        cff = round(-ni * 0.40)  # Buybacks + dividends
        fcf = round(cfo - ni * 0.05)  # CapEx ≈ 5 % of NI

        CFO[d]    = cfo
        CFF[d]    = cff
        freeCF[d] = fcf

    # ── Dividends (quarterly per-share amounts) ────────────────────────────────
    dividends: dict = {}
    for i, d in enumerate(fiscal_dates):
        ni   = netIncome[d]
        shs  = weightedAverageShsOut[d]
        # Quarterly dividend = (payout_ratio * annual NI) / 4 / shares
        div_per_share = (ni * _DIV_PAYOUT) / shs
        dividends[d]  = round(div_per_share, 6)

    # ── Stock price (daily close) ──────────────────────────────────────────────
    stockPrice: dict = {}
    start_date  = fiscal_dates[0]
    end_date    = fiscal_dates[-1]
    all_days    = _daily_dates(start_date, end_date)

    # Map each fiscal date → EPS (trailing annual)
    # Use a simple PER of 18× for pricing
    PER_TARGET = 18.0
    fiscal_price: dict = {}
    for i, d in enumerate(fiscal_dates):
        if i < 3:
            fiscal_price[d] = _INITIAL_STOCK_PRICE * ((qg) ** i)
        else:
            # EPS trailing (last 4 quarters)
            trailing_ni  = sum(netIncome[fiscal_dates[j]] for j in range(max(0, i-3), i+1))
            trailing_shs = weightedAverageShsOutDil[d]
            eps_ttm      = trailing_ni / trailing_shs
            fiscal_price[d] = round(eps_ttm * PER_TARGET, 2)

    # Forward-fill to daily
    prev_price = _INITIAL_STOCK_PRICE
    fi = 0  # fiscal index
    for day in all_days:
        while fi < n and fiscal_dates[fi] <= day:
            prev_price = fiscal_price[fiscal_dates[fi]]
            fi += 1
        stockPrice[day] = {"close": prev_price, "volume": 5_000_000}

    # ── Market cap (daily) ────────────────────────────────────────────────────
    marketCap: dict = {}
    for day in all_days:
        price = stockPrice[day]["close"]
        # Use a daily interpolation of diluted shares (approximate)
        approx_shares = _SHARES_Q1 * ((1.0 + _SHARE_BUYBACK) ** (len(all_days) * 0.5 / 365))
        marketCap[day] = round(price * approx_shares)

    return {
        "ticker":    ticker,
        "fiscalDates": fiscal_dates,
        # Income statement
        "revenue":                              revenue,
        "netIncome":                            netIncome,
        "netIncomeFromContinuingOperations":    netIncomeFromContinuing,
        "weightedAverageShsOut":                weightedAverageShsOut,
        "weightedAverageShsOutDil":             weightedAverageShsOutDil,
        # Balance sheet
        "cashAndShortTermInvestments":          cashAndShortTermInvestments,
        "inventory":                            inventory,
        "totalAssets":                          totalAssets,
        "totalStockholdersEquity":              totalStockholdersEquity,
        "totalDebt":                            totalDebt,
        "longTermDebt":                         longTermDebt,
        "netDebt":                              netDebt,
        # Cash flow
        "CFO":      CFO,
        "CFF":      CFF,
        "freeCF":   freeCF,
        # Market data
        "dividends":  dividends,
        "stockPrice": stockPrice,
        "marketCap":  marketCap,
    }
