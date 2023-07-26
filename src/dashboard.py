from flask import render_template
from src.models import Portfolio, my_dictionary
from src.stock_details import get_stock_details_cap, get_company_fundamentals

def calculate_allocation(capitalization):
    small_cap = 5000000000
    mid_cap = 70000000000
    large_cap = 200000000000

    if capitalization < small_cap:
        return 'Smallcap'
    elif capitalization < mid_cap:
        return 'Midcap'
    elif capitalization >= large_cap:
        return 'Largecap'
    else:
        return 'Unknown'

def get_portfolio_data(user):
    is_authenticated = user is not None
    stocks_data = []
    total_invested = 0.0
    total_current = 0.0
    total_price = 0.0
    symbol_allocation = my_dictionary()
    sector_allocation = my_dictionary()
    market_cap_allocation = my_dictionary()
    symbol_allocation_current = my_dictionary()
    sector_allocation_current = my_dictionary()
    market_cap_allocation_current = my_dictionary()

    portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
    stocks_symbol = set()
    symbol_occurrences = {}

    for entry in portfolio_entries:
        stock_symbol = entry.stock_symbol
        entry_price = entry.entry_price
        stock_quantity = entry.stock_quantity
        entry_date = entry.entry_date
        total_price += entry_price * stock_quantity
        symbol_occurrences[stock_symbol] = symbol_occurrences.get(stock_symbol, 0) + 1

        sector, market_cap, current_price, percent_change = get_stock_details_cap(stock_symbol + '.NS')
        stock_total = current_price * stock_quantity
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
            existing_stock['change_percentage'] = ((stock_invested - stock_total) / stock_total) * 100
            existing_stock['entry_date'] = entry_date
        else:
            stock_data = {
                'stock_symbol': stock_symbol,
                'entry_price': entry_price,
                'stock_quantity': stock_quantity,
                'entry_date': entry_date,
                'real_time_price': current_price,
                'positive_return': False,
                'stock_invested': stock_invested,
                'average_price': stock_invested / stock_quantity,
                'percent_change':percent_change
            }
            if current_price is not None:
                stock_data['positive_return'] = current_price > entry_price
                stock_data['change_percentage'] = ((stock_invested - stock_total) / stock_total) * 100
            stocks_data.append(stock_data)

        stock_invested = sum(stock['stock_invested'] for stock in stocks_data)

        symbol_allocation.add(stock_symbol, stock_invested)
        symbol_allocation_current.add(stock_symbol, current_price * stock_quantity)

        sector_allocated = sector
        sector_allocation.add(sector_allocated, stock_invested)
        sector_allocation_current.add(sector_allocated, current_price * stock_quantity)

        cap_allocation = calculate_allocation(market_cap)
        market_cap_allocation.add(cap_allocation, stock_invested)
        market_cap_allocation_current.add(cap_allocation, current_price * stock_quantity)

        if current_price is not None:
            total_current += current_price * stock_quantity
        total_invested += stock_invested

    total_percentage = ((total_current - total_price) / total_current) * 100 if total_current != 0 else 0
    dict_obj_new = {
        'StockAllocation': symbol_allocation,
        'SectorAllocation': sector_allocation,
        'MarketCapAllocation': market_cap_allocation,
    }
    dict_obj_current = {
        'StockAllocation': symbol_allocation_current,
        'SectorAllocation': sector_allocation_current,
        'MarketCapAllocation': market_cap_allocation_current,
    }

    stock_fundamentals = [get_company_fundamentals(stock['stock_symbol'] + '.NS') for stock in stocks_data]

    return render_template(
        'base.html',
        analytical_data=stocks_data,
        is_authenticated=is_authenticated,
        is_dashboard=True,
        total_invested=total_price,
        total_current=total_current,
        total_percentage=total_percentage,
        active_item='dashboard',
        chart_datasets=dict_obj_new,
        dict_obj_current=dict_obj_current,
        stock_fundamentals=stock_fundamentals,
    )
