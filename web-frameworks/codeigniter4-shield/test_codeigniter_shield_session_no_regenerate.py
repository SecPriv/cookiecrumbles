import requests
from bs4 import BeautifulSoup
import os, sys, random

from common import get_csrf_token, login, logout, transfer, get_balance, register_default_users
from common import PROTOCOL, TARGET, ATTACKER, PRIVATE_KEY
from common import HOMEPAGE_MESSAGE, LOGIN_PAGE, LOGGEDIN_MESSAGE
from common import CORF_FAIL_WITHOUT_LOGIN, CORF_FAIL_WITH_WRONG_TOKEN, CORF_FAIL_STATUS_CODE, CORF_SUCCESS_MSG
from common import CORF_PRE_LOGIN_MSG

NAME1 = f"{random.randint(10000, 99999)}"
NAME2 = f"{random.randint(10000, 99999)}"
AMMOUNT1 = 100
AMMOUNT2 = 200
PASSWORD = "ab-cd-ef"


EXPECTED_RESULT = "VULNERABLE"
if "fixed" in sys.argv or "FIXED" in sys.argv:
    EXPECTED_RESULT = "FIXED"

try:
    VERSION = os.environ['VERSION']
except: 
    VERSION = "UNDEFINED"


with requests.Session() as s:
    register_default_users(NAME1, NAME2)


print(f"[+] Testing version {VERSION} in {PROTOCOL} mode")
# print(f"[+] Expected result: {EXPECTED_RESULT}\n")


### Test correct functionality
with requests.Session() as s:
    print("[+] Step1: Testing correct behaviour")

    ### Access main page
    r = s.get(TARGET, verify = PRIVATE_KEY)
    assert HOMEPAGE_MESSAGE in r.text

    ### Fail to perform the CSRF protected action
    csrf_token = get_csrf_token(r.text)
    r = transfer(s, NAME2, AMMOUNT1, csrf_token)
    assert CORF_FAIL_WITHOUT_LOGIN in r.text

    ### Target Login
    r = login(s, NAME1, NAME1)

    ### Success in performing the CSRF protected action
    current_balance = get_balance(r.text)
    csrf_token = get_csrf_token(r.text)
    r = transfer(s, NAME2, AMMOUNT1, csrf_token)

    assert CORF_SUCCESS_MSG % (AMMOUNT1, NAME1, NAME2) in r.text
    current_balance -= AMMOUNT1
    r = s.get(TARGET)
    assert LOGGEDIN_MESSAGE % NAME1 in r.text
    assert str(current_balance) in r.text

    ### Logout
    logout(s)

    print("    - Correct behaviour confirmed")


with requests.Session() as s:
    print("[+] Step2: Testing CORF Token Fixation Attack (pre-login) without setting pre-session")

    ### Access main page
    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert HOMEPAGE_MESSAGE in r_target.text

    ### Target Login
    r_target = login(s, NAME1, NAME1)
    assert current_balance == get_balance(r_target.text)

    ### ATTACKER fails to perform the CSRF protected action on behalf of NAME1 WITHOUT pre-fixating the secret
    ### Notice that attacker is obtaining the token from a different session
    ### Notice that NAME1 is already logged in
    with requests.Session() as s1:
        r_attacker = s1.get(TARGET, verify = PRIVATE_KEY)
        assert HOMEPAGE_MESSAGE in r_attacker.text

        ### extract csrf_token to use later
        csrf_token_attacker = get_csrf_token(r_attacker.text)
        
    r_attacker = transfer(s, NAME2, AMMOUNT2, csrf_token_attacker)

    assert r_attacker.status_code == CORF_FAIL_STATUS_CODE
    assert CORF_FAIL_WITH_WRONG_TOKEN in r_attacker.text, r_attacker.text

    ### Logout
    logout(s)

    print("    - CORF attack failed without setting pre-session")


print("[+] Sanity Checks passed")


with requests.Session() as s:
    print("[+] Step3: Testing CORF Token Fixation Attack (pre-login)")

    # r_target = s.get(TARGET, verify = PRIVATE_KEY)
    # assert HOMEPAGE_MESSAGE in r_target.text

    ### Attacker sets Pre-Session
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_pre_session')
    ### extract csrf_token to use later
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    ### Target Login
    r_target = login(s, NAME1, NAME1)

    ### ATTACKER succeeds in performing CSRF protected action on behalf of USER1
    r_attacker = s.get(ATTACKER + 'remove')
    r_attacker = transfer(s, NAME2, AMMOUNT2, csrf_token_attacker)
    if EXPECTED_RESULT == 'VULNERABLE':
        assert CORF_SUCCESS_MSG % (AMMOUNT2, NAME1, NAME2) in r_attacker.text, "NOT " + CORF_PRE_LOGIN_MSG
        current_balance -= AMMOUNT2
        r = s.get(TARGET, verify = PRIVATE_KEY)

        assert LOGGEDIN_MESSAGE % NAME1 in r.text
        assert str(current_balance) in r.text
        print(f"    - {CORF_PRE_LOGIN_MSG}\n")
    else:
        assert CORF_FAIL_WITH_WRONG_TOKEN in r_attacker.text, CORF_PRE_LOGIN_MSG
        r = s.get(TARGET, verify = PRIVATE_KEY)

        assert LOGGEDIN_MESSAGE % NAME1 in r.text
        assert str(current_balance) in r.text
        print(f"    - NOT {CORF_PRE_LOGIN_MSG}\n")

    ### Logout
    logout(s)
