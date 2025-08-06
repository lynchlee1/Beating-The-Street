from importlib import reload
import json
import os
import time

from utilitylib import safe_average_dict, digit_formatter, inv_digit_formatter
from btsdesignlib import create_table, create_row
from btsplotlib import plot_trailing_bands, plot_trailing_data, calc_trailing_data, plot_box_whisker
from config import TVBLUE, TVDARKGREEN, TVGREEN, TVLIGHTBLUE, TVORANGE, TVBLACK, TVWHITE, TVLIGHTBLUE


def _load_2image2table(image_uris, table):
    return {
        "Quarterly": {
            "s1": {"type": "img", "src": image_uris[0]["1Q"]},
            "s2": table[0],
            "s3": {"type": "img", "src": image_uris[1]["1Q"]},
            "s4": table[1],
        },
        "Trailing 1Y": {
            "s1": {"type": "img", "src": image_uris[0]["4Q"]},
            "s2": table[0],
            "s3": {"type": "img", "src": image_uris[1]["4Q"]},
            "s4": table[1],
        },
        "Trailing 3Y": {
            "s1": {"type": "img", "src": image_uris[0]["12Q"]},
            "s2": table[0],
            "s3": {"type": "img", "src": image_uris[1]["12Q"]},
            "s4": table[1],
        },
    }

def create_html(data):
    ticker = data["ticker"]

    # Create tables
    revenue_table = create_table([
        {"label": "Revenue", "num1_dict": data["revenue"], "g_row": True},
        {"label": "Continuous Net Income", "num1_dict": data["netIncomeFromContinuingOperations"], "g_row": True},
        {"label": "Net Income", "num1_dict": data["netIncome"], "g_row": True},
    ])
    payout_table = create_table([
        {"label": "EPS", "num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOut"], "order": (-1, 1), "g_row": True},
        {"label": "DEPS", "num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOutDil"], "order": (-1, 1), "g_row": True},
        {"label": "Dividends", "num1_dict": data["alignedDividends"], "zero_on_none": True},
        {"label": "Dividend Yield", "num1_dict": data["alignedDividends"], "den1_dict": data["alignedStockPrice"], "order": (-1, 1), "unit": "%"},
        {"label": "Payout Ratio", "num1_dict": data["alignedDividends"], "num2_dict": data["weightedAverageShsOut"], "den1_dict": data["netIncome"], "order": (1, 0), "unit": "%"}
    ])
    stocks_outstanding_table = create_table([
        {"label": "Shares Outstanding", "num1_dict": data["weightedAverageShsOut"], "order": (1, 0), "g_row": True},
        {"label": "Diluted Shares Outstanding", "num1_dict": data["weightedAverageShsOutDil"], "order": (1, 0), "g_row": True},
    ])
    cashflow_table = create_table([
        {"label": "Free Cash Flow", "num1_dict": data["freeCF"]},
        {"label": "CFO", "num1_dict": data["CFO"]},
        {"label": "CFF", "num1_dict": data["CFF"]},
    ])
    liquidity_solvency_table = create_table([
        {"label": "Cash & Equivalents", "num1_dict": data["cashAndShortTermInvestments"], "order": (1, 0), "g_row": True},
        {"label": "Long Term Debt", "num1_dict": data["longTermDebt"], "order": (1, 0), "g_row": True},
        {"label": "Net Debt", "num1_dict": data["netDebt"], "order": (1, 0), "g_row": True},
        {"label": "Debt to Equity", "num1_dict": data["totalDebt"], "den1_dict": data["totalStockholdersEquity"]},
        {"label": "Inventory", "num1_dict": data["inventory"], "order": (1, 0)},
    ])
    capital_structure_table = create_table([
        {"label": "Net Margin", "num1_dict": data["netIncome"], "den1_dict": data["revenue"]},
        {"label": "ROE", "num1_dict": data["netIncome"], "den1_dict": data["totalStockholdersEquity"], "order": (-1, 1)},
        {"label": "Asset Turnover", "num1_dict": data["revenue"], "den1_dict": data["totalAssets"], "order": (-1, 0)},
        {"label": "Leverage", "num1_dict": data["totalAssets"], "den1_dict": data["totalStockholdersEquity"]}
    ])
    
    # Create plots
    revenue_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "Revenue", "num1_dict": data["revenue"], "color": TVBLUE},
            {"label": "Continuous Net Income", "num1_dict": data["netIncomeFromContinuingOperations"], "color": TVDARKGREEN},
            {"label": "Net Income", "num1_dict": data["netIncome"], "color": TVGREEN},
        ],
        "ax2_configs": [
            {"label": "Dividends", "num1_dict": data["alignedDividends"], "color": TVORANGE, "zero_on_none": True}
        ],
        "scale2": 0.5,
    })
    payout_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "EPS", "num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOut"], "color": TVBLUE, "order": (-1, 1)},
            {"label": "DEPS", "num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOutDil"], "color": TVLIGHTBLUE, "order": (-1, 1)},
        ],
        "ax2_configs": [
            {"label": "Dividends", "num1_dict": data["alignedDividends"], "color": TVORANGE, "zero_on_none": True}
        ],
        "scale2": 0.5,
    })
    stocks_outstanding_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "Shares Outstanding", "num1_dict": data["weightedAverageShsOut"], "color": TVBLUE, "order": (1, 0)},
            {"label": "Diluted Shares Outstanding", "num1_dict": data["weightedAverageShsOutDil"], "color": TVLIGHTBLUE, "order": (1, 0)},
        ],
    })
    cashflow_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "Free Cash Flow", "num1_dict": data["freeCF"], "color": TVBLUE},
            {"label": "CFO", "num1_dict": data["CFO"], "color": TVLIGHTBLUE},
            {"label": "CFF", "num1_dict": data["CFF"], "color": TVGREEN},
        ],
    })
    liquidity_solvency_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "Cash & Equivalents", "num1_dict": data["cashAndShortTermInvestments"], "color": TVBLUE, "order": (1, 0), "zero_on_none": True},
            {"label": "Long Term Debt", "num1_dict": data["longTermDebt"], "color": TVGREEN, "order": (1, 0), "zero_on_none": True},
        ],
        "ax2_configs": [
            {"label": "Inventory", "num1_dict": data["inventory"], "color": TVORANGE, "order": (1, 0), "zero_on_none": True}
        ],
        "scale2": 0.5,
    })
    capital_structure_plots  = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "ax1_configs": [
            {"label": "Net Margin", "num1_dict": data["netIncome"], "den1_dict": data["revenue"], "color": TVBLUE, "order": (0, 0)},
            {"label": "ROE", "num1_dict": data["netIncome"], "den1_dict": data["totalStockholdersEquity"], "color": TVGREEN, "order": (-1, 1)},
        ],
        "ax2_configs": [
            {"label": "Leverage", "num1_dict": data["totalAssets"], "den1_dict": data["totalStockholdersEquity"], "color": TVORANGE, "order": (0, 0)},
        ],
        "scale2": 0.5,
    })

    band_plots = plot_trailing_bands({
        "line_dict": data["marketCap"],
        "area_dict": data["netIncome"],
        "x_discrete": 180,
        "y_grid_ticks": 6,
        "order": (0, 1),
        "amplifier": 1
    })
    per_plots = plot_trailing_data({
        "sum_dates": data["fiscalDates"],
        "axis_dates": sorted(list(data["filledMarketCap"].keys())),
        "ax1_configs": [
            {"label": "PER", "num1_dict": data["filledMarketCap"], "den1_dict": data["netIncome"], "color": TVBLUE, "order": (1, -1)},
        ],
        "ax2_configs": [
            {"label": "Market Cap", "num1_dict": data["filledMarketCap"], "color": TVORANGE, "order": (1, 0), "disable_trailing": True}
        ],
        "x_discrete": 210,
    })

    configs = {
        "Net Income": {"num1_dict": data["netIncome"]},
        "Div x Shares": {"num1_dict": data["alignedDividends"], "num2_dict": data["weightedAverageShsOut"], "order": (1, 1)},
        "Shares": {"num1_dict": data["weightedAverageShsOut"], "order": (1, 0)},
        "DEPS": {"num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOutDil"], "order": (-1, 1)},
        "Dividends": {"num1_dict": data["alignedDividends"]},
        "Payout": {"num1_dict": data["alignedDividends"], "num2_dict": data["weightedAverageShsOut"], "den1_dict": data["netIncome"], "order": (1, 0)},
        "PER": {"num1_dict": data["alignedMarketCap"], "den1_dict": data["netIncome"], "order": (1, -1)}
    }
    averages = {}
    for name, config in configs.items():
        averages[name] = {}
        period_config = config.copy()
        period_config["sum_dates"] = data["fiscalDates"]
        period_config["trailing_length"] = 1
        period_data = calc_trailing_data(period_config)
        averages[name] = period_data
    averages_float = {}
    for metric in averages:
        averages_float[metric] = []
        for length in [12, 20, 40, 52, 80]:
            result = safe_average_dict(averages[metric], sorted(list(averages[metric].keys()))[-length:])
            averages_float[metric].append(result)
    valuation_result = {"Net Income": [], "EPS": [], "PY": []}
    for i in range(5):
        valuation_result["Net Income"].append(0.3333 * averages_float["Net Income"][i] + averages_float["Div x Shares"][i])
        valuation_result["EPS"].append(averages_float["Shares"][i] * (0.3333 * averages_float["DEPS"][i] + averages_float["Dividends"][i]))
        valuation_result["PY"].append(averages_float["Net Income"][i] * (0.3333 + averages_float["Payout"][i]))
    box_plot_groups = {
        "3Y":  {"Net Income": valuation_result["Net Income"][0], "EPS": valuation_result["EPS"][0], "PY": valuation_result["PY"][0]},
        "5Y":  {"Net Income": valuation_result["Net Income"][1], "EPS": valuation_result["EPS"][1], "PY": valuation_result["PY"][1]},
        "10Y": {"Net Income": valuation_result["Net Income"][2], "EPS": valuation_result["EPS"][2], "PY": valuation_result["PY"][2]},
        "13Y": {"Net Income": valuation_result["Net Income"][3], "EPS": valuation_result["EPS"][3], "PY": valuation_result["PY"][3]},
        "20Y": {"Net Income": valuation_result["Net Income"][4], "EPS": valuation_result["EPS"][4], "PY": valuation_result["PY"][4]},
    }
    market_cap = data["marketCap"][sorted(data["marketCap"].keys())[-1]]
    box_uri = plot_box_whisker(
        groups=box_plot_groups,
        current_market_cap=market_cap,
    )

    per = 0.25 * data["marketCap"][sorted(list(data["marketCap"].keys()))[-1]] / safe_average_dict(data["netIncome"], sorted(list(data["netIncome"].keys()))[-12:])
    per_formatted = digit_formatter(per, "")
    _, deps_grow       = create_row({"label": "DEPS Growth", "num1_dict": data["netIncome"], "den1_dict": data["weightedAverageShsOutDil"], "order": (-1, 1), "unit": "%", "g_row": True})
    _, net_income_grow = create_row({"label": "Net Income Growth", "num1_dict": data["netIncome"], "unit": "%", "g_row": True})
    _, shares_grow     = create_row({"label": "Diluted Shares Change", "num1_dict": data["weightedAverageShsOutDil"], "order": (1, 0), "unit": "%", "g_row": True})
    div_yield_row, _   = create_row({"label": "Dividend Yield", "num1_dict": data["alignedDividends"], "den1_dict": data["alignedStockPrice"], "order": (-1, 1), "unit": "%"})

    netCash = -data["netDebt"][sorted(list(data["netDebt"].keys()))[-1]]
    diluted_shares = data["weightedAverageShsOutDil"][sorted(list(data["weightedAverageShsOutDil"].keys()))[-1]]
    stockPrice = data["stockPrice"][sorted(list(data["stockPrice"].keys()))[-1]]["close"]
    netCashPerStock = digit_formatter(netCash / diluted_shares, "")
    netCashPercent = digit_formatter(netCash / diluted_shares / stockPrice, "", unit="%")
    if netCash / diluted_shares > 0:
        cash_info_text = "$" + netCashPerStock + " (" + netCashPercent + ")"
    else:
        cash_info_text = "-"
        
    # Calculate (EPS Growth + Div Yield) / PER
    peg_ratio = []
    for i in range(5):
        try:
            peg = 100 * (inv_digit_formatter(deps_grow[i]) + inv_digit_formatter(div_yield_row[i])) / per
            peg_ratio.append(f"{peg:.2f}")
        except:
            peg_ratio.append("N/A")
    adjusted_peg_ratio = []
    for i in range(5):
        try:
            if netCash > 0:
                adjusted_peg = 100 * (inv_digit_formatter(deps_grow[i]) + inv_digit_formatter(div_yield_row[i])) / per / inv_digit_formatter(netCashPercent)
                adjusted_peg_ratio.append(f"{adjusted_peg:.2f}")
            else:
                adjusted_peg_ratio.append("-")
        except:
            adjusted_peg_ratio.append("N/A")

    peg_table = {
        "type": "table",
        "title": "",
        "columns": ["" for i in range(6)],
        "rows": [
            ['', '3Y', '5Y', '10Y', '13Y', '20Y'],
            ["Cash per Stock", cash_info_text, "", "", "", ""],
            ["PER"] + [per_formatted for _ in range(5)],
            ["DEPS Growth"] + deps_grow, 
            ["\tNet Income Growth"] + net_income_grow,
            ["\tDiluted Shares Growth"] + shares_grow,
            ["Dividend Yield"] + div_yield_row,
            ["PEG Ratio"] + peg_ratio,
            ["adjusted PEG Ratio"] + adjusted_peg_ratio
        ],
    } 

    payload = {
        "ticker": ticker,
        "config": {
            "Valuation": {
                "Quarterly": {
                    "s1": {"type": "img", "src": band_plots["1Q"]},
                    "s2": {"type": "img", "src": box_uri},
                    "s3": {"type": "img", "src": per_plots["1Q"]},
                    "s4": peg_table,
                },
                "Trailing 1Y": {
                    "s1": {"type": "img", "src": band_plots["4Q"]},
                    "s2": {"type": "img", "src": box_uri},
                    "s3": {"type": "img", "src": per_plots["4Q"]},
                    "s4": peg_table,
                },
                "Trailing 3Y": {
                    "s1": {"type": "img", "src": band_plots["12Q"]},
                    "s2": {"type": "img", "src": box_uri},
                    "s3": {"type": "img", "src": per_plots["12Q"]},
                    "s4": peg_table,
                },
            },
            "Operations": _load_2image2table([revenue_plots, payout_plots], [revenue_table, payout_table]),
            "Financial Stability": _load_2image2table([stocks_outstanding_plots, cashflow_plots], [stocks_outstanding_table, cashflow_table]),
            "Capital Structure": _load_2image2table([liquidity_solvency_plots, capital_structure_plots], [liquidity_solvency_table, capital_structure_table]),
        }
    }
    color_map = {
        "BG": TVBLACK,
        "PANEL": TVBLACK,
        "TEXT": TVWHITE,
        "ACCENT": TVLIGHTBLUE,
    }
    call_script = f"""
<script>
  window.loadDashboardData({json.dumps(payload)}, {{ activeMain: "Sample Plots", activeSub: "Scenario A" }});
</script>
"""
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            html_template = f.read()
        
        # Replace placeholders with actual color values
        for key, value in color_map.items():
            html_template = html_template.replace(f"{{{{{key}}}}}", value)

        timestamp = int(time.time())
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        report_path = os.path.join("reports", f"report_{ticker}_{timestamp}.html")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_template + call_script)
            
        print(f"Successfully created '{report_path}'.")
    except FileNotFoundError:
        print("Error: 'dashboard.html' not found. Please ensure the template file is in the same directory.")
