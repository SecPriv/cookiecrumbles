from flask import Flask, render_template, make_response, redirect, url_for
from flask_talisman import Talisman
from bs4 import BeautifulSoup
import requests
import os, ssl


#### EDIT
session_cookie_name = 'ci_session'
csrf_form_id = 'csrf_token'
csrf_form_name = 'csrf_test_name'

def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find("input", {"name": csrf_form_name}).attrs['value']
#### /EDIT


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

PROTOCOL = os.environ['PROTOCOL']
if PROTOCOL == 'https':
    ssl._create_default_https_context = ssl._create_unverified_context
    Talisman(app)

values = {}
values['csrf_form_name'] = csrf_form_name
session_value = None


@app.route('/')
def index():
    return render_template('index.html', values = values, protocol = PROTOCOL)


@app.route('/set_pre_session/')
def pre_session():
    global values
    global session_value

    r = requests.get(f'{PROTOCOL}://localtest.me', verify = False)
    
    values[session_cookie_name] = r.cookies[session_cookie_name]
    values['csrf_token'] = get_csrf_token(r.text)

    session_value = r.cookies[session_cookie_name]

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(session_cookie_name, values[session_cookie_name], domain = 'localtest.me', max_age = 20)
    
    return resp


@app.route('/remove')
def remove():
    resp = make_response(redirect(url_for('index')))

    resp.delete_cookie(session_cookie_name, domain = 'localtest.me')

    return resp


@app.route('/get_refreshed_seed')
def get_refreshed_seed():
    headers = {}

    if session_value:
        headers["Cookie"] = f"ci_session={session_value}"

    r = requests.get(f'{PROTOCOL}://localtest.me/', headers = headers, verify = False)
    
    values['csrf_token'] = get_csrf_token(r.text)
    
    resp = make_response(redirect(url_for('index')))
    return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
