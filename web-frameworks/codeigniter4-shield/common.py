import requests, random
from bs4 import BeautifulSoup
import os, sys, time


#### EDIT
session_cookie_name = 'ci_session'
# csrf_cookie_name = ''
# csrf_form_id = ''
csrf_form_name = 'csrf_test_name'

PASSWORD = "ab-cd-ef"

HOMEPAGE_MESSAGE = '<button type="submit">Login</button>'
LOGIN_PAGE       = 'Use a Login Link'
LOGGEDIN_MESSAGE = 'Welcome %s.'

CORF_FAIL_WITHOUT_LOGIN     = 'Please login first.'
CORF_FAIL_WITH_WRONG_TOKEN  = 'The action you requested is not allowed.'
CORF_FAIL_STATUS_CODE       = 403
CORF_SUCCESS_MSG            = 'Successfully transferred %s from %s to %s'
#### /EDIT


try:
    PROTOCOL = os.environ['PROTOCOL']
except:
    PROTOCOL = 'http'
TARGET = f'{PROTOCOL}://localtest.me/'
ATTACKER = f'{PROTOCOL}://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'

INCOMPATIBILITY_MSG  = "Same-site attackers may bypass the CSRF protection. Please set it to 'session'"
SESSION_FIXATION_MSG = "Vulnerable to session fixation"
CORF_PRE_LOGIN_MSG   = "VULNERABLE to CORF Token Fixation Attack (pre-login)"
CORF_POST_LOGIN_MSG  = "VULNERABLE to CORF Token Fixation Attack (post-login)"



def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find("input", {"name": csrf_form_name})['value']


def login(s, username, password = PASSWORD):
    r = s.get(TARGET + 'login', verify = PRIVATE_KEY)
    assert LOGIN_PAGE in r.text

    pre_session_cookie = s.cookies.get_dict()[session_cookie_name]
    # pre_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]

    csrf_token = get_csrf_token(r.text)
    data = {csrf_form_name: csrf_token, 'email': f'{username}@test.com', 'password':  password}
    r = s.post(TARGET + 'login', data = data)

    ### Welcome message
    # assert (LOGGEDIN_MESSAGE % username) in r.text

    post_session_cookie = s.cookies.get_dict()[session_cookie_name]
    # post_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]
    
    # assert pre_session_cookie != post_session_cookie, SESSION_FIXATION_MSG

    return r


def logout(s):
    r = s.get(TARGET + 'logout')
    assert HOMEPAGE_MESSAGE in r.text
    

def transfer(s, target, ammount, csrf_token):
    data = {'ammount': ammount, 'target': target, csrf_form_name: csrf_token}
    return s.post(TARGET + 'transfer', data = data)


def get_balance(page):
    return int(page.split("Your <b>balance</b> is ")[1].split('<br>')[0])


def register(s, username, password = PASSWORD):
    r = s.get(TARGET + 'index.php/register', verify = PRIVATE_KEY)

    if r.status_code == 500 and INCOMPATIBILITY_MSG in r.text:
        print("Shield no longer accepts CSRF protection with Double Submit Pattern")
        exit()
    
    csrf_token = get_csrf_token(r.text)
    data = {csrf_form_name: csrf_token, 'email': f'{username}@test.com', 'username': username, 'password':  password, 'password_confirm': password}
    r = s.post(TARGET + 'index.php/register', data = data)
    
    assert (LOGGEDIN_MESSAGE % username) in r.text, r.text
    print(f"Registered: user: {username}@test.com:{password}")

    logout(s)


def register_default_users(USER1, USER2):
    with requests.Session() as s:
        for user in ['alice', 'bob', 'john_doe', 'attacker']:
            try:
                register(s, user, user)
            except:
                pass

        for user in [USER1, USER2]:
            register(s, user, user)
