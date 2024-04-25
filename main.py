import os

import flask
from flask import Flask, session
from flask_login import LoginManager
from functools import wraps
from flask import render_template, redirect

from classes.chess import Chess
from classes.login_form import LoginForm
from classes.register_form import RegisterForm
from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

games = [Chess(i) for i in range(3)]
users_emails = []
refresh_time = 5000


def current_user():
    data = session.get("current_user", None)
    user = None
    if (data is not None):
        user = User(
            name=data["name"],
            about=data["about"],
            email=data["email"]
        )
        if (data["game"] is not None):
            user.game = games[data["game"]]

    return user


def join_cur_user_in_to_game(game):
    user = current_user()
    data = {
        "name": user.name,
        "about": user.about,
        "email": user.email,
        "game": game.id
    }
    session["current_user"] = data


def quit_cur_user_from_game():
    user = current_user()
    if (user.game is not None and user in user.game.users):
        del user.game.users[user.game.users.index(user)]
    else:
        return

    if (not user.game.users):
        user.game.reset_field()

    data = {
        "name": user.name,
        "about": user.about,
        "email": user.email,
        "game": None
    }
    session["current_user"] = data


def login_user(user):
    data = {
        "name": user.name,
        "about": user.about,
        "email": user.email,
        "game": None
    }
    session["current_user"] = data
    users_emails.append(user.email)


def logout_user():
    quit_cur_user_from_game()
    if (current_user().email in users_emails):
        del users_emails[users_emails.index(current_user().email)]
    session["current_user"] = None


def is_cur_user_in_game():
    g = None
    for game in games:
        if (current_user() is not None and current_user() in game.users):
            g = game
            break
    return g


def render_template_new(*args, **kwargs):
    return render_template(*args, **kwargs, user=current_user())


def authorised_only(f):
    @wraps(f)
    def wrapper_f(*args, **kwargs):
        if (current_user() is None):
            return render_template_new("401.html", title="Error 401")
        else:
            return f(*args, **kwargs)

    return wrapper_f


def redirect_if_playing(f):
    @wraps(f)
    def wrapper_f(*args, **kwargs):
        g = is_cur_user_in_game()

        if (g):
            to_game = f"/game/{g.join_key}"
            if (to_game.startswith(flask.request.path)):
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
        if user and user.check_password(form.password.data) and user.email not in users_emails:
            login_user(user)
            return redirect("/user")
        return render_template_new('login.html',
                                   message="Wrong password or login or user is already logged",
                                   form=form)
    return render_template_new('login.html', title='Authorisation', form=form)


@app.route('/register', methods=['GET', 'POST'])
@redirect_if_playing
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if db_sess.query(User).filter(User.email == form.email.data).first():
            form.email.errors.append("Email is already using")
            return render_template_new('register.html', title='Registration', form=form)

        user = User(
            name=form.username.data,
            about=form.about.data,
            email=form.email.data,
            game=None
        )
        user.set_password(form.password.data)
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        login_user(user)
        return redirect("/find_game")
    return render_template_new('register.html', title='Registration', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/index")
@redirect_if_playing
def index():
    return render_template_new("base.html", title="index")


@app.route("/")
@redirect_if_playing
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


@app.route("/game/<int:key>/")
@app.route("/game/<int:key>")
@authorised_only
def game(key):
    g = is_cur_user_in_game()
    if (g):

        to_game = f"/game/{g.join_key}"
        if (flask.request.path != to_game):
            return redirect(to_game)

        return render_template_new("game.html", game=g, update_time=refresh_time)
    else:
        keys = [g.join_key for g in games]
        if (key in keys):
            g = games[keys.index(key)]
            if (not g.player_join(current_user())):
                return redirect("/find_game")
            join_cur_user_in_to_game(g)
            return render_template_new("game.html", game=g, update_time=refresh_time)
        else:
            return render_template_new("access_denied.html", title="Access Denied")


@app.route("/quit_game")
@authorised_only
def quit_game():
    quit_cur_user_from_game()
    return redirect("/find_game")


@app.route("/logout")
@authorised_only
def logout():
    logout_user()
    return redirect("/")


@app.route("/game/<int:key>/choose/<int:i>/<int:j>")
@authorised_only
def choose(key, i, j):
    current_user().game.make_move((i, j))
    return redirect("../..")


def main():
    db_session.global_init("db/tictactoe.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
