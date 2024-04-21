from flask import render_template, redirect
from flask_login import login_user

from classes.login_form import LoginForm
from classes.register_form import RegisterForm
from data import db_session
from data.users import User
from main import app


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # logout_user()
    form = RegisterForm()
    # form.hidden_tag()
    # print(form.data.keys())
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = User()
        user.name = form.username.data
        user.about = form.about.data
        user.email = form.email.data
        user.hashed_password = form.password.data
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/user")
    return render_template('register.html', title='Регистрация', form=form)