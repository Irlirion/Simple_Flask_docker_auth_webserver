from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from resources.validators import Email, Password


class LoginForm(FlaskForm):
    """Default login form"""
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    """Default registration form"""
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired(),
                                                     # Password()
                                                     ])


class DBForm(FlaskForm):
    text = StringField('text', validators=[DataRequired()])
