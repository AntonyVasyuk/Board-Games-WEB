import wtforms
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = wtforms.StringField("Псевдоним", validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Введите пароль еще раз', validators=[DataRequired(), wtforms.validators.equal_to("password", "Пароль должен совпадать")])
    about = wtforms.TextAreaField('Информация')
    submit = SubmitField('Зарегистрироваться')