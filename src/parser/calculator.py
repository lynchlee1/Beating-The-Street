"""Financial data parser and calculator.

Takes raw financial API data (as returned by any BaseFinancialClient
implementation) and produces a clean, UI-ready JSON structure that is
injected into the React dashboard.

Output schema
-------------
{
  "ticker":       str,
  "generatedAt":  ISO-8601 string,
  "fiscalDates":  [date_str, ...],          # sorted ascending
  "chartData":    [                         # one entry per fiscal date
    {
      "date":       str,
      "<metric>":   number | null,          # raw quarterly value
      "<metric>_4q":  number | null,        # trailing 4-quarter annualised
      "<metric>_12q": number | null,        # trailing 12-quarter annualised
    }, ...
  ],
  "availableMetrics": [
    {"key": str, "label": str, "category": str, "unit": str}, ...
  ],
  "averages": {
    "<metric>": {"3Y": v, "5Y": v, "10Y": v, "13Y": v, "20Y": v}, ...
  },
  "growth": {
    "<metric>": {"3Y": v, "5Y": v, "10Y": v, "13Y": v, "20Y": v}, ...
  },
  "valuation": {
    "currentMarketCap":  number,
    "currentStockPrice": number,
    "per":               number,
    "cashPerStock":      number,
    "cashPercent":       number,
    "boxGroups": {
      "3Y":  {"Net Income": v, "EPS": v, "PY": v},
      ...
    },
    "peg":         {"3Y": v, "5Y": v, "10Y": v, "13Y": v, "20Y": v},
    "adjustedPeg": {"3Y": v, "5Y": v, "10Y": v, "13Y": v, "20Y": v},
  }
}
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


# --------------------------------------------------------------------------- #
# Low-level helpers (ported from utilitylib.py / btsplotlib.py)               #
# --------------------------------------------------------------------------- #

def _safe_sum_dict(d: dict, keys: list, zero_on_none: bool = False) -> Optional[float]:
    total = 0.0
    if not d:
        return None
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            total += v
        elif v is None and zero_on_none:
            total += 0.0
        else:
            return None
    return total


def _safe_frac(n1, d1, n2=1, d2=1, amplifier=1.0) -> Optional[float]:
    try:
        return amplifier * (n1 * n2) / (d1 * d2)
    except Exception:
        return None


def _safe_average(values: list, zero_on_none: bool = False) -> Optional[float]:
    if zero_on_none:
        cleaned = [0.0 if v is None else v for v in values]
    else:
        cleaned = [v for v in values if v is not None]
    if not cleaned:
        return None
    return sum(cleaned) / len(cleaned)


def _safe_average_dict(d: dict, keys: list, zero_on_none: bool = False) -> Optional[float]:
    total, count = 0.0, 0
    if not d:
        return None
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            total += v
            count += 1
        elif v is None and zero_on_none:
            total += 0.0
            count += 1
        elif v is None:
            total += 0.0
        else:
            return None
    return total / count if count > 0 else None


def _last_quarter_date(date: str) -> str:
    year, month, day = int(date[:4]), int(date[5:7]), date[8:10]
    if month <= 3:
        year -= 1
        month += 9
    else:
        month -= 3
    return f"{year:04d}-{month:02d}-{day}"


# --------------------------------------------------------------------------- #
# Trailing-window series calculator                                             #
# --------------------------------------------------------------------------- #

def _calc_trailing_series(
    dates: list[str],
    num1_dict: Optional[dict] = None,
    num2_dict: Optional[dict] = None,
    den1_dict: Optional[dict] = None,
    den2_dict: Optional[dict] = None,
    trailing_length: int = 4,
    order: tuple = (0, 1),
    amplifier: float = 1.0,
    zero_on_none: bool = False,
) -> dict[str, Optional[float]]:
    """Return {date: trailing_value} for each fiscal date."""
    amp = amplifier * ((1.0 / trailing_length) ** order[0]) * ((4.0 / trailing_length) ** order[1])
    result: dict[str, Optional[float]] = {}

    for i, date in enumerate(dates):
        if i < trailing_length - 1:
            result[date] = None
            continue
        window = dates[i - trailing_length + 1 : i + 1]
        n1 = _safe_sum_dict(num1_dict, window, zero_on_none) if num1_dict else 1.0
        n2 = _safe_sum_dict(num2_dict, window, zero_on_none) if num2_dict else 1.0
        d1 = _safe_sum_dict(den1_dict, window, zero_on_none) if den1_dict else 1.0
        d2 = _safe_sum_dict(den2_dict, window, zero_on_none) if den2_dict else 1.0
        result[date] = _safe_frac(n1, d1, n2, d2, amplifier=amp)

    return result


# --------------------------------------------------------------------------- #
# Average / growth over multi-year windows                                      #
# --------------------------------------------------------------------------- #

_WINDOWS = [
    ("3Y", 12),
    ("5Y", 20),
    ("10Y", 40),
    ("13Y", 52),
    ("20Y", 80),
]


def _calc_averages_from_series(trailing_series: dict, dates_desc: list) -> dict:
    """Return {"3Y": v, "5Y": v, ...} averages of an already-computed trailing series."""
    out = {}
    for label, length in _WINDOWS:
        keys = dates_desc[:length]
        out[label] = _safe_average_dict(trailing_series, keys)
    return out


def _calc_growth_from_dicts(
    dates_desc: list,
    num1_dict: Optional[dict],
    num2_dict: Optional[dict],
    den1_dict: Optional[dict],
    den2_dict: Optional[dict],
) -> dict:
    """Return CAGR growth rates {"3Y": v, ...} between earliest and latest trailing windows."""
    out = {}
    for label, data_length in _WINDOWS:
        trailing_length = 4 if data_length <= 20 else 12
        if any(
            d is not None and len(d) < data_length
            for d in [num1_dict, num2_dict, den1_dict, den2_dict]
        ):
            out[label] = None
            continue

        last_w = dates_desc[:trailing_length]
        first_w = dates_desc[data_length - trailing_length : data_length]

        last_n1  = _safe_sum_dict(num1_dict,  last_w)  if num1_dict  else 1.0
        last_n2  = _safe_sum_dict(num2_dict,  last_w)  if num2_dict  else 1.0
        last_d1  = _safe_sum_dict(den1_dict,  last_w)  if den1_dict  else 1.0
        last_d2  = _safe_sum_dict(den2_dict,  last_w)  if den2_dict  else 1.0
        first_n1 = _safe_sum_dict(num1_dict,  first_w) if num1_dict  else 1.0
        first_n2 = _safe_sum_dict(num2_dict,  first_w) if num2_dict  else 1.0
        first_d1 = _safe_sum_dict(den1_dict,  first_w) if den1_dict  else 1.0
        first_d2 = _safe_sum_dict(den2_dict,  first_w) if den2_dict  else 1.0

        last_v  = _safe_frac(last_n1,  last_d1,  last_n2,  last_d2)
        first_v = _safe_frac(first_n1, first_d1, first_n2, first_d2)

        try:
            out[label] = (last_v / first_v) ** (4.0 / (data_length - trailing_length)) - 1.0
        except Exception:
            out[label] = None
    return out


# --------------------------------------------------------------------------- #
# Price / market-cap alignment helpers                                          #
# --------------------------------------------------------------------------- #

def _align_price_series(
    fiscal_dates: list[str],
    price_dict: dict,
    mcap_dict: dict,
    dividend_dict: dict,
) -> tuple[dict, dict, dict]:
    """Map daily price/mcap/dividend data onto quarterly fiscal dates."""
    price_dates = sorted(price_dict.keys())
    mcap_dates  = sorted(mcap_dict.keys())
    div_dates   = sorted(dividend_dict.keys())

    aligned_price: dict = {}
    aligned_mcap:  dict = {}
    aligned_div:   dict = {}

    def _period_avg(source_dict, source_dates, start_inc, end_exc):
        total, count = 0.0, 0
        for d in source_dates:
            if start_inc <= d < end_exc:
                v = source_dict[d]
                if isinstance(v, dict):
                    v = v.get("close", 0.0)
                total += v
                count += 1
        return total / count if count > 0 else 0.0

    def _period_sum(source_dict, source_dates, start_inc, end_exc):
        total = 0.0
        for d in source_dates:
            if start_inc <= d < end_exc:
                total += source_dict[d]
        return total

    # Pre-period (before first fiscal date)
    first_date = fiscal_dates[0]
    prev_q = _last_quarter_date(first_date)
    aligned_price[first_date] = _period_avg(price_dict, price_dates, prev_q, first_date)
    aligned_mcap[first_date]  = _period_avg(mcap_dict,  mcap_dates,  prev_q, first_date)
    aligned_div[first_date]   = _period_sum(dividend_dict, div_dates, prev_q, first_date)

    for i in range(len(fiscal_dates) - 1):
        cur  = fiscal_dates[i]
        nxt  = fiscal_dates[i + 1]
        aligned_price[nxt] = _period_avg(price_dict, price_dates, cur, nxt)
        aligned_mcap[nxt]  = _period_avg(mcap_dict,  mcap_dates,  cur, nxt)
        aligned_div[nxt]   = _period_sum(dividend_dict, div_dates,  cur, nxt)

    return aligned_price, aligned_mcap, aligned_div


def _fill_market_cap(mcap_dict: dict) -> dict:
    """Forward-fill market cap for every calendar day (for PER chart)."""
    dates = sorted(mcap_dict.keys())
    if not dates:
        return {}
    start = datetime.strptime(dates[0], "%Y-%m-%d")
    end   = datetime.strptime(dates[-1], "%Y-%m-%d")
    filled: dict = {}
    cur, prev_val = start, mcap_dict[dates[0]]
    while cur <= end:
        ds = cur.strftime("%Y-%m-%d")
        v  = mcap_dict.get(ds)
        if v is not None:
            prev_val = v
        filled[ds] = prev_val
        cur += timedelta(days=1)
    return filled


# --------------------------------------------------------------------------- #
# Validation                                                                    #
# --------------------------------------------------------------------------- #

class InsufficientDataError(ValueError):
    pass


def _validate(data: dict):
    net_income = data.get("netIncome", {})
    if len(net_income) < 52:
        raise InsufficientDataError(
            f"Only {len(net_income)} quarters found; need at least 52 (13 years)."
        )
    dates_desc = sorted(net_income.keys(), reverse=True)
    recent_12 = dates_desc[:12]
    deficit = sum(1 for d in recent_12 if net_income[d] < 0)
    if deficit > 0:
        raise InsufficientDataError(
            f"Net income was negative in {deficit} of the last 12 quarters."
        )


# --------------------------------------------------------------------------- #
# Main entry point                                                              #
# --------------------------------------------------------------------------- #

def build_parsed_data(raw: dict) -> dict:
    """Convert raw fetched data dict into the UI-ready JSON structure.

    Parameters
    ----------
    raw : dict
        As returned by ``FMPClient.fetch_all`` (or any compatible provider).
        Expected keys: ticker, netIncome, revenue, operatingIncome,
        netIncomeFromContinuingOperations, eps, epsDiluted,
        weightedAverageShsOut, weightedAverageShsOutDil,
        cashAndShortTermInvestments, inventory, totalCurrentAssets, totalAssets,
        shortTermDebt, totalCurrentLiabilities, longTermDebt, totalLiabilities,
        totalStockholdersEquity, totalEquity, totalDebt, netDebt,
        CFO, CFI, CFF, freeCF, netStockIssuance,
        dividends, stockPrice, marketCap, fiscalDates.

    Returns
    -------
    dict
        UI-ready payload (see module docstring for full schema).
    """
    _validate(raw)

    ticker = raw["ticker"]
    fiscal_dates: list[str] = sorted(raw["fiscalDates"])
    dates_desc = list(reversed(fiscal_dates))

    # --- Align price / mcap / dividend onto fiscal dates ---
    aligned_price, aligned_mcap, aligned_div = _align_price_series(
        fiscal_dates, raw["stockPrice"], raw["marketCap"], raw["dividends"]
    )
    filled_mcap = _fill_market_cap(raw["marketCap"])

    # --- Convenience shortcuts ---
    ni    = raw["netIncome"]
    rev   = raw["revenue"]
    ni_co = raw["netIncomeFromContinuingOperations"]
    shs   = raw["weightedAverageShsOut"]
    shsd  = raw["weightedAverageShsOutDil"]
    cash  = raw["cashAndShortTermInvestments"]
    inv   = raw["inventory"]
    ltd   = raw["longTermDebt"]
    nd    = raw["netDebt"]
    td    = raw["totalDebt"]
    eq    = raw["totalStockholdersEquity"]
    ta    = raw["totalAssets"]
    cfo   = raw["CFO"]
    cff   = raw["CFF"]
    fcf   = raw["freeCF"]

    # ------------------------------------------------------------------ #
    # Build chart-data array (one object per fiscal date)                  #
    # ------------------------------------------------------------------ #

    # Pre-compute trailing series for all metrics we want to chart
    def _trail(num1=None, num2=None, den1=None, den2=None,
                length=4, order=(0,1), zero_on_none=False):
        return _calc_trailing_series(
            fiscal_dates, num1, num2, den1, den2,
            trailing_length=length, order=order, zero_on_none=zero_on_none
        )

    trailing_4q: dict[str, dict] = {
        "revenue":            _trail(rev),
        "netIncome":          _trail(ni),
        "netIncomeCO":        _trail(ni_co),
        "eps":                _trail(ni, den1=shs, order=(-1, 1)),
        "epsDiluted":         _trail(ni, den1=shsd, order=(-1, 1)),
        "shares":             _trail(shs, order=(1, 0)),
        "sharesDiluted":      _trail(shsd, order=(1, 0)),
        "dividends":          _trail(aligned_div, zero_on_none=True),
        "dividendYield":      _trail(aligned_div, den1=aligned_price, order=(-1, 1)),
        "payoutRatio":        _trail(aligned_div, num2=shs, den1=ni, order=(1, 0)),
        "cash":               _trail(cash, order=(1, 0)),
        "longTermDebt":       _trail(ltd, order=(1, 0)),
        "netDebt":            _trail(nd, order=(1, 0)),
        "debtToEquity":       _trail(td, den1=eq),
        "inventory":          _trail(inv, order=(1, 0)),
        "netMargin":          _trail(ni, den1=rev),
        "roe":                _trail(ni, den1=eq, order=(-1, 1)),
        "assetTurnover":      _trail(rev, den1=ta, order=(-1, 0)),
        "leverage":           _trail(ta, den1=eq),
        "cfo":                _trail(cfo),
        "cff":                _trail(cff),
        "freeCashFlow":       _trail(fcf),
        "per":                _trail(aligned_mcap, den1=ni, order=(1, -1)),
    }

    trailing_12q: dict[str, dict] = {k: _trail(**{
        "revenue":           dict(num1=rev),
        "netIncome":         dict(num1=ni),
        "netIncomeCO":       dict(num1=ni_co),
        "eps":               dict(num1=ni, den1=shs, order=(-1, 1)),
        "epsDiluted":        dict(num1=ni, den1=shsd, order=(-1, 1)),
        "shares":            dict(num1=shs, order=(1, 0)),
        "sharesDiluted":     dict(num1=shsd, order=(1, 0)),
        "dividends":         dict(num1=aligned_div, zero_on_none=True),
        "dividendYield":     dict(num1=aligned_div, den1=aligned_price, order=(-1, 1)),
        "payoutRatio":       dict(num1=aligned_div, num2=shs, den1=ni, order=(1, 0)),
        "cash":              dict(num1=cash, order=(1, 0)),
        "longTermDebt":      dict(num1=ltd, order=(1, 0)),
        "netDebt":           dict(num1=nd, order=(1, 0)),
        "debtToEquity":      dict(num1=td, den1=eq),
        "inventory":         dict(num1=inv, order=(1, 0)),
        "netMargin":         dict(num1=ni, den1=rev),
        "roe":               dict(num1=ni, den1=eq, order=(-1, 1)),
        "assetTurnover":     dict(num1=rev, den1=ta, order=(-1, 0)),
        "leverage":          dict(num1=ta, den1=eq),
        "cfo":               dict(num1=cfo),
        "cff":               dict(num1=cff),
        "freeCashFlow":      dict(num1=fcf),
        "per":               dict(num1=aligned_mcap, den1=ni, order=(1, -1)),
    }[k], length=12) for k in trailing_4q}

    # Raw quarterly point-in-time values (for each metric that makes sense)
    raw_q: dict[str, dict] = {
        "revenue":       rev,
        "netIncome":     ni,
        "netIncomeCO":   ni_co,
        "eps":           {d: _safe_frac(ni.get(d), shs.get(d)) for d in fiscal_dates},
        "epsDiluted":    {d: _safe_frac(ni.get(d), shsd.get(d)) for d in fiscal_dates},
        "shares":        shs,
        "sharesDiluted": shsd,
        "dividends":     aligned_div,
        "cash":          cash,
        "longTermDebt":  ltd,
        "netDebt":       nd,
        "inventory":     inv,
        "cfo":           cfo,
        "cff":           cff,
        "freeCashFlow":  fcf,
        "marketCap":     aligned_mcap,
    }

    # Build flat chart-data list
    chart_data = []
    for date in fiscal_dates:
        row: dict = {"date": date}
        for key, src in raw_q.items():
            row[key] = src.get(date)
        for key, series in trailing_4q.items():
            row[f"{key}_4q"] = series.get(date)
        for key, series in trailing_12q.items():
            row[f"{key}_12q"] = series.get(date)
        chart_data.append(row)

    # ------------------------------------------------------------------ #
    # Averages table                                                        #
    # ------------------------------------------------------------------ #

    # Use 4Q trailing as basis for averages (annualised quarterly values)
    averages: dict[str, dict] = {}
    for key, series in trailing_4q.items():
        averages[key] = _calc_averages_from_series(series, dates_desc)

    # ------------------------------------------------------------------ #
    # Growth table                                                          #
    # ------------------------------------------------------------------ #

    growth: dict[str, dict] = {
        "revenue":      _calc_growth_from_dicts(dates_desc, rev,  None, None, None),
        "netIncome":    _calc_growth_from_dicts(dates_desc, ni,   None, None, None),
        "eps":          _calc_growth_from_dicts(dates_desc, ni,   None, shs,  None),
        "epsDiluted":   _calc_growth_from_dicts(dates_desc, ni,   None, shsd, None),
        "shares":       _calc_growth_from_dicts(dates_desc, shs,  None, None, None),
        "sharesDiluted":_calc_growth_from_dicts(dates_desc, shsd, None, None, None),
        "freeCashFlow": _calc_growth_from_dicts(dates_desc, fcf,  None, None, None),
    }

    # ------------------------------------------------------------------ #
    # Valuation                                                             #
    # ------------------------------------------------------------------ #

    last_mcap_date  = sorted(raw["marketCap"].keys())[-1]
    last_price_date = sorted(raw["stockPrice"].keys())[-1]
    last_ni_date    = sorted(ni.keys())[-1]
    last_nd_date    = sorted(nd.keys())[-1]
    last_shsd_date  = sorted(shsd.keys())[-1]

    current_mcap  = raw["marketCap"][last_mcap_date]
    current_price = raw["stockPrice"][last_price_date]["close"]
    avg_ni_3y     = _safe_average_dict(ni, dates_desc[:12])

    per_val = _safe_frac(0.25 * current_mcap, avg_ni_3y) if avg_ni_3y else None

    net_cash    = -(nd.get(last_nd_date, 0) or 0)
    dil_shares  = shsd.get(last_shsd_date, 1) or 1
    cash_per_sh = net_cash / dil_shares if dil_shares else 0.0
    cash_pct    = cash_per_sh / current_price if current_price else 0.0

    # Box whisker groups (the "Beating The Street" valuation bands)
    # Uses 3Y/5Y/10Y/13Y/20Y averages of three valuation proxies
    _t1_series = _calc_trailing_series(fiscal_dates, ni, order=(0, 1), trailing_length=1)
    _div_shs_series = _calc_trailing_series(
        fiscal_dates, aligned_div, shs, order=(1, 1), trailing_length=1
    )
    _shsd_series = _calc_trailing_series(fiscal_dates, shsd, order=(1, 0), trailing_length=1)
    _depsdil_series = _calc_trailing_series(fiscal_dates, ni, den1_dict=shsd, order=(-1, 1), trailing_length=1)
    _div_series = _calc_trailing_series(fiscal_dates, aligned_div, trailing_length=1)
    _payout_series = _calc_trailing_series(fiscal_dates, aligned_div, shs, den1_dict=ni, order=(1, 0), trailing_length=1)
    _per_series = _calc_trailing_series(fiscal_dates, aligned_mcap, den1_dict=ni, order=(1, -1), trailing_length=1)

    box_groups: dict = {}
    for label, length in _WINDOWS:
        keys = dates_desc[:length]
        ni_avg    = _safe_average_dict(_t1_series, keys)
        ds_avg    = _safe_average_dict(_div_shs_series, keys)
        shsd_avg  = _safe_average_dict(_shsd_series, keys)
        deps_avg  = _safe_average_dict(_depsdil_series, keys)
        div_avg   = _safe_average_dict(_div_series, keys)
        pay_avg   = _safe_average_dict(_payout_series, keys)

        try:
            ni_val  = 0.3333 * ni_avg + (ds_avg or 0)
        except Exception:
            ni_val = None
        try:
            eps_val = shsd_avg * (0.3333 * deps_avg + (div_avg or 0))
        except Exception:
            eps_val = None
        try:
            py_val  = ni_avg * (0.3333 + (pay_avg or 0))
        except Exception:
            py_val = None

        box_groups[label] = {"netIncome": ni_val, "eps": eps_val, "py": py_val}

    # PEG ratios
    eps_grow   = growth.get("epsDiluted", {})
    div_yield_4q = trailing_4q.get("dividendYield", {})
    div_yield_3y_avg = _safe_average_dict(div_yield_4q, dates_desc[:12])

    def _peg(label, length_q):
        try:
            return (
                100 * (eps_grow.get(label, 0) + (div_yield_3y_avg or 0)) / per_val
            )
        except Exception:
            return None

    peg = {lbl: _peg(lbl, q) for lbl, q in _WINDOWS}

    def _adj_peg(label, length_q):
        try:
            if cash_pct <= 0:
                return None
            return (
                100 * (eps_grow.get(label, 0) + (div_yield_3y_avg or 0)) / per_val / cash_pct
            )
        except Exception:
            return None

    adj_peg = {lbl: _adj_peg(lbl, q) for lbl, q in _WINDOWS}

    # ------------------------------------------------------------------ #
    # Available metrics metadata                                            #
    # ------------------------------------------------------------------ #

    available_metrics = [
        # Income
        {"key": "revenue",        "label": "Revenue",                "category": "Income",    "unit": "$"},
        {"key": "netIncome",      "label": "Net Income",             "category": "Income",    "unit": "$"},
        {"key": "netIncomeCO",    "label": "Continuing Net Income",  "category": "Income",    "unit": "$"},
        # Per-share
        {"key": "eps",            "label": "EPS",                    "category": "Per Share", "unit": "$"},
        {"key": "epsDiluted",     "label": "Diluted EPS",            "category": "Per Share", "unit": "$"},
        {"key": "dividends",      "label": "Dividends",              "category": "Per Share", "unit": "$"},
        {"key": "dividendYield",  "label": "Dividend Yield",         "category": "Per Share", "unit": "%"},
        {"key": "payoutRatio",    "label": "Payout Ratio",           "category": "Per Share", "unit": "%"},
        # Shares
        {"key": "shares",         "label": "Shares Outstanding",     "category": "Shares",    "unit": "#"},
        {"key": "sharesDiluted",  "label": "Diluted Shares",         "category": "Shares",    "unit": "#"},
        # Cash flow
        {"key": "freeCashFlow",   "label": "Free Cash Flow",         "category": "Cash Flow", "unit": "$"},
        {"key": "cfo",            "label": "Operating Cash Flow",    "category": "Cash Flow", "unit": "$"},
        {"key": "cff",            "label": "Financing Cash Flow",    "category": "Cash Flow", "unit": "$"},
        # Balance sheet
        {"key": "cash",           "label": "Cash & Equivalents",     "category": "Balance",   "unit": "$"},
        {"key": "longTermDebt",   "label": "Long Term Debt",         "category": "Balance",   "unit": "$"},
        {"key": "netDebt",        "label": "Net Debt",               "category": "Balance",   "unit": "$"},
        {"key": "inventory",      "label": "Inventory",              "category": "Balance",   "unit": "$"},
        # Ratios
        {"key": "netMargin",      "label": "Net Margin",             "category": "Ratios",    "unit": "%"},
        {"key": "roe",            "label": "ROE",                    "category": "Ratios",    "unit": "%"},
        {"key": "assetTurnover",  "label": "Asset Turnover",         "category": "Ratios",    "unit": "x"},
        {"key": "leverage",       "label": "Leverage",               "category": "Ratios",    "unit": "x"},
        {"key": "debtToEquity",   "label": "Debt / Equity",          "category": "Ratios",    "unit": "x"},
        # Valuation
        {"key": "per",            "label": "P/E Ratio",              "category": "Valuation", "unit": "x"},
        {"key": "marketCap",      "label": "Market Cap",             "category": "Valuation", "unit": "$"},
    ]

    return {
        "ticker":           ticker,
        "generatedAt":      datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "fiscalDates":      fiscal_dates,
        "chartData":        chart_data,
        "availableMetrics": available_metrics,
        "averages":         averages,
        "growth":           growth,
        "valuation": {
            "currentMarketCap":  current_mcap,
            "currentStockPrice": current_price,
            "per":               per_val,
            "cashPerStock":      cash_per_sh,
            "cashPercent":       cash_pct,
            "boxGroups":         box_groups,
            "peg":               peg,
            "adjustedPeg":       adj_peg,
        },
    }
