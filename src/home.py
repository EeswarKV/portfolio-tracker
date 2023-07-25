from flask import render_template
from src.models import Portfolio
from src.utils import calculate_weekly_performance


def get_home_data(user):
    is_authenticated = user is not None
    portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
    stocks_data = []
    for entry in portfolio_entries:
        stock_data = {
            'stock_symbol': entry.stock_symbol,
            'weekly_performance': calculate_weekly_performance(entry.entry_date)
        }
        stocks_data.append(stock_data)
    
    return render_template('base.html', is_authenticated=is_authenticated, is_home=True, active_item='home')
