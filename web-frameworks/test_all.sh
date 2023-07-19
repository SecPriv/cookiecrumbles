#!/bin/bash

RED="\e[31m"
GREEN="\e[32m"
ENDCOLOR="\e[0m"

cd codeigniter4-shield/
export MODE="session_no_regenerate"; export VERSION="v4.2.1"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_codeigniter_shield_session_no_regenerate.py
export MODE="session_no_regenerate"; export VERSION="v4.2.4"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_codeigniter_shield_session_no_regenerate.py
export MODE="session_regenerate"; export VERSION="v4.2.1"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_codeigniter_shield_session_regenerate.py
export MODE="session_regenerate"; export VERSION="v4.2.4"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_codeigniter_shield_session_regenerate.py
export MODE="cookies"; export VERSION="v4.2.1"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test_codeigniter_shield_cookies.py
export MODE="cookies"; export VERSION="v4.2.4"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to post-login. Deprecated${ENDCOLOR}\n"; python3 test_codeigniter_shield_cookies.py
docker-compose stop
cd ..
cd express-post-login/
export VERSION="v0.5.3"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test-express-post-login.py
export VERSION="v0.6.0"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test-express-post-login.py
docker-compose stop
cd ..
cd express-pre-login/
export VERSION="v0.5.3"; docker-compose up -d --build ; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-express-pre-login.py
export VERSION="v0.6.0"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-express-pre-login.py
export VERSION="v0.6.0-keepSessionInfo"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login. Opt out of fix${ENDCOLOR}\n"; python3 test-express-pre-login.py
docker-compose stop
cd ..
cd express-session-fixation/
export VERSION="v0.5.3"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to session fixation${ENDCOLOR}\n"; python3 test-express-session-fixation.py
export VERSION="v0.6.0"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to session fixation${ENDCOLOR}\n"; python3 test-express-session-fixation.py
export VERSION="v0.6.0-keepSessionInfo"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to session fixation${ENDCOLOR}\n"; python3 test-express-session-fixation.py
docker-compose stop
cd ..
cd fastify-post-login
export VERSION="v2.2.0"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test-fastify-post-login.py
export VERSION="v2.3.0"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to post-login${ENDCOLOR}\n"; python3 test-fastify-post-login.py
docker-compose stop
cd ..
cd fastify-pre-login
export VERSION="v2.2.0"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-fastify-pre-login.py
export VERSION="v2.3.0"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-fastify-pre-login.py
export VERSION="v2.3.0-preserveFields"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login. Opt out of fix${ENDCOLOR}\n"; python3 test-fastify-pre-login.py
docker-compose stop
cd ..
cd flask-pre-login/
export VERSION="v0.6.1"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-flask-pre-login.py
docker-compose stop
cd ..
cd koa-pre-login/
export VERSION="v4.1.3"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test-koa-pre-login.py
docker-compose stop
cd ..
cd sails
export VERSION="v1.5.3"; docker-compose up -d --build; sleep 10; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_sails.py
docker-compose stop
cd ..
cd symfony-pre-login/
export VERSION="v5.4.19"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_symfony.py
export VERSION="v5.4.20"; docker-compose up -d --build; sleep 5; echo -e "\n${GREEN}Should NOT be vulnerable to pre-login${ENDCOLOR}\n"; python3 test_symfony.py
docker-compose stop
cd ..
cd tornado-post-login/
export VERSION="v6.2.0"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test_tornado.py
docker-compose stop
cd ..
cd yii2
export VERSION="v2.0.45"; docker-compose up -d --build; sleep 5; echo -e "\n${RED}Should be vulnerable to post-login${ENDCOLOR}\n"; python3 test_yii2.py
docker-compose stop
cd ..
