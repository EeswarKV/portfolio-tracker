from flask import Flask, render_template, redirect, url_for, session
from src.models import User, db
from src.dashboard import get_portfolio_data
from src.modify_entry import edit_portfolio_entry, delete_portfolio_entry
from src.invest import get_invest_data
from src.login_register import get_user_register, get_user_login, bcrypt
from src.home import get_home_data
from functools import wraps
from src.forms import LoginForm, RegistrationForm

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config.Config')
db.init_app(app) 
bcrypt.init_app(app)

# Create the tables
with app.app_context():
    db.create_all()

#decorator to check if user logged in and returns user if successful
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        if user is None:
            return redirect(url_for('login'))
        return f(user, *args, **kwargs)
    return decorated_function

#login route returns to login template
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            return get_user_login(form)
        return render_template('login.html', form=form)
    except Exception as e:
        print(f"Error trying to login: {e}")
        return None

#returns to log template once registration successful
@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            return get_user_register(form)
        return render_template('register.html', form=form)
    except Exception as e:
        print(f"Error trying to register: {e}")
        return None
    
#returns to invest template to record investments 
@app.route('/invest', methods=['GET', 'POST'])
@login_required
def invest(user):
    try:
        return get_invest_data(user)
    except Exception as e:
        print(f"Error trying to redirecting to invest page: {e}")
        return None
    
#returns to home template
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home(user):
    try:
        return get_home_data(user)
    except Exception as e:
        print(f"Error trying to redirecting to home page: {e}")
        return None
    
#returns dashboard template
@app.route('/dashboard')
@login_required
def dashboard(user):
    try:
        # Retrieve the portfolio data for the current user
        return get_portfolio_data(user)
    except Exception as e:
        print(f"Error trying to redirecting to dashboard: {e}")
        return None
    
@app.route('/edit_entry/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(user, entry_id):
    return handle_entry_action(user, edit_portfolio_entry, entry_id)

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(user, entry_id):
    return handle_entry_action(user, delete_portfolio_entry, entry_id)

def handle_entry_action(user, action_function, entry_id):
    try:
        action_function(user, entry_id)
        return redirect(url_for('invest'))  # Redirect to the dashboard
    except Exception as e:
        print(f"Error trying to perform action on entry: {e}")
        return "Error", 500  # Return an error message


#returns to login template once logout succesful
@app.route('/logout')
def logout():
    try:
        session.pop('user_id', None)  # Remove the user ID from the session
        return redirect(url_for('login')) 
    except Exception as e:
        print(f"Error trying to logout: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
