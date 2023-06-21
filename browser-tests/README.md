Browser Testing Suite
=====================
This folder contains the test suite to verify cookie behavior in different browsers. The test suite can be used to validate the results presented in Table 2 of the paper. In the following, we describe how to setup the test suite and how to interpret the results using Firefox-104.


Setup
-----
The test suite can be launched using the following command from the current directory:

```bash
docker compose up --build
```

Ensure that ports `80` and `443` are free on the local machine and that `cookies.localtest.me` and `sub.cookies.localtest.me` resolve to `127.0.0.1`. If this is not the case, add the following entry to your `/etc/hosts` file, assuming that the testing environment is a Linux system:

```
127.0.0.1   cookies.localtest.me sub.cookies.localtest.me
```

Download Firefox-104 to match the version in Table 2 of the paper. On Linux, Firefox can be downloaded from the following [link](https://archive.mozilla.org/pub/firefox/releases/104.0/linux-x86_64/en-US/firefox-104.0.tar.bz2). Extract the archive:

```bash
mkdir ~/firefox-104
cd ~/firefox-104
wget https://archive.mozilla.org/pub/firefox/releases/104.0/linux-x86_64/en-US/firefox-104.0.tar.bz2
tar -xvf firefox-104.0.tar.bz2
cd firefox
```

Now run the browser with a clean profile:

```bash
PROFILEDIR=$(mktemp -p ../ -d profile.XXXXXX.d)
./firefox -profile $PROFILEDIR -no-remote -new-instance
rm -rf $PROFILEDIR
```

Visit the following URLs and accept the self-signed TLS certificates https://cookies.localtest.me/,  https://sub.cookies.localtest.me/. Be sure to also visit `about:preferences` and disable `Block pop-up windows`. Finally, visit https://cookies.localtest.me/ and click on start to begin the experiment.


Evaluation
----------
In the following table, we describe how to match the output of the test suite to relevant findings presented in Table 2 for Firefox-104. Please notice that the evaluation performed by the test suite is more extensive compared to the summary discussed in the paper.

| Attack                                | Test                                      | Test Outcome | Explanation |
|---------------------------------------|-------------------------------------------|--------------|-------------|
| Tossing (creation date)               | `ordering_createdFirstJSSentFirst`        | confirmed    | When 2 cookies have the same path, the cookie created first is sent first. FF results **unaffected** by attempts to shadow old cookies with new ones. |
| Tossing (insecure over secure)        | `tossing_SecureWithNonSecure`             | unconfirmed  | FF is **unaffected** by attempts to shadow a secure cookie with a non-secure cookie. |
| Serialization collision (=a=b > a=b)  | `tossing_SecureWithNamelessNonSecure`     | confirmed    | FF is **affected** by attempts to shadow a secure cookie with a non-secure nameless cookie. |
| Serialization collision (__Host-)     | `tossing_hostPrefixWithNamelessNonSecure` | confirmed    | FF is **affected** by attempts to shadow a `__Host-` prefixed cookie with a non-secure nameless cookie. |
| Eviction (cookie jar overflow)        | `eviction_SecureWithSecure`               | confirmed    | FF is **affected** by attempts to evict a secure cookie via a cookie jar overflow with other secure cookies. |
| Eviction (__Host- via secure cookies) | `eviction_hostPrefixWithSecure`           | confirmed    | FF is **affected** by attempts to evict a `__Host-` prefixed cookie via a cookie jar overflow with other secure cookies. |
| Cookie jar desynchronization          | `eviction_SecureWithNonSecure`            | unconfirmed  | The cookies retrieved via `document.cookie` do not match those attached to the HTTP request. FF is **affected** by desynchronizations of the cookie jar (see Section 4.2.3). Notice that this desynchronization affects all subsequent tests. |