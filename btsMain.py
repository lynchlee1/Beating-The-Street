from importlib import reload
import fmpQuery
reload(fmpQuery)
from fmpQuery import query_all_data, check_criteria

import config
reload(config)
from config import PLOT_CONFIGS, PER_TREND_CONFIGS, TABLE_COLUMN_LABELS, ANALYSIS_TYPES, SUBBUTTONS

import btsPlot
reload(btsPlot)
from btsPlot import plot_metrics, extract_image_src, plot_valuation_bands, get_column, get_average_value, plot_box_whisker

import btsAppend
reload(btsAppend)
from btsAppend import append_per_ttm, append_trailing_value, append_metrics, append_metrics_price

import generate_interactive_report
reload(generate_interactive_report)
from generate_interactive_report import generate_interactive_report

# Main execution gpk, ingr
tickers = ["AAPL"]

for ticker in tickers:
    length, black_count = check_criteria(ticker, 20)
    if length < 20:
        print(ticker, ": Insufficient length")
        continue
    elif black_count < 15:
        print(ticker, ": Insufficient profit") 
        continue

    try:
        data = query_all_data(ticker)

        append_per_ttm(data, "per_quarterly", 1)
        append_per_ttm(data, "per_ttm", 4)
        append_per_ttm(data, "per_ttm_long", 12)

        append_trailing_value(data, data, {"label": "revenue_ttm"     , "num1": "revenue", "trailing_period": 4})
        append_trailing_value(data, data, {"label": "revenue_ttm_long", "num1": "revenue", "trailing_period": 12})

        append_trailing_value(data, data, {"label": "netIncome_ttm"     , "num1": "netIncome", "trailing_period": 4})
        append_trailing_value(data, data, {"label": "netIncome_ttm_long", "num1": "netIncome", "trailing_period": 12})

        append_trailing_value(data, data, {"label": "netIncomeCont_ttm"     , "num1": "netIncomeFromContinuingOperations", "trailing_period": 4})
        append_trailing_value(data, data, {"label": "netIncomeCont_ttm_long", "num1": "netIncomeFromContinuingOperations", "trailing_period": 12})

        append_trailing_value(data, data, {"label": "eps_ttm"     , "num1": "netIncome", "den1": "weightedAverageShsOutDil", "trailing_period": 4, "amplifier": 4})
        append_trailing_value(data, data, {"label": "eps_ttm_long", "num1": "netIncome", "den1": "weightedAverageShsOutDil", "trailing_period": 12, "amplifier": 4})

        append_trailing_value(data, data, {"label": "dividends_ttm"     , "num1": "alignedDividends", "trailing_period": 4})
        append_trailing_value(data, data, {"label": "dividends_ttm_long", "num1": "alignedDividends", "trailing_period": 12})

        append_trailing_value(data, data, {"label": "weightedAverageShsOut_ttm"     , "num1": "weightedAverageShsOut", "trailing_period": 4, "amplifier": 1/4})
        append_trailing_value(data, data, {"label": "weightedAverageShsOut_ttm_long", "num1": "weightedAverageShsOut", "trailing_period": 12, "amplifier": 1/12})

        append_trailing_value(data, data, {"label": "weightedAverageShsOutDil_ttm"     , "num1": "weightedAverageShsOutDil", "trailing_period": 4, "amplifier": 1/4})
        append_trailing_value(data, data, {"label": "weightedAverageShsOutDil_ttm_long", "num1": "weightedAverageShsOutDil", "trailing_period": 12, "amplifier": 1/12})

        append_trailing_value(data, data, {"label": "cash_ttm"     , "num1": "cashAndShortTermInvestments", "trailing_period": 4, "amplifier": 1/4})
        append_trailing_value(data, data, {"label": "cash_ttm_long", "num1": "cashAndShortTermInvestments", "trailing_period": 12, "amplifier": 1/12})

        append_trailing_value(data, data, {"label": "longTermDebt_ttm"     , "num1": "longTermDebt", "trailing_period": 4, "amplifier": 1/4})
        append_trailing_value(data, data, {"label": "longTermDebt_ttm_long", "num1": "longTermDebt", "trailing_period": 12, "amplifier": 1/12})

        append_trailing_value(data, data, {"label": "inventory_ttm"     , "num1": "inventory", "trailing_period": 4, "amplifier": 1/4})
        append_trailing_value(data, data, {"label": "inventory_ttm_long", "num1": "inventory", "trailing_period": 12, "amplifier": 1/12})

        append_trailing_value(data, data, {"label": "netMargin_ttm"     , "num1": "netIncome", "den1": "revenue", "trailing_period": 4})
        append_trailing_value(data, data, {"label": "netMargin_ttm_long", "num1": "netIncome", "den1": "revenue", "trailing_period": 12})

        append_trailing_value(data, data, {"label": "roe_ttm"     , "num1": "netIncome", "den1": "totalStockholdersEquity", "trailing_period": 4, "amplifier": 4})
        append_trailing_value(data, data, {"label": "roe_ttm_long", "num1": "netIncome", "den1": "totalStockholdersEquity", "trailing_period": 12, "amplifier": 4})

        append_trailing_value(data, data, {"label": "leverage_ttm"     , "num1": "totalAssets", "den1": "totalStockholdersEquity", "trailing_period": 4, "amplifier": 1})
        append_trailing_value(data, data, {"label": "leverage_ttm_long", "num1": "totalAssets", "den1": "totalStockholdersEquity", "trailing_period": 12, "amplifier": 1})

        append_metrics(data, {"label": "eps", "num1": "netIncome", "den1": "weightedAverageShsOutDil"})
        append_metrics(data, {"label": "netMargin", "num1": "netIncome", "den1": "revenue"})
        append_metrics(data, {"label": "roe", "num1": "netIncome", "den1": "totalStockholdersEquity", "amplifier": 4})
        append_metrics(data, {"label": "leverage", "num1": "totalAssets", "den1": "totalStockholdersEquity"})
        append_metrics(data, {"label": "assetTurnover", "num1": "revenue", "den1": "totalAssets", "amplifier": 4})
        append_metrics(data, {"label": "debtToEquity", "num1": "totalDebt", "den1": "totalStockholdersEquity"})
        append_metrics(data, {"label": "payoutRatio", "num1": "alignedDividends", "num2": "weightedAverageShsOut", "den1": "netIncome"})
        append_metrics(data, {"label": "paidDividends", "num1": "alignedDividends", "num2": "weightedAverageShsOut"})
        append_metrics(data, {"label": "currentRatio", "num1": "totalCurrentAssets", "den1": "totalCurrentLiabilities"})
        append_metrics(data, {"label": "inventoryRatio", "num1": "inventory", "den1": "totalCurrentLiabilities"})
        data["quickRatio"] = {"quarterly": {}}
        for key in data["currentRatio"]["quarterly"].keys():
            try:
                data["quickRatio"]["quarterly"][key] = data["currentRatio"]["quarterly"][key] - data["inventoryRatio"]["quarterly"][key]
            except:
                data["quickRatio"]["quarterly"][key] = None
        append_metrics(data, {"label": "cashRatio", "num1": "cashAndShortTermInvestments", "den1": "totalCurrentLiabilities"})
        append_metrics_price(data, {"label": "dividendYield", "num1": "alignedDividends", "num2": "weightedAverageShsOut", "market_cap_pos": "den"})

        per_band_config = {
            "Quarterly": {
                "base_dict": data["netIncome"]["quarterly"],
                "x_discrete": 200,
                "marker": "",
                "line_width": 1.0,
                "auto_scale": 2,
                "amplifier": 4
            },
            "Trailing 1Y": {
                "base_dict": data["netIncome_ttm"],
                "x_discrete": 200,
                "marker": "",
                "line_width": 1.0,
                "auto_scale": 2
            },
            "Trailing 3Y": {
                "base_dict": data["netIncome_ttm_long"],
                "x_discrete": 200,
                "marker": "",
                "line_width": 1.0,
                "auto_scale": 2
            }
        }

        images = {}
        subbutton_labels = {}

        def get_average_values(dict, amplifier=1):
            lengths = [12, 15, 40, 52, 80]
            value3y = get_average_value(dict, lengths[0], amplifier)
            value5y = get_average_value(dict, lengths[1], amplifier)
            value10y = get_average_value(dict, lengths[2], amplifier)
            value13y = get_average_value(dict, lengths[3], amplifier)
            value20y = get_average_value(dict, lengths[4], amplifier)

            return [value3y, value5y, value10y, value13y, value20y]

        # Comapany value = Net income and Dividends : Standard valuation method
        valuation_netIncome = get_average_values(data["netIncome"]["quarterly"], amplifier=4)
        valuation_paidDividends = get_average_values(data["paidDividends"]["quarterly"], amplifier=4)

        # Comapany value = EPS and Dividends per stock : Accounting for rapid Shares outstanding changes
        valuation_eps = get_average_values(data["eps"]["quarterly"], amplifier=4)
        valuation_dividends = get_average_values(data["alignedDividends"]["quarterly"], amplifier=4)

        # Comapany value = Payout ratio and Net income : Accounting for rapid change in Payout ratio
        valuation_payoutRatio = get_average_values(data["payoutRatio"]["quarterly"], amplifier=4)

        def safe_calc_list(list1, list2, multiplier=1/3, amplifier=1):
            if list1 is None:
                list1 = [1 for _ in range(len(list2))]
            if list2 is None:
                list2 = [1 for _ in range(len(list1))]
            
            list_result = []
            for i in range(len(list1)):
                if list1[i] is None or list2[i] is None:
                    list_result.append(None)
                else:
                    list_result.append((list1[i] * multiplier + list2[i]) * amplifier)

            return list_result

        valuation1 = safe_calc_list(valuation_netIncome, valuation_paidDividends)
        mult_shares = get_average_value(data["weightedAverageShsOut"]["quarterly"], 12)
        valuation2 = safe_calc_list(valuation_eps, valuation_dividends, amplifier=mult_shares)
        mult_netIncome = get_average_value(data["netIncome"]["quarterly"], 12)
        valuation3 = safe_calc_list(None, valuation_payoutRatio, amplifier=mult_netIncome)
        data_list = valuation1 + valuation2 + valuation3
        market_cap = data["market_cap"][sorted(data["market_cap"].keys())[-1]]
        labels = ["3Y", "5Y", "10Y", "13Y", "20Y", 
                "3Y", "5Y", "10Y", "13Y", "20Y",
                "3Y", "5Y", "10Y", "13Y", "20Y"]
        valuation_image = extract_image_src(plot_box_whisker(data_list, labels=labels, n_groups=3, m_elements=5, market_cap=market_cap))

        images["Valuation_Quarterly"] = valuation_image
        images["Valuation_Trailing 1Y"] = valuation_image
        images["Valuation_Trailing 3Y"] = valuation_image

        images["PER Trend_Quarterly"] = extract_image_src(plot_metrics(data, PER_TREND_CONFIGS["Quarterly"]))
        images["PER Analysis_Quarterly"] = extract_image_src(plot_valuation_bands(data, per_band_config["Quarterly"]))

        images["PER Trend_Trailing 1Y"] = extract_image_src(plot_metrics(data, PER_TREND_CONFIGS["Trailing 1Y"]))
        images["PER Analysis_Trailing 1Y"] = extract_image_src(plot_valuation_bands(data, per_band_config["Trailing 1Y"]))

        images["PER Trend_Trailing 3Y"] = extract_image_src(plot_metrics(data, PER_TREND_CONFIGS["Trailing 3Y"]))
        images["PER Analysis_Trailing 3Y"] = extract_image_src(plot_valuation_bands(data, per_band_config["Trailing 3Y"]))

        for analysis_type in ANALYSIS_TYPES:
            for subbutton in SUBBUTTONS:
                key = f"{analysis_type}_{subbutton}"
                if key not in images:
                    images[key] = extract_image_src(plot_metrics(data, PLOT_CONFIGS[analysis_type][subbutton]))
                subbutton_labels[subbutton] = subbutton

        # Create plot_configs
        plot_configs = {
            "images": images,
            "subbutton_labels": subbutton_labels
        }

        analysis_configs = {
            "images": images,
            "subbutton_labels": {
                "sub1": SUBBUTTONS[0],
                "sub2": SUBBUTTONS[1],
                "sub3": SUBBUTTONS[2],
            }
        }



        def fill_table(analysis_type):
            metrics = []
            growth = []
            if analysis_type == "Valuation":
                metrics = [
                    get_column(data["netIncome"]["quarterly"], "Net Income", amplifier=4),
                    get_column(data["paidDividends"]["quarterly"], "Total Dividends", amplifier=4),
                    get_column(data["eps"]["quarterly"], "EPS", amplifier=4),
                    get_column(data["alignedDividends"]["quarterly"], "Dividends per share", amplifier=4),
                    get_column(data["payoutRatio"]["quarterly"], "Payout Ratio", format="%"),
                    get_column(data["weightedAverageShsOut"]["quarterly"], "Shares Outstanding"),
                    get_column(data["weightedAverageShsOutDil"]["quarterly"], "Diluted Shares Outstanding"),
                ]

                growth = []

            elif analysis_type == "PER Trend":
                metrics = []

                growth = []
            
            elif analysis_type == "PER Analysis":
                metrics = []

                growth = []

            elif analysis_type == "Operations":
                metrics = [
                    get_column(data["revenue"]["quarterly"], "Revenue", amplifier=4),
                    get_column(data["netIncomeFromContinuingOperations"]["quarterly"], "Cont. Net Income", amplifier=4),
                    get_column(data["netIncome"]["quarterly"], "Net Income", amplifier=4)
                ]
                
                growth = [
                    get_column(data["revenue"]["quarterly"], "Revenue Growth", mode="growth"),
                    get_column(data["netIncomeFromContinuingOperations"]["quarterly"], "Cont. Net Income Growth", mode="growth"),
                    get_column(data["netIncome"]["quarterly"], "Net Income Growth", mode="growth")
                ]

            elif analysis_type == "Payouts":
                metrics = [
                    get_column(data["eps"]["quarterly"], "EPS", amplifier=4),
                    get_column(data["alignedDividends"]["quarterly"], "Dividend", amplifier=4),
                    get_column(data["dividendYield"]["quarterly"], "Dividend Yield", amplifier=4, format="%"),
                    get_column(data["payoutRatio"]["quarterly"], "Payout Ratio", format="%")
                ]
                
                growth = [
                    get_column(data["eps"]["quarterly"], "EPS Growth", mode="growth"),
                    get_column(data["dividends"]["quarterly"], "Dividends Growth", mode="growth"),
                ]
            
            elif analysis_type == "Stocks outstanding":
                metrics = [
                    get_column(data["weightedAverageShsOut"]["quarterly"], "Shares Outstanding"),
                    get_column(data["weightedAverageShsOutDil"]["quarterly"], "Diluted Shares Outstanding"),
                ]

                growth = [
                    get_column(data["weightedAverageShsOut"]["quarterly"], "Shares Growth", mode="growth"),
                    get_column(data["weightedAverageShsOutDil"]["quarterly"], "Diluted Shares Growth", mode="growth"),
                ]

            elif analysis_type == "Liquidity&Solvency":
                metrics = [
                    get_column(data["cashAndShortTermInvestments"]["quarterly"], "Cash & Equivalents"),
                    get_column(data["longTermDebt"]["quarterly"], "Long Term Debt"),
                    get_column(data["shortTermDebt"]["quarterly"], "Short Term Debt"),
                    get_column(data["netDebt"]["quarterly"], "Net Debt"),
                ]

                growth = [            
                    get_column(data["debtToEquity"]["quarterly"], "Debt to Equity"),
                    get_column(data["currentRatio"]["quarterly"], "Current Ratio"),
                    get_column(data["quickRatio"]["quarterly"], "Quick Ratio"),
                    get_column(data["cashRatio"]["quarterly"], "Cash Ratio"),
                ]
            
            elif analysis_type == "Profitability":
                metrics = [
                    get_column(data["roe"]["quarterly"], "ROE"),
                    get_column(data["netMargin"]["quarterly"], "Net Margin"),
                    get_column(data["assetTurnover"]["quarterly"], "Asset Turnover"),
                    get_column(data["leverage"]["quarterly"], "Leverage"),
                ]
                
                growth = [
                ]
            
            return {"metrics": metrics, "growth": growth}


        # Define flexible table column labels (different from subbutton labels)

        # Generate table data
        table_data = {}

        # Generate table data for each analysis type
        for analysis_type in ANALYSIS_TYPES:
            table_data[analysis_type] = fill_table(analysis_type)

        html_content = generate_interactive_report(ticker, analysis_configs, table_data, TABLE_COLUMN_LABELS)
        # Create reports directory if it doesn't exist
        import os
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        # Generate filename with ticker and date
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{reports_dir}/{ticker}_report_{timestamp}.html'

        with open(filename, 'w') as f:
            f.write(html_content)

        print(f"\nCompany report generated: {filename}")

    except:
        print(ticker, ": Error generating report")
        continue
