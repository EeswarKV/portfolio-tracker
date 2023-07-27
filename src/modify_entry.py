
from src.models import Portfolio, db
from flask import flash
from src.forms import StockForm

#edit the portfolio entry
def edit_portfolio_entry(user, entry_id):
    try:
        # Find the portfolio entry to edit
        entry = Portfolio.query.get(entry_id)
        if entry:
            # Check if the entry belongs to the current user
            if entry.user_id == user.id:
                form = StockForm()
                entry.stock_symbol = form.stock_symbol.data
                entry.entry_price = form.entry_price.data
                entry.stock_quantity = form.stock_quantity.data
                entry.entry_date = form.entry_date.data
                db.session.commit()
                flash('Portfolio entry updated successfully!', 'success')
            else:
                flash('danger: Unauthorized access to edit entry.', 'danger')
        else:
            flash('danger: Portfolio entry not found.', 'danger')
    except Exception as e:
        print(f"Error trying to edit record: {e}")
        return None

#delete the portfolio entry
def delete_portfolio_entry(user, entry_id):
    try:
        # Find the portfolio entry to delete
        entry = Portfolio.query.get(entry_id)
        if entry:
            # Check if the entry belongs to the current user
            if entry.user_id == user.id:
                db.session.delete(entry)
                db.session.commit()
                flash('Portfolio entry deleted successfully!', 'success')
            else:
                flash('danger: Unauthorized access to delete entry.', 'danger')
        else:
            flash('danger: Portfolio entry not found.', 'danger')
    except Exception as e:
        print(f"Error trying to delete record: {e}")
        return None