FROM ubuntu:20.04

## for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

RUN apt-get update -y && apt-get install -y libmcrypt-dev zip unzip
RUN apt-get install -y libicu-dev
RUN apt-get install -y php7.4 php7.4-cli php7.4-intl php7.4-json php7.4-common php7.4-mysql php7.4-zip php7.4-gd php7.4-mbstring php7.4-curl php7.4-xml php7.4-bcmath composer
RUN apt-get install -y git

# RUN composer create-project yiisoft/yii2-app-basic:master#27e20ee60e505ccd99138c58000f2c842412f097 /usr/src/app
RUN composer create-project --prefer-dist yiisoft/yii2-app-basic:2.0.45 /usr/src/app
WORKDIR /usr/src/app

COPY csrf_app.diff /usr/src/app/
RUN patch -p1 -i csrf_app.diff

# ### enable CSRF with Syncrhronizer Token Pattern
# COPY session.diff /usr/src/app/
# RUN patch -p1 -i session.diff

CMD ./yii serve 0.0.0.0 --port 8080
