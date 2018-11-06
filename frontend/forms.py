import flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

## Inherited class from flask_wtf.FlaskForm
class RegistrationForm(FlaskForm):
    ## Setting field label and validators
    username = StringField('Username', validators =
                           [DataRequired(), Length(min = 2, max = 16)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators =
                             [DataRequired(), Length(min = 8, max = 32)])
    confirm_password = PasswordField('Confirm Password', validators =
                                     [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators =
                             [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

