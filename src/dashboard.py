from src.models import Portfolio, my_dictionary
from src.stock_details import get_stock_details_cap, get_company_fundamentals
from flask import render_template, redirect, url_for, flash


SMALL_CAP = 5000000000
MID_CAP = 70000000000
LARGE_CAP = 200000000000

#categorise market capitalization
def calculate_allocation(capitalization):
    try:
        if capitalization < SMALL_CAP:
            return 'Smallcap'
        elif capitalization < MID_CAP:
            return 'Midcap'
        elif capitalization >= LARGE_CAP:
            return 'Largecap'
        else:
            return 'Unknown'
    except Exception as e:
        print(f"Error trying to calculate market capitalization: {e}")
        return None

#return stock related data object
def create_stock_data(stock_symbol, entry_price, stock_quantity, entry_date, current_price, stock_invested):
    try:
        stock_data = {
            'stock_symbol': stock_symbol,
            'entry_price': entry_price,
            'stock_quantity': stock_quantity,
            'entry_date': entry_date,
            'real_time_price': current_price,
            'positive_return': False,
            'stock_invested': stock_invested,
            'average_price': stock_invested / stock_quantity,
            'percent_change': 0 if current_price is None else ((stock_invested - (current_price * stock_quantity)) / (current_price * stock_quantity)) * 100
        }
        if current_price is not None:
            stock_data['positive_return'] = current_price > entry_price
        return stock_data
    except Exception as e:
        print(f"Error trying to create stock data: {e}")
        return None

#generate stock related data
def prepare_stocks_data(portfolio_entries):
    try:
        stocks_data = []
        total_price = 0.0
        stocks_symbol = set()
        symbol_occurrences = {}

        for entry in portfolio_entries:
            stock_symbol = entry.stock_symbol
            entry_price = entry.entry_price
            stock_quantity = entry.stock_quantity
            entry_date = entry.entry_date
            total_price += entry_price * stock_quantity
            symbol_occurrences[stock_symbol] = symbol_occurrences.get(stock_symbol, 0) + 1
            _, _, current_price, _ = get_stock_details_cap(stock_symbol + '.NS')
            stock_invested = entry_price * stock_quantity
            if stock_symbol in stocks_symbol:
                stock_invested += (entry_price * stock_quantity)
            else:
                stocks_symbol.add(stock_symbol)
            existing_stock = next((stock for stock in stocks_data if stock['stock_symbol'] == stock_symbol), None)
            if existing_stock:
                existing_stock['entry_price'] += entry_price
                existing_stock['stock_quantity'] += stock_quantity
                existing_stock['average_price'] = existing_stock['entry_price'] / symbol_occurrences[stock_symbol]
                existing_stock['stock_invested'] = existing_stock['average_price'] * existing_stock['stock_quantity']
            else:
                stock_data = create_stock_data(stock_symbol, entry_price, stock_quantity, entry_date, current_price, stock_invested)
                stocks_data.append(stock_data)

        return stocks_data, total_price
    except Exception as e:
        print(f"Error trying to prepare stock data: {e}")
        return None

#generate stock related allocation to draw charts
def calculate_allocations(stocks_data):
    try:
        total_current, total_invested = 0.0, 0.0
        allocations = {name: my_dictionary() for name in ['symbol', 'sector', 'market_cap', 'symbol_current', 'sector_current', 'market_cap_current']}
        for data in stocks_data:
            stock_symbol = data['stock_symbol']
            current_price = data['real_time_price']
            stock_quantity = data['stock_quantity']
            sector, market_cap, _, _ = get_stock_details_cap(stock_symbol + '.NS')

            stock_invested = data['stock_invested']

            allocations["symbol"].add(stock_symbol, stock_invested)
            allocations["symbol_current"].add(stock_symbol, current_price * stock_quantity)

            sector_allocated = sector
            allocations["sector"].add(sector_allocated, stock_invested)
            allocations["sector_current"].add(sector_allocated, current_price * stock_quantity)

            cap_allocation = calculate_allocation(market_cap)
            allocations["market_cap"].add(cap_allocation, stock_invested)
            allocations["market_cap_current"].add(cap_allocation, current_price * stock_quantity)

            if current_price is not None:
                total_current += current_price * stock_quantity
            total_invested += stock_invested

        dict_obj_new = {
            'StockAllocation': allocations["symbol"],
            'SectorAllocation': allocations["sector"],
            'MarketCapAllocation': allocations["market_cap"],
        }
        dict_obj_current = {
            'StockAllocation': allocations["symbol_current"],
            'SectorAllocation': allocations["sector_current"],
            'MarketCapAllocation': allocations["market_cap_current"],
        }

        return total_current, total_invested, dict_obj_new, dict_obj_current
    except Exception as e:
        print(f"Error trying to prepare stock data: {e}")
        return None


#generate all portfolio information
def get_portfolio_data(user):
    try:
        if user:
            portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
            stocks_data, total_price = prepare_stocks_data(portfolio_entries)
            total_current, total_invested, dict_obj_new, dict_obj_current = calculate_allocations(stocks_data)
            total_percentage = ((total_current - total_price) / total_current) * 100 if total_current != 0 else 0
            stock_fundamentals = [get_company_fundamentals(stock['stock_symbol'] + '.NS') for stock in stocks_data]

            return render_template(
                'base.html',
                analytical_data=stocks_data,
                is_authenticated=user is not None,
                is_dashboard=True,
                total_invested=total_price,
                total_current=total_current,
                total_percentage=total_percentage,
                active_item='dashboard',
                chart_datasets=dict_obj_new,
                dict_obj_current=dict_obj_current,
                stock_fundamentals=stock_fundamentals,
            ) 
        else:
            return redirect(url_for('login')) # Redirect to the login page if user is None
    except Exception as e:
        print(f"Error trying to redirecting to dashboard: {e}")
        return redirect(url_for('invest')) # Redirect to the invest page in case of any exception
