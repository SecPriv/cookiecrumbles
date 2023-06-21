FROM composer as composer
ADD ./composer.json /app/composer.json
ADD ./composer.lock /app/composer.lock
RUN composer install --no-scripts --ignore-platform-reqs

FROM php:8.1.10-cli
EXPOSE 80
COPY . /usr/src/reflector
COPY --from=composer /app/vendor /usr/src/reflector/vendor
WORKDIR /usr/src/reflector
CMD [ "php", "./index.php", "0.0.0.0:80" ]