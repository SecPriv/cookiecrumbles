from flask import Flask, render_template, make_response, redirect, url_for
from flask_talisman import Talisman
from bs4 import BeautifulSoup
import requests
import os, ssl


#### EDIT
session_cookie_name = 'connect.sid'
csrf_form_id = 'csrf_token'
csrf_form_name = '_csrf'

def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id=csrf_form_id).attrs['value']
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


@app.route('/set_pre_session/')
def pre_session():
    global values

    r = requests.get(f'{PROTOCOL}://localtest.me', verify = False)
    
    values[session_cookie_name] = r.cookies[session_cookie_name]
    values['csrf_token'] = get_csrf_token(r.text)

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(session_cookie_name, values[session_cookie_name], domain = 'localtest.me', path = '/login')
    
    return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
