from datetime import timedelta
from src.models import Portfolio, db

def calculate_weekly_performance(entry_date):
    # Calculate the start and end dates for the weekly period
    end_date = entry_date
    start_date = end_date - timedelta(days=7)

    # Perform the calculation based on your specific logic
    # Replace this with your own calculation method
    weekly_performance = 0.0

    return weekly_performance


def update_portfolio_entry(entry_id, form):
    entry = Portfolio.query.get(entry_id)
    entry.stock_symbol = form.stock_symbol.data
    entry.entry_price = form.entry_price.data
    entry.stock_quantity = form.stock_quantity.data
    entry.entry_date = form.entry_date.data
    db.session.commit()
