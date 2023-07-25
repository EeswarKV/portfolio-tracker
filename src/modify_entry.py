
from src.models import Portfolio, StockForm, db
from flask import flash

def get_portfolio_data_for_edit(user, entry_id):
    if user:
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
    else:
        flash('danger: User not found.', 'danger')

def get_portfolio_data_for_delete(user, entry_id):
    if user:
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
    else:
        flash('danger: User not found.', 'danger')