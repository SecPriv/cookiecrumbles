FROM nginx:1.21

COPY localtest.me.key /etc/ssl/private/localtest.me.key
COPY localtest.me.crt /etc/ssl/certs/localtest.me.crt

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
