import wtforms
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = wtforms.StringField("Username", validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password again', validators=[DataRequired(), wtforms.validators.equal_to("password", "Пароль должен совпадать")])
    about = wtforms.TextAreaField('About')
    submit = SubmitField('Sign in')