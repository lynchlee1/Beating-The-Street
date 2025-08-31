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
def query_income_statement(ticker, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/income-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    response_quarterly = requests.get(url_quarterly)
    data_quarterly = response_quarterly.json()
    
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

    return income_statement_quarterly

# 1.4. Define query for balance sheet
def query_balance_sheet(ticker, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    response_quarterly = requests.get(url_quarterly)
    data_quarterly = response_quarterly.json()

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
    
    return balance_sheet_quarterly

# 1.5. Define query for cash flow
def query_cash_flow(ticker, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    response_quarterly = requests.get(url_quarterly)
    data_quarterly = response_quarterly.json()

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
    
    return cash_flow_quarterly

# 1.6. Define query for dividends
def query_dividends(ticker, quarters_back = 80):
    url_quarterly = f"https://financialmodelingprep.com/stable/dividends?symbol={ticker}&apikey={API_KEY}&period=quarterly&limit={quarters_back}"
    response_quarterly = requests.get(url_quarterly)
    data_quarterly = response_quarterly.json()

    dividends_quarterly = {}
    for item in data_quarterly:
        date = item['date']
        if date not in dividends_quarterly:
            dividends_quarterly[date] = {}
        dividends_quarterly[date] = item['adjDividend']
    
    return dividends_quarterly

# 1.7. Define all-call function
def query_all_data(ticker, years_back = 20, quarters_back = 80):    
    data = {}
    data["ticker"] = ticker
    
    income_data = query_income_statement(ticker, quarters_back)
    for date in income_data:
        for metric in income_data[date]:
            if metric not in data:
                data[metric] = {}
            data[metric][date] = income_data[date][metric]

    # Check Data Length Criterion
    if len(data['netIncome']) < 52:
        print(f"Stock {ticker} has less than 13 years of data: {len(data['netIncome'])} quarters found")
        return ["Error 52l", len(data['netIncome'])]

    # Check Net Income Criterion
    income_dates = sorted(income_data.keys())
    recent_12_quarters = income_dates[:12]
    deficit_count = 0
    for date in recent_12_quarters:
        if data['netIncome'][date] < 0: deficit_count += 1
    if deficit_count > 0: 
        print(f"Stock {ticker} has deficit in recent 3 years: total deficit of {deficit_count} quarters")
        return ["Error 12d", deficit_count]
        
    balance_data = query_balance_sheet(ticker, quarters_back)
    for date in balance_data:
        for metric in balance_data[date]:
            if metric not in data:
                data[metric] = {}
            data[metric][date] = balance_data[date][metric]

    cash_flow_data = query_cash_flow(ticker, quarters_back)
    for date in cash_flow_data:
        for metric in cash_flow_data[date]:
            if metric not in data:
                data[metric] = {}
            data[metric][date] = cash_flow_data[date][metric]

    all_dates = set()
    for key in data:
        if isinstance(data[key], dict):
            all_dates.update(data[key].keys())
    all_dates = sorted(list(all_dates))
    data["fiscalDates"] = all_dates

    def _last_quarter_date(date):
        year, month, day = date[0:4], date[5:7], date[8:10]
        if int(month) <= 3:
            year, month = str(int(year) - 1), str(int(month) + 9)
            if len(month) == 1:
                month = "0" + month
            return f"{year}-{month}-{day}"
        else:
            month = str(int(month) - 3)
            if len(month) == 1:
                month = "0" + month
            return f"{year}-{month}-{day}"

    data["dividends"]  = query_dividends(ticker, quarters_back)
    data["stockPrice"] = query_stock_price(ticker, years_back)
    data["marketCap"]  = query_market_cap(ticker, years_back)

    quarterly_dividend_dates = sorted(data["dividends"].keys())
    stock_price_dates        = sorted(data["stockPrice"].keys())
    market_cap_dates         = sorted(data["marketCap"].keys())
    
    data["alignedDividends"]  = {}
    data["alignedStockPrice"] = {}
    data["alignedMarketCap"]  = {}

    first_date = data["fiscalDates"][0]
    total_price, count_price, total_mcap, count_mcap, total_dividend = 0, 0, 0, 0, 0
    for date in stock_price_dates:
        if _last_quarter_date(first_date) <= date < first_date:
            total_price += data["stockPrice"][date]["close"]
            count_price += 1
    for date in market_cap_dates:
        if _last_quarter_date(first_date) <= date < first_date:
            total_mcap += data["marketCap"][date]
            count_mcap += 1
    for date in quarterly_dividend_dates:
        if _last_quarter_date(first_date) <= date < first_date:
            total_dividend += data["dividends"][date]
    
    data["alignedStockPrice"][first_date] = total_price / count_price if count_price > 0 else 0
    data["alignedMarketCap"][first_date] = total_mcap / count_mcap if count_mcap > 0 else 0
    data["alignedDividends"][first_date] = total_dividend

    for i in range(len(data["fiscalDates"])-1):
        current_date = data["fiscalDates"][i]
        next_date = data["fiscalDates"][i+1]

        total_price, count_price, total_mcap, count_mcap, total_dividend = 0, 0, 0, 0, 0

        for date in stock_price_dates:
            if current_date <= date < next_date:
                total_price += data["stockPrice"][date]["close"]
                count_price += 1

        for date in market_cap_dates:
            if current_date <= date < next_date:
                total_mcap += data["marketCap"][date]
                count_mcap += 1

        for date in quarterly_dividend_dates:
            if current_date <= date < next_date:
                total_dividend += data["dividends"][date]        

        data["alignedStockPrice"][next_date] = total_price / count_price if count_price > 0 else 0
        data["alignedMarketCap"][next_date] = total_mcap / count_mcap if count_mcap > 0 else 0
        data["alignedDividends"][next_date] = total_dividend

    dates = sorted(list(data["marketCap"].keys()))
    start_date, end_date = dates[0], dates[-1]
    start, end = datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')
    current_date, prev_value = start, data["marketCap"][start_date]

    data["filledMarketCap"] = {}
    while current_date <= end:
        date_str = current_date.strftime('%Y-%m-%d')
        value = data["marketCap"].get(date_str)
        if value is not None:
            data["filledMarketCap"][date_str] = value
            prev_value = value
        else:
            data["filledMarketCap"][date_str] = prev_value        
        current_date += timedelta(days=1)

    return data
