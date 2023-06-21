FROM php:8.1.10-cli
EXPOSE 80
COPY . /usr/src/reflector
WORKDIR /usr/src/reflector
CMD [ "php", "-S", "0.0.0.0:80", "./index.php" ]
