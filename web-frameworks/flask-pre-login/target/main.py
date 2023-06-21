from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

login_manager = LoginManager()
login_manager.init_app(app)

balance = {}
balance['alice'] = 1000
balance['bob'] = 1000
balance['john_doe'] = 1000
balance['attacker'] = 1000


class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username
        self.balance = balance[username]

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(id):
    return User(id)


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    username  = StringField('UserName', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class TransferForm(FlaskForm):
    ammount  = IntegerField('Ammount', validators=[DataRequired()])
    target = StringField('Target', validators=[DataRequired()])


@app.route('/')
def index():
    return render_template('index.html', form=TransferForm())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and form.username.data == form.password.data and form.username.data in balance.keys():
        login_user(User(form.username.data))
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/transfer', methods=['POST'])
def csrf():
    form = TransferForm()
    if not form.validate_on_submit():
        return "Invalid Transaction."
    elif not current_user.is_authenticated:
        return "Please login first."
    elif form.target.data not in balance.keys():
        return f"User {form.target.data} does not exist."
    else:
        balance[form.target.data] += form.ammount.data
        balance[current_user.username] -= form.ammount.data
        print(f"Executing Transfer {form.ammount.data} from {current_user.username} to {form.target.data}")
        return f"Successfull transferred {form.ammount.data} from {current_user.username} to {form.target.data}"


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
