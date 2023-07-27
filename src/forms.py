from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, validators, SelectField
from wtforms.validators import DataRequired, Email, EqualTo
from src.constants import list_of_country_codes

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_number = StringField('Phone Number', validators=[validators.DataRequired()])
    country_code = SelectField('Country Code', validators=[validators.DataRequired()], choices=list_of_country_codes)
    submit = SubmitField('Register')

class StockForm(FlaskForm):
    stock_symbol = StringField('Stock Symbol', validators=[DataRequired()])
    entry_price = FloatField('Entry Price', validators=[DataRequired()])
    stock_quantity = FloatField('Quantity', validators=[DataRequired()])
    entry_date = DateField('Entry Date', validators=[DataRequired()])
    submit = SubmitField('Add Stock Entry')
