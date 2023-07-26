from datetime import timedelta
from src.models import Portfolio, db


# Calculate the start and end dates for the weekly period
def calculate_weekly_performance(entry_date):
    try:
        end_date = entry_date
        start_date = end_date - timedelta(days=7)
        weekly_performance = 0.0

        return weekly_performance
    except Exception as e:
        print(f"Error retrieving weekly perfromance details : {e}")
        return None

# Update portfolio entry details
def update_portfolio_entry(entry_id, form):
    try:
        entry = Portfolio.query.get(entry_id)
        entry.stock_symbol = form.stock_symbol.data
        entry.entry_price = form.entry_price.data
        entry.stock_quantity = form.stock_quantity.data
        entry.entry_date = form.entry_date.data
        db.session.commit()
    except Exception as e:
        print(f"Error while updating portfolio entry details : {e}")
        return None
