from flask import render_template, redirect, url_for, flash, request
from src.models import Portfolio, db
from datetime import datetime,date
from src.utils import calculate_weekly_performance
from src.forms import RegistrationForm, StockForm
import pandas as pd
from src.constants import list_of_stock_symbols

def get_invest_data(user):
    try:
        if user:
            username = user.username if user else None
            is_authenticated = user is not None
            today = date.today()
            registration_form = RegistrationForm()
            stock_form = StockForm()
            if request.method == 'POST' and stock_form.validate_on_submit():
                # Process the stock input form data
                stock_symbol = stock_form.stock_symbol.data
                entry_price = float(stock_form.entry_price.data)
                stock_quantity = int(stock_form.stock_quantity.data)
                entry_date = datetime.strptime(stock_form.entry_date.data.strftime('%Y-%m-%d'), '%Y-%m-%d')
                portfolio = Portfolio(user_id=user.id, stock_symbol=stock_symbol, entry_price=entry_price, stock_quantity=stock_quantity, entry_date=entry_date)
                db.session.add(portfolio)
                db.session.commit()
                flash('Stock entry added successfully!', 'success')
                return redirect(url_for('invest'))
            portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
            stocks_data = []
            for entry in portfolio_entries:
                stock_data = {
                    'stock_symbol': entry.stock_symbol,
                    'weekly_performance': calculate_weekly_performance(entry.entry_date)
                }
                stocks_data.append(stock_data)
            return render_template('base.html', username=username, is_authenticated=is_authenticated,
                                registration_form=registration_form, stock_form=stock_form,
                                portfolio_entries=portfolio_entries, stocks_data=stocks_data, today=today, active_item='invest',stock_codes=list_of_stock_symbols)
    except Exception as e:
        print(f"Error trying to redirecting to invest page: {e}")
        return redirect(url_for('invest'))
