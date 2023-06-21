FROM ubuntu:20.04 as base

ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update -y && apt-get install -y libmcrypt-dev zip unzip
RUN apt-get install -y libicu-dev
RUN apt-get install -y php7.4 php7.4-cli php7.4-intl php7.4-json php7.4-common php7.4-mysql php7.4-zip php7.4-gd php7.4-mbstring php7.4-curl php7.4-xml php7.4-bcmath
RUN apt-get install -y git

WORKDIR /usr/src

## INSTALL COMPOSER MANUALLY
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
RUN php -r "if (hash_file('sha384', 'composer-setup.php') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;"
RUN php composer-setup.php
RUN php -r "unlink('composer-setup.php');"
RUN mv composer.phar /usr/local/bin/composer

RUN composer self-update 2.3.8


FROM base as vulnerable

WORKDIR /usr/src
RUN composer create-project codeigniter4/appstarter:4.2.1 /usr/src/app

WORKDIR /usr/src/app
RUN composer require codeigniter4/framework:4.2.1
RUN composer require codeigniter4/shield:dev-develop#52bacb2797acc2a0bf821a024870e5336114f300


RUN php spark shield:setup

COPY csrf_app.diff /usr/src/app/
RUN patch -p1 -i csrf_app.diff

EXPOSE 8080


FROM vulnerable AS v4.2.1cookies

RUN echo "" > /usr/src/app/post_login
COPY .env_cookies .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080


FROM vulnerable AS v4.2.1session_no_regenerate

RUN echo "" > /usr/src/app/pre_login_no_regenerate
COPY .env_session_no_regenerate .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080


FROM vulnerable AS v4.2.1session_regenerate

RUN echo "" > /usr/src/app/pre_login_regenerate
COPY .env_session_regenerate .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080


FROM base as fixed

WORKDIR /usr/src
RUN composer create-project codeigniter4/appstarter:4.2.2 /usr/src/app

WORKDIR /usr/src/app
RUN composer require codeigniter4/framework:4.2.4
RUN composer require codeigniter4/shield:v1.0.0-beta.2


RUN php spark shield:setup

COPY csrf_app_patch.diff /usr/src/app/
RUN patch -p1 -i csrf_app_patch.diff

EXPOSE 8080


FROM fixed AS v4.2.4cookies

RUN echo "" > /usr/src/app/post_login
COPY .env_cookies .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080


FROM fixed AS v4.2.4session_no_regenerate

RUN echo "" > /usr/src/app/pre_login_no_regenerate
COPY .env_session_no_regenerate .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080


FROM fixed AS v4.2.4session_regenerate

RUN echo "" > /usr/src/app/pre_login_regenerate
COPY .env_session_regenerate .env

ENTRYPOINT sleep 5 && php /usr/src/app/spark migrate --all && php spark serve --host 0.0.0.0 --port 8080