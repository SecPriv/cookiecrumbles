FROM node:18 as base

WORKDIR /usr/src

COPY . .

FROM base AS v0.5.3
RUN echo "" > /usr/src/vulnerable

RUN npm install
CMD node app.js


FROM base AS v0.6.0
RUN echo "" > /usr/src/not_fixed

COPY patches/patch-package-0.6.0.json .
COPY patches/patch-app-0.6.0.js .

RUN patch -p0 < patch-package-0.6.0.json
RUN patch -p0 < patch-app-0.6.0.js
RUN npm install
CMD node app.js
