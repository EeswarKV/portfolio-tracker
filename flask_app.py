from flask import Flask, render_template, redirect, url_for, flash, session
from src.models import User, Portfolio, LoginForm, RegistrationForm, db
from src.dashboard import get_portfolio_data
from src.modify_entry import get_portfolio_data_for_edit, get_portfolio_data_for_delete
from src.invest import get_invest_data
from src.login_register import get_user_register, get_user_login, bcrypt
from src.home import get_home_data

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio-analysis.db'
db.init_app(app) 
bcrypt.init_app(app)

#https://pypi.org/project/tradingview-ta/ to get basic analysis
#https://pypi.org/project/yahoofinancials/ to get the financial information
#https://pyfinmod.readthedocs.io/en/latest/basic.html to record financial situation

with app.app_context():
    # Create the tables
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return get_user_login(form)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return get_user_register(form)
    return render_template('register.html', form=form)

@app.route('/invest', methods=['GET', 'POST'])
def invest():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if user:
        return get_invest_data(user)
    flash('danger: User not found.', 'danger')
    return redirect(url_for('invest'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if user:
        return get_home_data(user)
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
    get_portfolio_data_for_delete(user, entry_id)
    return redirect(url_for('invest'))

@app.route('/dashboard')
def dashboard():
    # Retrieve the portfolio data for the current user
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    if user:
        return get_portfolio_data(user)
    flash('danger: User not found.', 'danger')
    return redirect(url_for('invest'))


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
    get_portfolio_data_for_edit(user, entry_id)
    return redirect(url_for('invest'))

@app.route('/google-charts/pie-chart')
def google_pie_chart():
	data = {'GNA' : 184090.00, 'UCOBANK' : 23657.00}
	return render_template('piechart.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
