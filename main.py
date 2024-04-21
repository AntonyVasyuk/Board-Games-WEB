import flask_login
from flask import Flask, render_template
from flask_login import LoginManager, login_required

from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    return render_template("base.html", title="index")


@app.route("/user")
@login_required
def user():
    return render_template("show_user.html", title="В системе:", user=flask_login.current_user)


@app.route("/find_game")
def find_game():
    pass


from classes.forms_parsers import *


def main():
    db_session.global_init("db/blogs.db")
    app.run(host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()