# Analysis of Web Frameworks

This folder contains the artifacts developed as proof of concept for the vulnerabilities identified and presented in `Table 5: Analyzed Web frameworks, and their respective authentication and CSRF libraries` of the paper.

## Toolchain

Each artifact is composed of 4 components:

* a target application that includes a login form and a CSRF protected action.
* an attacker that performs the attack to the respective target application.
* a server application that serves the sites `localtest.me` and `attack.localtest.me`.
* a testing script that automatically performs the attack.

All artifacts are available in the `web-frameworks` folder and are provided as Docker images. The testing script is available as a Python file `<test_name.py>` in each directory. Notice that the versions of the artifacts are pinned to the versions available at the time of our disclosure. The exact versions are reported in the dependencies of each artifact. Whenever a fix is available, we also provide the artifact to validate the fix.

## Setup

In order to run the artifacts, one needs to:

1. edit the `testing.env` file with the IP of the user's machine, and the protocol to be tested, `http` or `https`. This file will be used to provide environment values to the artifacts
2. generate appropriate certificates for the https connections. The certificates can be generate in the folder `web-frameworks` using the provided configuration file `localtest.me.conf` and running the following command:

```bash
`openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout localtest.me.key -out localtest.me.crt -config localtest.me.conf -extensions v3_req`
```

These certificates should then be copied to the `server` folder of each of the frameworks.

We rely on the external service `localtest.me` that points this domain, and all its subdomains, to `127.0.0.1`

All artifacts can be built and run using `docker compose`, providing some environment variables (details on these variables can be found in the table below). As an example, to test the CORF Token Fixation attack (pre-login) on express, one should use:

```bash
$ export VERSION="v0.5.3"; docker-compose --env-file ../testing.env up -d --build
```

This will start the artifact with the server listening on ports 80 and 443.

The testing scripts for each framework have been tested on a standard Ubuntu 22.04.2 LTS running Python 3.10.6. The only dependencies are the `requests` and `Beautiful Soup` libraries, which can be installed using `pip install --user requests bs4`. The tests are run as:

```bash
$ python3 <test_name.py>
```

The expected duration of each test, including compilation and automatic testing, is less than 1 minute on a modern laptop equipped with i7-1255U and 16GB of RAM. The output of the script will return if the artifact is vulnerable or not.

## Executing the Tests

As mentioned before, each artifact has a companion script to test the artifact. We will provide examples on how to automatically test the `express` artifact, and how to manually test an artifact for the presence of `CORF Token Fixation` (pre- and post-login) and `Session Fixation`.

### Automatic Test

The artifact available in folder `express-pre-login` can be used to test the express CORF Token Fixation (pre-login) on express. To run the automatic test execute:

```bash
cd express-pre-login
export VERSION="v0.5.3"; docker-compose --env-file ../testing.env up -d --build
echo "Should be vulnerable to pre-login"
python3 test-express-pre-login.py
```

The output of this test is

```bash
[+] Testing login
  - Correct behaviour confirmed
[+] Trying pre-login without fixation
  - CSRF attack failed without pre-session
[+] Sanity Checks passed
[+] Testing pre-login CSRF attack
  - Vulnerable to pre-login CSRF attack
```

confirming the found vulnerability. The test performs sanity checks such as proper login, proper CSRF protection when the attack is not performed, and finally the success of the attack.

In this case the target is a simple application that has 4 users `alice`, `bob`, `john_doe` and `attacker` each initially with 1000 credits. The CSRF protected transaction is the `transfer` transaction that transfers credits from the current user account to a destination account.

* The testing script logs in as `alice` and legitimately transfers 100 credits to the `attacker` to test the proper functionality.
* The testing script performs the attack by transfering 200 credits to the `attacker` on behalf of `alice`.

To test all applications run the script `test_all.sh`.

### Manual Test (Pre-login)

To manually execute this test one should build the artifact:

```bash
cd express-pre-login
export VERSION="v0.5.3"; docker-compose --env-file ../testing.env up -d --build
```

and perform the following steps:

1. Access `http://attack.localtest.me/` in a browser.
2. Press `Set Pre-session`.
3. Open a new tab in the browser and access `http://localtest.me/`.
4. Login as one of the users, `alice`, `bob`, or `john_doe`. The password is equal to the name of the user.
    * The balance should be 1000 credits.
5. Return to the tab `http://attack.localtest.me/` and execute a transfer of 1 credit to `attacker`.
6. Return to the tab `http://localtest.me/` and refresh.
    * Your balance should now be 999 credits.

To test the fixed version run

```bash
export VERSION="v0.6.0"; docker-compose --env-file ../testing.env up -d --build
echo "Should NOT be vulnerable to pre-login"
```

and repeat the previous steps. You should not be able to perform step 5.

### Manual Test (Post-login)

To manually test the CORF Token Fixation (post-login) attack one can use the artifact `express-post-session`:

```bash
docker-compose --env-file ../testing.env down
cd ../express-post-login
export VERSION="v0.5.3"; docker-compose --env-file ../testing.env up -d --build
echo "Should be vulnerable to post-login"
```

and perform the following steps:

1. Access `http://localtest.me/` in a browser.
2. Login as one of the users, `alice`, `bob`, or `john_doe`. The password is equal to the name of the user.
    - Your balance should be 1000 credits.
3. Open a new tab in the browser and access `http://attack.localtest.me/`.
4. Press `Set Post-session`.
5. Execute a transfer of 1 credit to `attacker`.
6. Return to the tab `http://localtest.me/` and refresh.
    - Your balance should now be 999 credits.

### Manual Test (Session-Fixation)

To manually test the session-fixation attack one can use the artifact `express-session-fixation`:

```bash
docker-compose --env-file ../testing.env down
cd ../express-session-fixation
export VERSION="v0.5.3"; docker-compose --env-file ../testing.env up -d --build
echo "Should be vulnerable to session fixation"
```

and perform the following steps:

1. Access `http://localtest.me/login` in a browser and observe the value of `session` in the DEBUG section (or `connect.sid` in your browser's cookies).
2. Login as one of the users, `alice`, `bob`, or `john_doe`. The password is equal to the name of the user.
3. Observe that the value of the session cookie is the same after login.

To test the fixed version run

```bash
export VERSION="v0.6.0"; docker-compose --env-file ../testing.env up -d --build
echo "Should NOT be vulnerable to session fixation"
```

and observe that the session cookie at step 3. is different from the section cookie at step 1.

### Testing other frameworks

Below we present a table with the values that should be used to test the other artifacts:

Framework | Folder | Vulnerability | Environment vars | Status
|:---|:---|:---|:---|:---|
express | express-pre-login        | Pre-login        | VERSION="v0.5.3"                 | CVE-2022-25896
express | express-pre-login        | Pre-login        | VERSION="v0.6.0"                 | Fixed
express | express-pre-login        | Pre-login        | VERSION="v0.6.0-keepSessionInfo" | Vulnerable/Opt out of fix
express | express-post-login       | Post-login       | VERSION="v0.5.3"                 | Vulnerable
express | express-post-login       | Post-login       | VERSION="v0.6.0"                 | Vulnerable
express | express-session-fixation | Session Fixation | VERSION="v0.5.3"                 | Vulnerable
express | express-session-fixation | Session Fixation | VERSION="v0.6.0"                 | Fixed
koa     | koa-pre-login            | Pre-login        | VERSION="v4.1.3"                 | Vulnerable
koa     | koa-pre-login            | Pre-login        | VERSION="v6.0.0"                 | Vulnerable
sails   | sails                    | Pre-login        | VERSION="v1.5.3"                 | Vulnerable
sails   | sails                    | Session Fixation | VERSION="v1.5.3"                 | Vulnerable
fastify | fastify-pre-login        | Pre-login        | VERSION="v2.2.0"                 | CVE-2023-29020
fastify | fastify-pre-login        | Pre-login        | VERSION="v2.3.0"                 | Fixed
fastify | fastify-pre-login        | Pre-login        | VERSION="v2.3.0-preserveFields"  | Vulnerable/Opt out of fix
fastify | fastify-post-login       | Post-login       | VERSION="v2.2.0"                 | CVE-2023-27495
fastify | fastify-post-login       | Post-login       | VERSION="v2.3.0"                 | Fixed
fastify | fastify-pre-login        | Session Fixation | VERSION="v2.2.0"                 | CVE-2023-29019
fastify | fastify-pre-login        | Session Fixation | VERSION="v2.3.0"                 | Fixed
flask   | flask-pre-login          | Pre-login        | VERSION="v0.6.1"                 | Vulnerable
flask   | flask-pre-login          | Pre-login        | VERSION="v0.6.2"                 | Vulnerable
tornado | tornado-post-login       | Post-login       | VERSION="v6.2.0"                 | Vulnerable
symfony | symfony-pre-login        | Pre-lofin        | VERSION="v5.4.19"                | CVE-2022-24895
codeigniter4 | codeigniter4-shield | Pre-login        | MODE="session_no_regenerate"; VERSION="v4.2.1" | CVE-2022-35943
codeigniter4 | codeigniter4-shield | Pre-login        | MODE="session_regenerate"; VERSION="v4.2.1"    | CVE-2022-35943
codeigniter4 | codeigniter4-shield | Post-login       | MODE="cookies"VERSION="v4.2.1"                 | CVE-2022-35943
codeigniter4 | codeigniter4-shield | Pre-login        | MODE="session_no_regenerate"; VERSION="v4.2.4" | Fixed
codeigniter4 | codeigniter4-shield | Pre-login        | MODE="session_regenerate"; VERSION="v4.2.4"    | Fixed
codeigniter4 | codeigniter4-shield | Post-login       | MODE="cookies"; VERSION="v4.2.4"               | Deprecated
Yii2         | yii2                | Post-login       | VERSION="2.0.45"                 | Vulnerable

## Notes on the Target Applications

Each applications has a script to automatticaly perform the test. Users can however test the applications manually following similar steps to the ones described above for the `express` framework.

Most vulnerable applications are simple applications that illustrate a bank where the transfer operation is CSRF protected.
The goal is to perform a CORF token fixation attack and transfer money to the attacker's account. Exceptions to this are the following where we performed modifications to demo applications of the frameworks:

- tornado framework has a demo blog application where the CSRF protected operation is the creation of posts. In this case an attacker is able to create posts on behalf of the authenticated user. As a side note, users can be created using endpoint `auth/create`.
- symfony framework also provides a blog as a demo application. We used that application for our experiments by introducing a CSRF protected form that shares its seed with the form that allows for the deletion of posts (task only available to the admin). The goal of the attacker in this case is to delete a message.
- Yii2 framework has a demo contact application where the CSRF protected operation is the creation of new contact requests. In this case an attacker is able to send these requests on behalf of the authenticated user.

Also, while manually testing, fatufy and codeigniter 4 present non-standard testing flows:

- in the fastify framework, tokens may be bound to the users. When manually testing the post-login attack, one needs to use the name of the authenticated user to generate a valid CSRF token.
- for codeigniter4, the attack flow for the `regenerate` case is also non-standard; for this attack to work one needs to set the pre-session (in attack.localtest.me), login in the application, and then evict the old cookie (or let it expire after 20s), get a fresh seed, and only afterwards perform the CSRF attack.
