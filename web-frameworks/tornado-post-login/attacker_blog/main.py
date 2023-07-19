from flask import Flask, render_template, make_response, redirect, url_for
from flask_talisman import Talisman
from bs4 import BeautifulSoup
import requests
import os, ssl


#### EDIT
csrf_cookie_name = '_xsrf'
csrf_form_id = '_xsrf'
csrf_form_name = '_xsrf'
#### /EDIT


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

PROTOCOL = os.environ['PROTOCOL']
if PROTOCOL == 'https':
    ssl._create_default_https_context = ssl._create_unverified_context
    Talisman(app)

values = {}
values['csrf_form_name'] = csrf_form_name


@app.route('/')
def index():
    return render_template('index.html', values = values, protocol = PROTOCOL)


@app.route('/set_post_session/')
def post_session():
    global values

    r = requests.get(f'{PROTOCOL}://localtest.me/auth/login', verify = False)
    
    values[csrf_cookie_name] = r.cookies[csrf_cookie_name]
    values['csrf_token'] = r.cookies[csrf_cookie_name]

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(csrf_cookie_name, values[csrf_cookie_name], domain = 'localtest.me')
    
    return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
