FROM node:16 as base

WORKDIR /usr/src

RUN echo -n "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" > /usr/src/secret-key

FROM base AS v2.2.0
RUN echo "" > /usr/src/vulnerable

COPY package.json .
RUN npm install
COPY . .

CMD node app.mjs


FROM base AS v2.3.0
RUN echo "" > /usr/src/fixed

COPY package.json .
COPY patches/patch-package-2.3.0.json .

RUN patch -p0 < patch-package-2.3.0.json
RUN npm install
COPY . .

CMD node app.mjs


FROM base AS v2.3.0-preserveFields
RUN echo "" > /usr/src/not_fixed_preserveFields

COPY package.json .
COPY patches/patch-package-2.3.0.json .

RUN patch -p0 < patch-package-2.3.0.json
RUN npm install

COPY . .

COPY patches/patch-app-2.3.0-preserveFields.mjs .
RUN patch -p0 < patch-app-2.3.0-preserveFields.mjs

CMD node app.mjs
