FROM php:8.1-cli

RUN apt-get update -y && apt-get install -y libmcrypt-dev zip unzip git

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
RUN docker-php-ext-install pdo

WORKDIR /usr/src

RUN git clone https://github.com/symfony/demo.git app

WORKDIR /usr/src/app
RUN git checkout 6c1e93a
RUN rm composer.lock

COPY composer.json /usr/src/app
COPY patch.diff /usr/src/app

RUN patch -p1 -i patch.diff

RUN composer config --no-plugins allow-plugins true
RUN composer install


EXPOSE 8000

CMD php -S 0.0.0.0:8000 -t public/
