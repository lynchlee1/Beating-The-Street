import requests
from datetime import datetime, timedelta
from config import API_KEY

# 1.1. Define query for stock price
# {date: {close: float, volume: int}}
def query_stock_price(ticker, years_back = 20):
    today = datetime.now()
    end_date = (today - timedelta(days=0)).strftime('%Y-%m-%d')
    begin_date = (today - timedelta(days=365*years_back)).strftime('%Y-%m-%d')
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={begin_date}&to={end_date}&apikey={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    stock_price_data = {}
    for item in data['historical']:
        date = item['date']
        if date not in stock_price_data:
            stock_price_data[date] = {}
        stock_price_data[date]['close'] = item['close']
        stock_price_data[date]['volume'] = item['volume']
    return stock_price_data


# 1.2. Define query for market cap
# {date: marketCap}
def query_market_cap(ticker, years_back = 20):
    query_size = 5
    query_count = years_back // query_size
    market_cap_data = {}
    
    today = datetime.now()
    begin_date = (today - timedelta(days=365*years_back)).strftime('%Y-%m-%d')
    url = f"https://financialmodelingprep.com/stable/historical-market-capitalization?symbol={ticker}&from={begin_date}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
        
    for item in data:
        date = item['date']
        if date not in market_cap_data:
            market_cap_data[date] = {}
        market_cap_data[date] = item['marketCap']
    
    return market_cap_data


# 1.3. Define query for income statement
# {date: {revenue: float, operatingIncome: float, netIncomeFromContinuingOperations: float, netIncome: float, eps: float, epsDiluted: float, weightedAverageShsOut: float, weightedAverageShsOutDil: float}}
def query_income_statement(ticker, years_back = 20, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    url_annual = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&apikey={API_KEY}&period=annual&limit={years_back}"
    response_quarterly = requests.get(url_quarterly)
    response_annual = requests.get(url_annual)
    data_quarterly = response_quarterly.json()
    data_annual = response_annual.json()
    
    income_statement_quarterly = {}
    for item in data_quarterly:
        date = item['date']
        if date not in income_statement_quarterly:
            income_statement_quarterly[date] = {}
        income_statement_quarterly[date]['revenue'] = item['revenue']
        income_statement_quarterly[date]['operatingIncome'] = item['operatingIncome']
        income_statement_quarterly[date]['netIncomeFromContinuingOperations'] = item['netIncomeFromContinuingOperations']
        income_statement_quarterly[date]['netIncome'] = item['netIncome']
        income_statement_quarterly[date]['eps'] = item['eps']
        income_statement_quarterly[date]['epsDiluted'] = item['epsDiluted']
        income_statement_quarterly[date]['weightedAverageShsOut'] = item['weightedAverageShsOut']
        income_statement_quarterly[date]['weightedAverageShsOutDil'] = item['weightedAverageShsOutDil']

    income_statement_annual = {}
    for item in data_annual:
        date = item['date']
        if date not in income_statement_annual:
            income_statement_annual[date] = {}
        income_statement_annual[date]['revenue'] = item['revenue']
        income_statement_annual[date]['operatingIncome'] = item['operatingIncome']
        income_statement_annual[date]['netIncomeFromContinuingOperations'] = item['netIncomeFromContinuingOperations']
        income_statement_annual[date]['netIncome'] = item['netIncome']
        income_statement_annual[date]['eps'] = item['eps']
        income_statement_annual[date]['epsDiluted'] = item['epsDiluted']
        income_statement_annual[date]['weightedAverageShsOut'] = item['weightedAverageShsOut']
        income_statement_annual[date]['weightedAverageShsOutDil'] = item['weightedAverageShsOutDil']
    return {
        "quarterly": income_statement_quarterly,
        "annual": income_statement_annual
    }


# 1.4. Define query for balance sheet
# {date: {cashAndShortTermInvestments: float, inventory: float, totalCurrentAssets: float, totalAssets: float, shortTermDebt: float, totalCurrentLiabilities: float, longTermDebt: float, totalLiabilities: float, totalStockholdersEquity: float, totalEquity: float, totalDebt: float, netDebt: float}}
def query_balance_sheet(ticker, years_back = 20, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    url_annual = f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&apikey={API_KEY}&period=annual&limit={years_back}"
    response_quarterly = requests.get(url_quarterly)
    response_annual = requests.get(url_annual)
    data_quarterly = response_quarterly.json()
    data_annual = response_annual.json()

    balance_sheet_quarterly = {}
    for item in data_quarterly:
        date = item['date']
        if date not in balance_sheet_quarterly:
            balance_sheet_quarterly[date] = {}
        balance_sheet_quarterly[date]['cashAndShortTermInvestments'] = item['cashAndShortTermInvestments']
        balance_sheet_quarterly[date]['inventory'] = item['inventory']
        balance_sheet_quarterly[date]['totalCurrentAssets'] = item['totalCurrentAssets']
        balance_sheet_quarterly[date]['totalAssets'] = item['totalAssets']
        balance_sheet_quarterly[date]['shortTermDebt'] = item['shortTermDebt']
        balance_sheet_quarterly[date]['totalCurrentLiabilities'] = item['totalCurrentLiabilities']
        balance_sheet_quarterly[date]['longTermDebt'] = item['longTermDebt']
        balance_sheet_quarterly[date]['totalLiabilities'] = item['totalLiabilities']
        balance_sheet_quarterly[date]['totalStockholdersEquity'] = item['totalStockholdersEquity']
        balance_sheet_quarterly[date]['totalEquity'] = item['totalEquity']
        balance_sheet_quarterly[date]['totalDebt'] = item['totalDebt']
        balance_sheet_quarterly[date]['netDebt'] = item['netDebt']
    
    balance_sheet_annual = {}
    for item in data_annual:
        date = item['date']
        if date not in balance_sheet_annual:
            balance_sheet_annual[date] = {}
        balance_sheet_annual[date]['cashAndShortTermInvestments'] = item['cashAndShortTermInvestments']
        balance_sheet_annual[date]['inventory'] = item['inventory']
        balance_sheet_annual[date]['totalCurrentAssets'] = item['totalCurrentAssets']
        balance_sheet_annual[date]['totalAssets'] = item['totalAssets']
        balance_sheet_annual[date]['shortTermDebt'] = item['shortTermDebt']
        balance_sheet_annual[date]['totalCurrentLiabilities'] = item['totalCurrentLiabilities']
        balance_sheet_annual[date]['longTermDebt'] = item['longTermDebt']
        balance_sheet_annual[date]['totalLiabilities'] = item['totalLiabilities']
        balance_sheet_annual[date]['totalStockholdersEquity'] = item['totalStockholdersEquity']
        balance_sheet_annual[date]['totalEquity'] = item['totalEquity']
        balance_sheet_annual[date]['totalDebt'] = item['totalDebt']
        balance_sheet_annual[date]['netDebt'] = item['netDebt']
    return {
        "quarterly": balance_sheet_quarterly,
        "annual": balance_sheet_annual
    }


# 1.5. Define query for cash flow
# {date: {netCashProvidedByOperatingActivities: float, netCashProvidedByInvestingActivities: float, netDebtIssuance: float, netStockIssuance: float, netCashProvidedByFinancingActivities: float, freeCashFlow: float}}
def query_cash_flow(ticker, years_back = 20, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    url_annual = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&apikey={API_KEY}&period=annual&limit={years_back}"
    response_quarterly = requests.get(url_quarterly)
    response_annual = requests.get(url_annual)
    data_quarterly = response_quarterly.json()
    data_annual = response_annual.json()

    cash_flow_quarterly = {}
    for item in data_quarterly:
        date = item['date']
        if date not in cash_flow_quarterly:
            cash_flow_quarterly[date] = {}
        cash_flow_quarterly[date]['CFO'] = item['netCashProvidedByOperatingActivities']
        cash_flow_quarterly[date]['CFI'] = item['netCashProvidedByInvestingActivities']
        cash_flow_quarterly[date]['CFF'] = item['netCashProvidedByFinancingActivities']
        cash_flow_quarterly[date]['freeCF'] = item['freeCashFlow']
        cash_flow_quarterly[date]['netStockIssuance'] = item['netStockIssuance']
    
    cash_flow_annual = {}
    for item in data_annual:
        date = item['date']
        if date not in cash_flow_annual:
            cash_flow_annual[date] = {}
        cash_flow_annual[date]['CFO'] = item['netCashProvidedByOperatingActivities']
        cash_flow_annual[date]['CFI'] = item['netCashProvidedByInvestingActivities']
        cash_flow_annual[date]['CFF'] = item['netCashProvidedByFinancingActivities']
        cash_flow_annual[date]['freeCF'] = item['freeCashFlow']
        cash_flow_annual[date]['netStockIssuance'] = item['netStockIssuance']
    return {
        "quarterly": cash_flow_quarterly,
        "annual": cash_flow_annual
    }


# 1.6. Define query for dividends
# {date: dividend}
def query_dividends(ticker, years_back = 20, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/dividends?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    url_annual = f"https://financialmodelingprep.com/stable/dividends?symbol={ticker}&apikey={API_KEY}&period=annual&limit={years_back}"
    response_quarterly = requests.get(url_quarterly)
    response_annual = requests.get(url_annual)
    data_quarterly = response_quarterly.json()
    data_annual = response_annual.json()

    dividends_quarterly = {}
    for item in data_quarterly:
        date = item['date']
        if date not in dividends_quarterly:
            dividends_quarterly[date] = {}
        dividends_quarterly[date] = item['adjDividend']
    
    dividends_annual = {}
    for item in data_annual:
        date = item['date']
        if date not in dividends_annual:
            dividends_annual[date] = {}
        dividends_annual[date] = item['adjDividend']
    return {
        "quarterly": dividends_quarterly,
        "annual": dividends_annual
    }


# 1.7. Define all-call function
def query_all_data(ticker, years_back = 20, quarters_back = 80):
    data = {}
    
    data["ticker"] = ticker

    stock_price_data = query_stock_price(ticker, years_back)
    data["stock_price"] = stock_price_data
        
    market_cap_data = query_market_cap(ticker, years_back)
    data["market_cap"] = market_cap_data
        
    income_data = query_income_statement(ticker, years_back, quarters_back)
    for date in income_data["quarterly"]:
        for metric in income_data["quarterly"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}
                data[metric]["annual"] = {}
            data[metric]["quarterly"][date] = income_data["quarterly"][date][metric]
    for date in income_data["annual"]:
        for metric in income_data["annual"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}
                data[metric]["annual"] = {}
            data[metric]["annual"][date] = income_data["annual"][date][metric]
        
    balance_data = query_balance_sheet(ticker, years_back, quarters_back)
    for date in balance_data["quarterly"]:
        for metric in balance_data["quarterly"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}
                data[metric]["annual"] = {}
            data[metric]["quarterly"][date] = balance_data["quarterly"][date][metric]
    for date in balance_data["annual"]:
        for metric in balance_data["annual"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}
                data[metric]["annual"] = {}
            data[metric]["annual"][date] = balance_data["annual"][date][metric]

    cash_flow_data = query_cash_flow(ticker, years_back, quarters_back)
    for date in cash_flow_data["quarterly"]:
        for metric in cash_flow_data["quarterly"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}
                data[metric]["annual"] = {}
            data[metric]["quarterly"][date] = cash_flow_data["quarterly"][date][metric]
    for date in cash_flow_data["annual"]:
        for metric in cash_flow_data["annual"][date]:
            if metric not in data:
                data[metric] = {}
                data[metric]["quarterly"] = {}

    dividend_data = query_dividends(ticker, years_back, quarters_back)
    data["dividends"] = {
        "quarterly": dividend_data["quarterly"],
        "annual": dividend_data["annual"]
    }

    # Align dividends and market cap to fiscal dates
    quarterly_fiscal_dates = sorted(data["netIncome"]["quarterly"].keys())
    annual_fiscal_dates = sorted(data["netIncome"]["annual"].keys())
    quarterly_dividend_dates = sorted(data["dividends"]["quarterly"].keys())
    annual_dividend_dates = sorted(data["dividends"]["annual"].keys())
    market_cap_dates = sorted(data["market_cap"].keys())

    data["alignedDividends"] = {}
    data["alignedMarketCap"] = {}

    data["alignedDividends"]["quarterly"] = {}
    data["alignedDividends"]["annual"] = {}
    data["alignedMarketCap"]["quarterly"] = {}
    data["alignedMarketCap"]["annual"] = {}

    for i in range(len(quarterly_fiscal_dates)-1):
        current_date = quarterly_fiscal_dates[i]
        next_date = quarterly_fiscal_dates[i+1]

        total_dividend = 0
        total_market_cap = 0
        count_market_cap = 0

        for date in quarterly_dividend_dates:
            if current_date <= date < next_date:
                total_dividend += data["dividends"]["quarterly"][date]

        for date in market_cap_dates:
            if current_date <= date < next_date:
                total_market_cap += data["market_cap"][date]
                count_market_cap += 1

        data["alignedDividends"]["quarterly"][next_date] = total_dividend
        data["alignedMarketCap"]["quarterly"][next_date] = total_market_cap / count_market_cap if count_market_cap > 0 else 0

    for i in range(len(annual_fiscal_dates)-1):
        current_date = annual_fiscal_dates[i]
        next_date = annual_fiscal_dates[i+1]
    
        total_dividend = 0
        total_market_cap = 0
        count_market_cap = 0

        for date in quarterly_dividend_dates:
            if current_date <= date < next_date:
                total_dividend += data["dividends"]["quarterly"][date]

        for date in market_cap_dates:
            if current_date <= date < next_date:
                total_market_cap += data["market_cap"][date]
                count_market_cap += 1

        data["alignedDividends"]["annual"][next_date] = total_dividend
        data["alignedMarketCap"]["annual"][next_date] = total_market_cap / count_market_cap if count_market_cap > 0 else 0
    
    return data


# 1.8. Define function to check Net Income criteria
def check_criteria(ticker, total_count):
    url = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&apikey={API_KEY}&period=annual&limit={total_count}"
    response = requests.get(url)
    data_annual = response.json()
    
    black_count = 0
    for i in range(len(data_annual)):
        if data_annual[i]["netIncome"] > 0:
            black_count += 1

    return len(data_annual), black_count
