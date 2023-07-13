from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date, timedelta
import yfinance as yf
from forex_python.converter import CurrencyRates


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio-analysis.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Create your dictionary class
class my_dictionary(dict):
 
    # __init__ function
    def __init__(self):
        self = dict()
         
    # Function to add key:value
    def add(self, key, value):
        self[key] = value

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class StockForm(FlaskForm):
    stock_symbol = StringField('Stock Symbol', validators=[DataRequired()])
    entry_price = FloatField('Entry Price', validators=[DataRequired()])
    stock_quantity = FloatField('Quantity', validators=[DataRequired()])
    entry_date = DateField('Entry Date', validators=[DataRequired()])
    submit = SubmitField('Add Stock Entry')

with app.app_context():
    # Create the tables
    db.create_all()

def calculate_weekly_performance(entry_date):
    # Calculate the start and end dates for the weekly period
    end_date = entry_date
    start_date = end_date - timedelta(days=7)

    # Perform the calculation based on your specific logic
    # Replace this with your own calculation method
    weekly_performance = 0.0

    return weekly_performance

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', 'success')
            session['user_id'] = user.id  # Store the user ID in the session
            return redirect(url_for('home'))  # Redirect to the invest page
        else:
            flash('danger: Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_username = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_username:
            flash('danger: Username already exists. Please choose a different username.')
            return redirect(url_for('register'))
        if existing_email:
            flash('danger: Email already exists. Please choose a different email.')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to the login page

    return render_template('register.html', form=form)

@app.route('/invest', methods=['GET', 'POST'])
def invest():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
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

    if user:
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
                               portfolio_entries=portfolio_entries, stocks_data=stocks_data, today=today, active_item='invest')

    flash('danger: User not found.', 'danger')
    return redirect(url_for('invest'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    is_authenticated = user is not None

    if user:
        portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
        stocks_data = []
        for entry in portfolio_entries:
            stock_data = {
                'stock_symbol': entry.stock_symbol,
                'weekly_performance': calculate_weekly_performance(entry.entry_date)
            }
            stocks_data.append(stock_data)
        
        return render_template('base.html', is_authenticated=is_authenticated, is_home=True, active_item='home')

    flash('danger: User not found.', 'danger')
    return redirect(url_for('invest'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user ID from the session
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))  # Redirect to the login page

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    # Retrieve the current user
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

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

    return redirect(url_for('invest'))

def append_if_not_exists(item, array):
    if item not in array:
        array.append(item)

@app.route('/dashboard')
def dashboard():
    # Retrieve the stocks data for the current user
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    is_authenticated = user is not None
    stocks_data = []
    total_invested = 0.0  # Initialize total invested amount
    total_current = 0.0  # Initialize total current amount
    total_percentage = 0.0  # Initialize total percentage change
    total_price = 0.0
    symbol_allocation = my_dictionary()
    sector_allocation = my_dictionary()
    market_cap_allocation = my_dictionary()
    symbol_allocation_current = my_dictionary()
    sector_allocation_current = my_dictionary()
    market_cap_allocation_current = my_dictionary()

    if user:
        portfolio_entries = Portfolio.query.filter_by(user_id=user.id).all()
        stocks_symbol = []
        stock_invested = 0.0
        average_price = 0.0
        for entry in portfolio_entries:
            stock_symbol = entry.stock_symbol
            entry_price = entry.entry_price
            stock_quantity = entry.stock_quantity
            entry_date = entry.entry_date
            total_price += entry.entry_price * entry.stock_quantity

            if stock_symbol in stocks_symbol: 
                stock_invested += (entry_price * stock_quantity)
                stock_total += get_real_time_price(stock_symbol) * entry.stock_quantity
            else:
                stock_total = get_real_time_price(stock_symbol) * entry.stock_quantity
                stock_invested = entry.entry_price * entry.stock_quantity
                stocks_symbol.append(stock_symbol)

           
            # Check if stock symbol already exists in stocks_data
            existing_stock = next((stock for stock in stocks_data if stock['stock_symbol'] == stock_symbol), None)

            if existing_stock:
                # Update existing stock entry
                existing_stock['entry_price'] += entry_price
                existing_stock['stock_quantity'] += stock_quantity
                existing_stock['stock_invested'] = stock_invested
                existing_stock['average_price'] = stock_invested / existing_stock['stock_quantity']
                existing_stock['change_percentage'] = ((stock_total - stock_invested)/stock_total) * 100
                existing_stock['entry_date'] = entry_date
                
            else:
                stock_data = {
                    'stock_symbol': stock_symbol,
                    'entry_price': entry_price,
                    'stock_quantity': stock_quantity,
                    'entry_date': entry_date,
                    'real_time_price': get_real_time_price(stock_symbol),
                    'positive_return': False,
                    'stock_invested': stock_invested,
                    'average_price' : stock_invested / stock_quantity
                }
                if stock_data['real_time_price'] is not None:
                    stock_data['positive_return'] = stock_data['real_time_price'] > stock_data['entry_price']
                    stock_data['change_percentage'] = ((stock_total - stock_invested)/stock_total) * 100

                stocks_data.append(stock_data)
        

        isStock = ''
        # Calculate total current amount and percentage change
        for stock in stocks_data:
            small_cap = 5000000000
            mid_cap = 70000000000
            large_cap = 200000000000
            stock['current_amount'] = stock['real_time_price'] * stock['stock_quantity']
            total_current += stock['current_amount']
            total_invested += stock['entry_price']
            symbol_allocation.add(stock['stock_symbol'], stock['stock_invested'])
            symbol_allocation_current.add(stock['stock_symbol'], stock['current_amount'])
            ticker = yf.Ticker(stock['stock_symbol']+'.NS')
            sectorAllocated = ticker.info['sector']
            capitalization = ticker.info['marketCap']
            sector_allocation.add(sectorAllocated, stock['stock_invested'])
            sector_allocation_current.add(sectorAllocated, stock['current_amount'])
            
            if capitalization < small_cap:
                isStock = 'Smallcap'
            elif capitalization > small_cap and capitalization < mid_cap:
                isStock = 'Midcap'
            elif capitalization > large_cap:
                isStock = 'Largecap'
            else:
                isStock = 'Unknown'
            
            market_cap_allocation.add(isStock, stock['stock_invested'])
            market_cap_allocation_current.add(isStock, stock['current_amount'])
        
        print("capitalization", market_cap_allocation)
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
        if total_current != 0:
            total_percentage = ((total_current - total_price) / total_current) * 100

        return render_template('base.html', analytical_data=stocks_data, is_authenticated=is_authenticated, is_dashboard=True,
                               total_invested=total_price, total_current=total_current, total_percentage=total_percentage, active_item='dashboard', chart_datasets=dict_obj_new, dict_obj_current = dict_obj_current)
    
    flash('danger: User not found.', 'danger')
    return redirect(url_for('invest'))

def get_real_time_price(stock_symbol):
    # Fetch real-time price using yfinance
    ticker = yf.Ticker(stock_symbol+'.NS')
    data = ticker.history(period="1d")  # Fetch historical data for 1 day
    real_time_price = round(data["Close"][-1], 2) if not data.empty else None

    # Convert USD to INR
    c = CurrencyRates()
    real_time_price_inr = c.convert("USD", "INR", real_time_price) if real_time_price else None

    return real_time_price

@app.route('/clear_table', methods=['POST'])
def clear_table():
    # Retrieve the current user
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

    if user:
        # Delete all portfolio entries associated with the user
        Portfolio.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        flash('Portfolio table cleared successfully!', 'success')
    else:
        flash('danger: User not found.', 'danger')

    return redirect(url_for('invest'))

@app.route('/edit_entry/<int:entry_id>', methods=['POST'])
def edit_entry(entry_id):
    # Retrieve the current user
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None

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

    return redirect(url_for('invest'))

@app.route('/google-charts/pie-chart')
def google_pie_chart():
	data = {'GNA' : 184090.00, 'UCOBANK' : 23657.00}
	return render_template('piechart.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
