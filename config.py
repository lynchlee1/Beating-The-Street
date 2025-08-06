API_KEY = "" # Enter your FMP API key here
DEFAULT_YEARS_BACK = 20

DEFAULT_PERIODS = [
    ["quarterly", 12], 
    ["quarterly", 20],
    ["annual", 13], 
    ["annual", 20]  
]

TABLE_COLUMN_LABELS = ["3Y/1Y", "5Y/1Y", "10Y/3Y", "13Y/3Y", "20Y/3Y"]
ANALYSIS_TYPES = ["Valuation", "PER Trend", "PER Analysis", "Operations", "Payouts", "Stocks outstanding", "Liquidity&Solvency", "Profitability"]
SUBBUTTONS = ["Quarterly", "Trailing 1Y", "Trailing 3Y"]

PLOT_CONFIGS = {
    "Operations": {
        "Quarterly": {
            "timeframe": "quarterly",
            "ax1_metrics": {
                "revenue": {"label": "Revenue", "color": "tab:red", "zorder": 3},
            },
            "ax2_metrics": {
                "netIncome": {"label": "Net Income", "color": "tab:green", "zorder": 2},
                "netIncomeFromContinuingOperations": {"label": "Continuing Net Income", "color": "tab:green", "zorder": 1, "opacity": 0.5}
            },
            "x_discrete": 4,
            "scale2": 2
        },
        "Trailing 1Y": {
            "ax1_metrics": {
                "revenue_ttm": {"label": "Revenue", "color": "tab:red", "zorder": 3},
            },
            "ax2_metrics": {
                "netIncome_ttm": {"label": "Net Income", "color": "tab:green", "zorder": 2},
                "netIncomeCont_ttm": {"label": "Continuing Net Income", "color": "tab:green", "zorder": 1, "opacity": 0.5}
            },
            "x_discrete": 4,
            "scale2": 2
        },
        "Trailing 3Y": {
            "ax1_metrics": {
                "revenue_ttm_long": {"label": "Revenue", "color": "tab:red", "zorder": 3},
            },
            "ax2_metrics": {
                "netIncome_ttm_long": {"label": "Net Income", "color": "tab:green", "zorder": 2},
                "netIncomeCont_ttm_long": {"label": "Continuing Net Income", "color": "tab:green", "zorder": 1, "opacity": 0.5}
            },
            "x_discrete": 4,
            "scale2": 2
        }
    },
    "Payouts": {
        "Quarterly": {
            "timeframe": "quarterly",
            "ax1_metrics": {
                "eps": {"label": "EPS", "color": "tab:red", "zorder": 1},
            },
            "ax2_metrics": {
                "alignedDividends": {"label": "Dividend", "color": "tab:green", "zorder": 2},
            },
            "x_discrete": 4,
        },
        "Trailing 1Y": {
            "ax1_metrics": {
                "eps_ttm": {"label": "EPS", "color": "tab:red", "zorder": 1},
            },
            "ax2_metrics": {
                "dividends_ttm": {"label": "Dividend", "color": "tab:green", "zorder": 2},
            },
            "x_discrete": 4,
        },
        "Trailing 3Y": {
            "ax1_metrics": {
                "eps_ttm_long": {"label": "EPS", "color": "tab:red", "zorder": 1},
            },
            "ax2_metrics": {
                "dividends_ttm_long": {"label": "Dividend", "color": "tab:green", "zorder": 2},
            },
            "x_discrete": 4,
        },
    },
    "Stocks outstanding": {
        "Quarterly": {
            "timeframe": "quarterly",
            "ax1_metrics": {
                "weightedAverageShsOut": {"label": "Shares Outstanding", "color": "tab:red", "zorder": 1, "opacity": 0.5},
                "weightedAverageShsOutDil": {"label": "Diluted Shares Outstanding", "color": "tab:red", "zorder": 2}
            },
            "x_discrete": 4,
        },
        "Trailing 1Y": {
            "ax1_metrics": {
                "weightedAverageShsOut_ttm": {"label": "Shares Outstanding", "color": "tab:red", "zorder": 1, "opacity": 0.5},
                "weightedAverageShsOutDil_ttm": {"label": "Diluted Shares Outstanding", "color": "tab:red", "zorder": 2}
            },
            "x_discrete": 4,
        },
        "Trailing 3Y": {
            "ax1_metrics": {
                "weightedAverageShsOut_ttm_long": {"label": "Shares Outstanding", "color": "tab:red", "zorder": 1, "opacity": 0.5},
                "weightedAverageShsOutDil_ttm_long": {"label": "Diluted Shares Outstanding", "color": "tab:red", "zorder": 2}
            },
            "x_discrete": 4,
        },
    },
    "Liquidity&Solvency": {
        "Quarterly": {
            "timeframe": "quarterly",
            "ax1_metrics": {
                "cashAndShortTermInvestments": {"label": "Cash", "color": "tab:red", "zorder": 3},
                "longTermDebt": {"label": "Long-term Debt", "color": "tab:orange", "zorder": 2}
            },
            "ax2_metrics": {
                "inventory": {"label": "Inventory", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "auto_scale": 2,
        },
        "Trailing 1Y": {
            "ax1_metrics": {
                "cash_ttm": {"label": "Cash", "color": "tab:red", "zorder": 3},
                "longTermDebt_ttm": {"label": "Long-term Debt", "color": "tab:orange", "zorder": 2}
            },
            "ax2_metrics": {
                "inventory_ttm": {"label": "Inventory", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "auto_scale": 2,
        },
        "Trailing 3Y": {
            "ax1_metrics": {
                "cash_ttm_long": {"label": "Cash", "color": "tab:red", "zorder": 3},
                "longTermDebt_ttm_long": {"label": "Long-term Debt", "color": "tab:orange", "zorder": 2}
            },
            "ax2_metrics": {
                "inventory_ttm_long": {"label": "Inventory", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "auto_scale": 2,
        },
    },
    "Profitability": {
        "Quarterly": {
            "timeframe": "quarterly",
            "ax1_metrics": {
                "netMargin": {"label": "Net Margin", "color": "tab:red", "zorder": 3},
                "roe": {"label": "ROE", "color": "tab:orange", "zorder": 2},
            },
            "ax2_metrics": {
                "leverage": {"label": "Leverage", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "min_margin": 3
        },
        "Trailing 1Y": {
            "ax1_metrics": {
                "netMargin_ttm": {"label": "Net Margin", "color": "tab:red", "zorder": 3},
                "roe_ttm": {"label": "ROE", "color": "tab:orange", "zorder": 2},
            },
            "ax2_metrics": {
                "leverage_ttm": {"label": "Leverage", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "min_margin": 3
        },
        "Trailing 3Y": {
            "ax1_metrics": {
                "netMargin_ttm_long": {"label": "Net Margin", "color": "tab:red", "zorder": 3},
                "roe_ttm_long": {"label": "ROE", "color": "tab:orange", "zorder": 2},
            },
            "ax2_metrics": {
                "leverage_ttm_long": {"label": "Leverage", "color": "tab:green", "zorder": 1},
            },
            "x_discrete": 4,
            "min_margin": 3
        },
    },
}

PER_TREND_CONFIGS = {
    "Quarterly": {
        "ax1_metrics": {"market_cap": {"label": "Market Cap", "color": "tab:red", "zorder": 2}},
        "ax2_metrics": {"per_quarterly": {"label": "PER", "color": "tab:green", "zorder": 1}},
        "x_discrete": 150,
        "marker": "",
        "line_width": 1.0,
        "auto_scale": 2
    },
    "Trailing 1Y": {
        "ax1_metrics": {"market_cap": {"label": "Market Cap", "color": "tab:red", "zorder": 2}},
        "ax2_metrics": {"per_ttm": {"label": "PER", "color": "tab:green", "zorder": 1}},
        "x_discrete": 150,
        "marker": "",
        "line_width": 1.0,
        "auto_scale": 2
    },
    "Trailing 3Y": {
        "ax1_metrics": {"market_cap": {"label": "Market Cap", "color": "tab:red", "zorder": 2}},
        "ax2_metrics": {"per_ttm_long": {"label": "PER", "color": "tab:green", "zorder": 1}},
        "x_discrete": 150,
        "marker": "",
        "line_width": 1.0,
        "auto_scale": 2
    }
}
