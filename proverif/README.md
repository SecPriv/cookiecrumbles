ProVerif Models and Verification of Web Frameworks
==================================================
This folder contains all the files required to formally verify our proposed solution to fix the synchronizer token pattern. That is, refreshing the CSRF token secret in the session upon user login.


Framework API
-------------
We define a framework as a set of functions for handling user management and CSRF protection.

```
empty_session : () -> Session
valid_session : Session -> bool
session_from_cookie : CookiePair -> Session
cookie_of_session : Session -> CookiePair
is_loggedin : Session -> bool
login_user : (Session, User) -> Session
logout_user : Session -> Session
generate_token : Session -> Session
serialize_token : Session -> CSRFToken
validate_token : (Session, CSRFToken) -> bool
```

In particular, each framework model provides definitions for: 

- **Session.** The implementation for the session data type and the functions to construct, validate and serialize such session to a cookie: `empty_session`, `valid_session`, `session_from_cookie`, `cookie_of_session`. The session could be stored on the server or client side: in the first case, `session_from_cookie` fetches from the server storage the session corresponding to the session id in the cookie, in the second case, the function decodes the cookie value into a session that can be later validated with `valid_session`. Similar considerations apply to the inverse operation.
- **User management.** The implementation of the user management functions such as `is_loggedin`, `login_user`, `logout_user`. Such function modify the current session with the status of the user if, e.g., the credentials are valid.
- **CSRF protection.** The implementation of the generation and validation of CSRF tokens: `generate_token`, `serialize_token`, `validate_token`. These functions may rely on implementation-specific types for the CSRF secret that can be stored in the session. The `generate_token` function generates the CSRF secret, possibly updating the session; similarly, the validation and serialization of the CSRF token may depend on the secret stored in the session.


Technical Details
-----------------
We make use of the C preprocessor for macro expansion, for generating the `vulnerable` and `fixed` variations of the model, and for modularity. In particular, we define the following files:

- `prelude.inc.pv`: Common types and functions declarations that are reused across all framework models.
- `application.inc.pv`: Model of the generic web application that uses the Framework API described above.
- `queries.inc.pv`: Definition of the events and security queries to check against the models.
- `attacker.inc.pv`: Definition of the attacker model. The attacker runs a website on a subdomain of the target application and can overwrite any cookie: we over-approximate all threat models by assuming no integrity on cookies.
- `user_agent.inc.pv`: Definition of the honest user's actions when visiting the target application.
- `main_process.inc.pv`: Network/Main process definition: we run the WebSpi library, the application and the attacker and we have an unbound number of users with valid credentials.
- `codeigniter.pv`, `express.pv`, `fastify_client.pv`, `fastify_server.pv`, `flask.pv`, `koa.pv`, `symfony.pv`: Framework models. Each framework model defines the specific implementation of the functions of the Framework API, and, including all other `*.inc.pv` files, provides the entry point for the verification of each framework.

The project makes use of a slightly modified version of the [WebSpi](http://web.archive.org/web/20210516103027/https://prosecco.gforge.inria.fr/webspi/) library, provided in the file `webspi.pvl`. In particular, we merge the possibility to handle subdomains (CSF version) with the ability to use standard ProVerif correspondences instead of datalog-like properties (POST version).

### Queries
The `queries.inc.pv` file defines two queries:

- Reachability of all events in the application. We make sure that every event can be executed: correspondence assertions could be marked valid if events are never executed, so we ensure events are reachable before checking for our correspondence.
  ```
  query b:Browser, cp:CookiePair, token:CSRFToken, id:Id, pwd: Secret;
    event ( app_gen_token(cp, token) );
    event ( app_login(cp, id, pwd, token) );
    event ( app_logout(cp) );
    event ( user_login_begin(b, id, pwd, token) );
    event ( app_action_successful(cp, token) );
    event ( app_action_begin(b, token) ).
  ```

- Main invariant (Sec. 7): *Every action executed by a token-protected endpoint must be explicitly initiated by an honest user by performing a request containing the token.*.
  ```
  query b:Browser, cp:CookiePair, token:CSRFToken;
        event ( app_action_successful(cp, token) ) ==>
        event ( app_action_begin(b, token) ).
  ```

ProVerif could return three possible answers:
- `is true`: the property is true. When ProVerif returns true, it the property guaranteed to hold.
- `cannot be proved`: the property is not true. There is a counterexample (in form of a resolution derivation) to the property.
- `is false`: the property is not true, **and** the derivation could be translated to applied pi calculus. It may be the case that the generated derivations cannot be converted to pi-calculus processes: WebSpi configures (Line 25 of `webspi.pvl`) proverif to never attempt to reconstruct a process, so all properties that are not `true` either return `cannot be proved` or loop.

#### Note
For reachability of an `event(...)`, ProVerif tries to prove `not event(...)`, so the result `cannot be proved` confirms the reachability of the event, whereas `is true` shows that the event **is not reachable**.

For correspondence assertions, instead, a `is true` result confirms that the property holds.

For this reason, we expect the output of our reachability query to return `cannot be proved`.


Additional Details
------------------
We refer to Appendix B of the extended version of the paper for additional details on the modeling of frameworks.


Setup
-----
The framework models have been verified with ProVerif version 2.04.
The `Makefile` in this folder requires the `cpp` preprocessor, GNU `make` and the `bat` utility.

We provide an exact copy of our environment in the docker image `wert310/proverif:a2e281f` (built using the `Dockerfile` in this folder).
All subsequent commands can be run inside the shell of the container obtained by running the following commands from the current directory:
```
docker pull wert310/proverif:a2e281f
docker run --rm -ti -v$PWD:/mnt --workdir /mnt wert310/proverif:a2e281f bash
```


Usage
-----
- Execute proverif on the `<framework_name>` model without applying any fix
  ```sh
  stdbuf -o0 make -B run-<framework_name>
  ```
  
We list how to verify the fixed version of each framework in the following subsections.
For each framework, we expect the following output from the invocation of ProVerif on the fixed model:
```
Verification summary:

Query not event(app_gen_token(cp_9,token_7)) cannot be proved.

Query not event(app_login(cp_9,id,pwd,token_7)) cannot be proved.

Query not event(app_logout(cp_9)) cannot be proved.

Query not event(user_login_begin(b_9,id,pwd,token_7)) cannot be proved.

Query not event(app_action_successful(cp_9,token_7)) cannot be proved.

Query not event(app_action_begin(b_9,token_7)) cannot be proved.

Query event(app_action_successful(cp_9,token_7)) ==> event(app_action_begin(b_9,token_7)) is true.
```

Each framework model implements the fix of refreshing the token upon login using the conditional compilation (`#ifdef`) capabilities offered by the `cpp` preprocessor. In particular, defining the flag `REFRESH_TOKEN_LOGIN` (i.e., passing the `CFLAGS=-DREFRESH_TOKEN_LOGIN` parameter to `make`) selects the fixed framework implementation. 
Note that in case of Express, the additional flag `REFRESH_SESSION_ID` is required, since also the session dentifier need to be refreshed.

### Flask

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-flask
  ```

### Koa

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-koa
  ```

### Express

- Apply both fixes (refresh token and refresh session id)
  ```sh
  stdbuf -o0 make -B "CFLAGS=-DREFRESH_TOKEN_LOGIN -DREFRESH_SESSION_ID" run-express
  ```

### Symfony

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-symfony
  ```

__Note__: since the session ID is refreshed upon login, the model without the fix does not terminate.

### Sails

Although Sails does not implement a login interface/module, the template application provides a user-management service based on express-session.
Sails can be configured to enable CSRF protection out of the box via the csurf and csrf libraries.
For our purposes, this makes the Sails model identical to Express.

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-sails
  ```

### Fastify

Fastify provides two modes, which configure the session to be stored either at the client or the server-side. Fastify uses a fork of the passport library and the implementation of fastify/csrf-protection closely resembles the csurf and csrf libraries. For our purposes, this makes the Fastify model identical to Express (server-side) or Koa (client-side).

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-fastify_client
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-fastify_server
  ```


### CodeIgniter 4

- Apply the fix and run proverif
  ```sh
  stdbuf -o0 make -B CFLAGS=-DREFRESH_TOKEN_LOGIN run-codeigniter
  ```

__Note__: since the CSRF seed is inserted in a table twice for every login, the model without the fix may not terminate.


Verifying all Frameworks
------------------------
The summary of the verification result for all frameworks can be obtained with the following bash loop:

```sh
for FW in flask koa express symfony sails fastify_client fastify_server codeigniter; do
  echo "===== $FW ====="
  echo "default configuration:"
  timeout 2m stdbuf -o0 make -B run-$FW |& grep RESULT
  echo "fixed version:"
  stdbuf -o0 make -B "CFLAGS=-DREFRESH_TOKEN_LOGIN -DREFRESH_SESSION_ID" run-$FW |& grep RESULT
done
```

The loop prints the verification result before and after applying the fix.
Note that we enable both the `REFRESH_TOKEN_LOGIN` and `REFRESH_SESSION_ID` flags since `REFRESH_SESSION_ID` is required for Express and ignored by all other framework models.
