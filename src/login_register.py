from flask import redirect, url_for, flash, session
from src.models import User, db
from flask_bcrypt import Bcrypt
from src.communication import registration_message

#intializing the password hashing function from flask_bcrypt
bcrypt = Bcrypt()

#get user registration details
def get_user_register(form):
    try:
        existing_username = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_username:
            flash('danger: Username already exists. Please choose a different username.')
            return redirect(url_for('register'))
        if existing_email:
            flash('danger: Email already exists. Please choose a different email.')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, username=form.username.data, password=hashed_password, phone_number=form.phone_number.data, country_code=form.country_code.data)
        db.session.add(user)
        db.session.commit()
        registration_message(user.country_code + user.phone_number, user.email)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to the login page
    except Exception as e:
        print(f"Error trying to register: {e}")
        flash('There was an error trying to register. Please try again.', 'danger')
        return redirect(url_for('register'))

#get user login details
def get_user_login(form):
    try:
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', 'success')
            session['user_id'] = user.id  # Store the user ID in the session
            return redirect(url_for('home'))  # Redirect to the home page
        else:
            flash('danger: Invalid email or password.', 'danger')
            return redirect(url_for('login'))  # Redirect back to the login page
    except Exception as e:
        print(f"Error trying to login: {e}")
        flash('There was an error trying to login. Please try again.', 'danger')
        return redirect(url_for('login'))
