from flask import Flask, render_template, make_response, redirect, url_for, request
from flask_talisman import Talisman
from bs4 import BeautifulSoup
import requests
import os, ssl
import hashlib
from base64 import b64encode


#### EDIT
csrf_cookie_name = '_csrf'
csrf_form_id = 'csrf_token'
csrf_form_name = '_csrf'

def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id=csrf_form_id).attrs['value']
#### /EDIT


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

MODE = os.environ['MODE']

PROTOCOL = os.environ['PROTOCOL']
if PROTOCOL == 'https':
    ssl._create_default_https_context = ssl._create_unverified_context
    Talisman(app)

values = {}
values['csrf_form_name'] = csrf_form_name


def base64url(string):
    return string.replace(b'+', b'-').replace(b'/', b'_')

def generate_token1(secret, salt, user = None):
    toHash = b''

    if user:
        m = hashlib.sha256()
        m.update(user)
        toHash += base64url(b64encode(m.digest())).replace(b'-', b'_').replace(b'=', b'') + b'-'
    
    toHash += salt

    m = hashlib.sha256()
    m.update(toHash + b'-' + secret)

    token = toHash + b'-' + base64url(b64encode(m.digest())).replace(b'=', b'')
    return token.decode()


@app.route('/')
def index():
    return render_template('index.html', values = values, protocol = PROTOCOL, mode = MODE)


@app.route('/set_post_session/')
def post_session():
    global values

    r = requests.get(f'{PROTOCOL}://localtest.me', verify = False)
    
    values[csrf_cookie_name] = r.cookies[csrf_cookie_name]

    if MODE != 'user':
        values['csrf_token'] = get_csrf_token(r.text)
    else:
        secret = r.cookies[csrf_cookie_name].split('.')[0].encode()
        salt = b'70AXYYpH'
        if request.args.get('username') == '':
            values['csrf_token'] = generate_token1(secret, salt, b'default')
        else:
            values['csrf_token'] = generate_token1(secret, salt, request.args.get('username').encode())

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(csrf_cookie_name, values[csrf_cookie_name], domain = 'localtest.me', path = '/transfer')
    
    return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
