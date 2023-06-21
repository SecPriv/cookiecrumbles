FROM node:18

EXPOSE 1337
WORKDIR /usr/src

RUN npm i -g sails@1.5.3
RUN echo "1" | sails new test-project

WORKDIR /usr/src/test-project

COPY production.js ./config/env/production.js
# COPY production_host_cookies.js ./config/env/production.js

COPY transfer.js ./api/controllers/transfer.js
COPY transfer.ejs ./views/pages/transfer.ejs

COPY view-homepage.js ./api/controllers/view-homepage.js
COPY homepage.ejs ./views/pages/homepage.ejs

COPY routes.js ./config/routes.js
COPY policies.js ./config/policies.js

COPY signup.js ./api/controllers/entrance/signup.js
COPY User.js ./api/models/User.js

ENV NODE_ENV "production"

CMD sails lift --prod
