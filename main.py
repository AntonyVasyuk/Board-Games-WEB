import flask
import flask_login
import werkzeug
from flask import Flask, render_template
from flask_login import LoginManager, AnonymousUserMixin
from functools import wraps
import flask_login
from flask import render_template, redirect
from flask_login import login_user

from classes.login_form import LoginForm
from classes.register_form import RegisterForm
from data import db_session
from data.users import User

from classes.game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

games = [Game(i) for i in range(1, 4)]
refresh_time = 1000


def is_cur_user_in_game():
    g = None
    for game in games:
        if (flask_login.current_user in game.players):
            g = game
            break
    return g


def render_template_new(*args, **kwargs):
    return render_template(*args, **kwargs, user=flask_login.current_user)


def authorised_only(f):
    @wraps(f)
    def wrapper_f(*args, **kwargs):
        if (not flask_login.current_user.is_authenticated):
            return render_template_new("401.html", title="Error 401")
        else:
            return f(*args, **kwargs)
    return wrapper_f


def redirect_if_playing(f):
    @wraps(f)
    def wrapper_f(*args, **kwargs):
        g = is_cur_user_in_game()

        if (g):
            to_game = f"/game/{g.join_code}"
            print(flask.request.path)
            if (flask.request.path != to_game):
                # pass
                return redirect(to_game)
        else:
            return f(*args, **kwargs)
    return wrapper_f


@app.route('/login', methods=['GET', 'POST'])
@redirect_if_playing
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/user")
        return render_template_new('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template_new('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
@redirect_if_playing
def register():
    # logout_user()
    form = RegisterForm()
    # form.hidden_tag()
    # print(form.data.keys())
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            form.email.errors.append("Введенный email уже используется")
            return render_template_new('register.html', title='Регистрация', form=form)

        user = User(
            name=form.username.data,
            about=form.about.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/find_game")
    return render_template_new('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/index")
@redirect_if_playing
def index():
    return render_template_new("base.html", title="index")

@app.route("/")
@authorised_only
# @redirect_if_playing
def main_page():
    return render_template_new("main.html", title="Main page")


@app.route("/user")
@authorised_only
@redirect_if_playing
def user():
    return render_template_new("show_user.html", title="Logged in:")


@app.route("/find_game")
@redirect_if_playing
@authorised_only
def find_game():
    return render_template_new("find_game.html", title="Find game", games=games, update_time=refresh_time)


@app.route("/game/<int:key>")
@authorised_only
# @redirect_if_playing
def game(key):
    g = is_cur_user_in_game()
    if (g):

        to_game = f"/game/{g.join_code}"
        print(flask.request.path)
        if (flask.request.path != to_game):
            return redirect(to_game)

        # return "1"
        return render_template_new("game.html", game=g)
    else:
        keys = [g.join_code for g in games]
        if (key in keys):
            g = games[keys.index(key)]
            if (not g.player_join(flask_login.current_user)):
                return redirect("/find_game")
            # print(g.players[0].email)
            # return "2"
            return render_template_new("game.html", game=g)
        else:
            # print('***')
            # return "3"
            return render_template_new("access_denied.html", title="Access Denied")


@app.route("/logout")
@authorised_only
# @redirect_if_playing
def logout():
    flask_login.logout_user()
    return redirect("./")


# from classes.forms_parsers import *


def main():
    db_session.global_init("db/tictactoe.db")
    app.run(host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
