import sqlite3
import os
from flask import Flask, render_template, request, g, flash, redirect, url_for
from data_access import DataAccess
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user_login import UserLogin

# config
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'  # session activation, password generated using os-package

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Login to access restricted pages"
login_manager.login_message_category = "success"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().from_db(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Helper function for creating database tables"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """DB connection if not already established"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()  # this variable contains the application context
    return g.link_db


dbase = None


@app.before_request
def before_request():
    """Establishing a database connection before executing a query"""
    global dbase
    db = get_db()
    dbase = DataAccess(db)


@app.teardown_appcontext
def close_db(error):
    """Close the connection to the database, if it was established"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html', menu=dbase.get_menu(), title="Login System")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.get_user_by_email(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            user_login = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(user_login, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))
        flash("Invalid username/password pair", "error")
    return render_template("login.html", menu=dbase.get_menu(), title="Login")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.add_user(request.form['name'], request.form['email'], hash)
            if res:
                flash("You have successfully registered", "success")
                return redirect(url_for('login'))
            else:
                flash("Error adding to database", "error")
        else:
            flash("Fields filled out incorrectly", "error")
    return render_template("register.html", menu=dbase.get_menu(), title="Sign up")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You are logged out", "success")
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return f"""<h1>WELCOM!</h1>
               <u>USER INFO: </u>
               <p>name: {current_user.get_name()}</p>
               <p>ID: {current_user.get_id()}</p>
               <p>E-mail: {current_user.get_email()}</p>
               <p>_____________________________________</p>
               <p><a href="{url_for('logout')}">Logout of profile</a>"""


if __name__ == "__main__":
    app.run(debug=False)
