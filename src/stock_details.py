from yahoofinancials import YahooFinancials
from yahooquery import Ticker

#retrieve the compnany details to calculate ratios
def get_stock_details_cap(symbol):
    try:
        ticker = Ticker(symbol)
        profile = ticker.asset_profile[symbol]
        summary_detail = ticker.summary_detail[symbol]
        history = ticker.history(period="1d")
        sector = profile["sector"]
        market_cap = summary_detail["marketCap"]
        current_price = history["close"].iloc[-1]
        previous_close = summary_detail.get('previousClose')
        percent_change = None
        
        if previous_close is not None and current_price is not None:
            percent_change = ((current_price - previous_close) / previous_close) * 100
        return sector, market_cap, current_price, percent_change
    except Exception as e:
        print(f"Error retrieving stock cap details for {symbol}: {e}")
        return None
    

#calculate the company ratios
def get_company_fundamentals(symbol):
    try:
        ticker = Ticker(symbol)
        trailing_eps = ticker.key_stats[symbol].get("trailingEps")
        history = ticker.history(period="1d")
        current_price = history["close"].iloc[-1]
        balance_sheet = ticker.balance_sheet(frequency="annual")

         # Store the required values to variables
        total_debt = balance_sheet["TotalDebt"].values[-1]
        total_equity = balance_sheet["StockholdersEquity"].values[-1]
        total_assets = balance_sheet["TotalAssets"].values[-1]
        shares_outstanding = balance_sheet["OrdinarySharesNumber"].values[-1]

        yahoo_financials = YahooFinancials(symbol)
        cash_flow_data = yahoo_financials.get_financial_stmts('annual', 'cash')
        cash_flow_statement = cash_flow_data['cashflowStatementHistory'][symbol]
        year = '2023'
        cash_flow_2023 = []

        for record in cash_flow_statement:
            date = list(record.keys())[0]
            if date.startswith(year):
                for key, value in record.items():
                    cash_flow_2023.append(record[key])

        pb_ratio = None
        if trailing_eps is not None and trailing_eps != 0:
            pe_ratio = current_price / trailing_eps

         # Calculate Debt-to-Equity ratio
        if total_equity is not None and total_equity != 0:
             debt_to_equity = total_debt / total_equity
        else:
             debt_to_equity = None

        # Calculate Price-to-Book (P/B) ratio manually
        book_value_per_share = None
       
        if total_assets != 0:
            book_value_per_share = (total_assets - total_debt) / shares_outstanding

        # Calculate PB/V ratio manually
        if book_value_per_share is not None and book_value_per_share != 0:
            pb_ratio = current_price / book_value_per_share
        
        # Calculate operating_cash_flow
        operating_cash_flow = cash_flow_2023[0]['operatingCashFlow']/10000000 +  cash_flow_2023[0]['financingCashFlow']/10000000 + cash_flow_2023[0]['investingCashFlow']/10000000
        return {
            'stock_symbol': symbol,
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio,
            'debt_to_equity': debt_to_equity,
            'operating_cash_flow': operating_cash_flow
        }
    except Exception as e:
        print(f"Error retrieving fundamentals for {symbol}: {e}")
        return None