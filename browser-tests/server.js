/*
Tests to perform. 

- (Ordering) Cookies created first via JS are sent first (same path)
- (Ordering) Cookies with a most specific path are sent first

- (Tossing) Non-Secure cookie with non-Secure cookie (most specific path)
- (Tossing) Non-Secure cookie with Secure cookie (most specific path)
- (Tossing) Secure cookie with Secure cookie (most specific path)
- (Tossing) Secure cookie with non-Secure cookie (most specific path)
- (Tossing) HttpOnly cookie via HttpOnly Set-Cookie header (most specific path)
- (Tossing) HttpOnly cookie via non-HttpOnly document.cookie (most specific path)
- (Tossing) Secure cookie with non-secure nameless cookie (most specific path)
- (Tossing) __Host- cookie with non-secure nameless cookie (most specific path)

- (Eviction) Non-Secure cookie with non-Secure cookies
- (Eviction) Secure cookie with non-Secure cookies
- (Eviction) Secure cookie with Secure cookies
- (Eviction) __Host- cookie via Secure cookies
- (Eviction) __Host- cookie via non-Secure cookies
*/

const http = require('http');
const url = require('url');

const hostname = '0.0.0.0';
const port = 3000;

const domain = 'cookies.localtest.me'
const subdomain = 'sub.cookies.localtest.me'

var normalCookie = "normalcookie";
var hostCookie = "__Host-securecookie";
var namelessNormalCookie = `=${normalCookie}`;
var namelessHostCookie = `=${hostCookie}`;
var overflowCookies = []; // c001..c200
for(let i=1; i<=200; i++) {
    overflowCookies.push(`c${(i+'').padStart(3, '0')}`);
}
var allCookies = [normalCookie, hostCookie].concat(overflowCookies);

const server = http.createServer((req, res) => {
    const parsedURL = url.parse(req.url, true);

    if (parsedURL.query.delete) {
        // do your best to remove all possible cookies
        var cookies = [];
        allCookies.forEach(cName => {
            cookies.push(`${cName}=_; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`);
            cookies.push(`${cName}=_; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/folder;`);
            cookies.push(`${cName}=_; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=${domain}; path=/;`);
            cookies.push(`${cName}=_; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=${domain}; path=/folder;`);
        });
        // remove all possible cookie combos using the Set-Cookie header
        res.setHeader('Set-Cookie', cookies);
        res.writeHead(200, {
            // this header is not yet supported by Safari
            'Clear-Site-Data': '"cookies"'
        });
        // delete all the cookies via document.cookie too
        var jsCookies = "";
        cookies.forEach(cName => {
            jsCookies += `document.cookie = "${cName}";\n`;
            jsCookies += `document.cookie = "${cName}=_; expires=${new Date(0).toUTCString()}; path=/;";\n`;
            jsCookies += `document.cookie = "${cName}=_; expires=${new Date(0).toUTCString()}; path=/folder;";\n`;
            jsCookies += `document.cookie = "${cName}=_; expires=${new Date(0).toUTCString()}; domain=${domain}; path=/;";\n`;
            jsCookies += `document.cookie = "${cName}=_; expires=${new Date(0).toUTCString()}; domain=${domain}; path=/folder;";\n`;
        });
        res.end(`
            <!DOCTYPE html>
            <script>
            ${jsCookies}
            </script>
            Done
        `);
    } else if (parsedURL.query.read) {
        // reading cookies has the maximum priority, no matter what is the path
        var cookiesHeader = req.headers['cookie'];
        var cookies = "";
        if(cookiesHeader !== undefined) {
            cookies = cookiesHeader;
        }
        res.writeHead(200, {
            'Content-Type': 'text/html'
        });
        res.end(`
            <!DOCTYPE html>
            <script>
                function parseCookies(cookies) {
                    if(cookies) {
                        return cookies.split("; ");
                    } else {
                        return [];
                    }
                }
                window.opener.postMessage({headers: parseCookies("${cookies}"), js: parseCookies(document.cookie)}, "*");
            </script>
        `);
    } else if (parsedURL.query.set) {
        var cookies = [];
        var cs = [];
        var isNormal = parsedURL.query.isnormal;
        var isHost = parsedURL.query.ishost;
        var isNamelessNormal = parsedURL.query.isnamelessnormal;
        var isNamelessHost = parsedURL.query.isnamelesshost;
        var isOverflow = parsedURL.query.isoverflow;
        var params = parsedURL.query.params;
        if(isOverflow) {
            cookies = cookies.concat(overflowCookies);
        }
        if(isNormal) {
            cookies = cookies.concat([normalCookie]);
        }
        if(isHost) {
            cookies = cookies.concat([hostCookie]);
        }
        if(isNamelessNormal) {
            cookies = cookies.concat([namelessNormalCookie]);
        }
        if(isNamelessHost) {
            cookies = cookies.concat([namelessHostCookie]);
        }
        if (parsedURL.query.set == "header") {
            // set cookies via Set-Cookie header
            cookies.forEach(cName => {
                cs.push(`${cName}=${params}`);
            });
            res.setHeader('Set-Cookie', cs);
            res.writeHead(200, {
                'Content-Type': 'text/html',
            });
            res.end('Done');
        } else {
            // set cookies via the document.cookie API
            var jsCookies = "";
            cookies.forEach(cName => {
                jsCookies += `document.cookie = "${cName}=${params}";\n`;
            });
            res.writeHead(200, {
                'Content-Type': 'text/html',
            });
            res.end(`
                <!DOCTYPE html>
                <script>
                ${jsCookies}
                </script>
                Done
            `);
        }

    } else if (parsedURL.pathname == '/') {
        res.writeHead(200, {
            'Content-Type': 'text/html'
        });
        res.end(`
            <!DOCTYPE html>
            <html lang="en" data-theme="dark">          
              <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Cookie Integrity Evaluator</title>
                <meta name="description" content="Cookie Integrity Evaluator">
                <link rel="stylesheet" href="https://unpkg.com/@picocss/pico@latest/css/pico.min.css">
                <style>
                    .danger {
                        background-color: var(--form-element-invalid-active-border-color);
                        color: var(--color);
                    }
                    .safe {
                        background-color: var(--primary);
                        color: var(--color);
                    }
                    details {
                        margin-bottom: 0;
                        padding-bottom: 0;
                        border-bottom: 0;
                    }
                </style>
              </head>
              <body>
                <main class="container">
                  <section if="control">
                    <h1>Cookie Integrity Evaluator</h1>
                    <p>The tests will open multiple pages. Please allow the current site to open pop-ups. Wait until all tests are executed.</p>
                    <p><a href="#" role="button" class="outline" id="start">Start!</a></p>
                    <progress value="0" max="100" id="progress"></progress>
                  </section>

                  <section id="results">  
                    <figure>
                      <table id="results-table" role="grid">
                        <tbody>
                          <tr>
                            <td><strong>Test</strong></td>
                            <td><strong>Outcome</strong></td>
                            <td><strong>JS == Header</strong></td>
                            <td><strong>Details</strong></td>
                          </tr>
                        </tbody>
                      </table>
                    </figure>
                  </section>
                </main>
                <footer class="container">
                  <small>TU Wien, 2023</small>
                </footer>
            <script>
            var data;
          
            const deleteURLs = [
                "https://${domain}/?delete=1",
                "https://${domain}/folder/foo?delete=1",
                "https://${subdomain}/?delete=1",
                "https://${subdomain}/folder/foo?delete=1"
            ];

            function delay() {
                return new Promise(resolve => setTimeout(resolve, 400));
            }

            // this is our cookie reader
            window.addEventListener("message", (event) => {
                data = event.data;
            }, false);

            function validateTossing(cookies) {
                return cookies.headers[0] == "${normalCookie}=evil";
            }

            function validateEviction(cookies) {
                var evilFound = false;
                var goodFound = false;
                for(const c of cookies.headers) {
                    if(c == "${normalCookie}=evil") {
                        evilFound = true;
                    } else if(c == "${normalCookie}=good") {
                        goodFound = true;
                    }
                }
                return evilFound && (!goodFound);
            }

            function appendResult(testName, result, cookies) {
                var tbodyRef = document.getElementById('results-table').getElementsByTagName('tbody')[0];
                var newRow = tbodyRef.insertRow();
                var cell = newRow.insertCell();
                cell.appendChild(document.createTextNode(testName));
                cell = newRow.insertCell();
                if(result) {
                    cell.className = "danger";
                    cell.appendChild(document.createTextNode("confirmed"));
                } else {
                    cell.className = "safe";
                    cell.appendChild(document.createTextNode("unconfirmed"));
                }
                cell = newRow.insertCell();
                if(JSON.stringify(cookies.headers) === JSON.stringify(cookies.js)) {
                    cell.className = "safe";
                    cell.appendChild(document.createTextNode("true"));
                } else {
                    cell.className = "danger";
                    cell.appendChild(document.createTextNode("false"));
                }
                cell = newRow.insertCell();
                cell.innerHTML = "<details><summary>Expand</summary><code>" + JSON.stringify(cookies) + "</code></details>";
            }

            var tests = {
                // Ordering
                ordering_createdFirstJSSentFirst: {
                    preset: "https://${subdomain}/folder/foo?set=js&isnormal=1&params=evil; domain=${domain}; path=/;",
                    set: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: (cookies) => {
                        return cookies.headers[0] == "${normalCookie}=evil";
                    }
                },
                ordering_mostSpecificPathJSSentFirst: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/;",
                    set: "https://${subdomain}/folder/foo?set=js&isnormal=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: (cookies) => {
                        return cookies.headers[0] == "${normalCookie}=evil" && cookies.headers[1] == "${normalCookie}=good";
                    }
                },
                // Tossing
                tossing_nonSecureWithNonSecure: {
                    preset: "http://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/;",
                    set: "http://${subdomain}/folder/foo?set=header&isnormal=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_nonSecureWithSecure: {
                    preset: "http://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/;",
                    set: "https://${subdomain}/folder/foo?set=header&isnormal=1&params=evil; domain=${domain}; path=/folder; Secure;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_SecureWithSecure: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; Secure;",
                    set: "https://${subdomain}/folder/foo?set=header&isnormal=1&params=evil; domain=${domain}; path=/folder; Secure;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_SecureWithNonSecure: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; Secure;",
                    set: "http://${subdomain}/folder/foo?set=header&isnormal=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_httpOnlyWithHttpOnly: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; HttpOnly;",
                    set: "https://${subdomain}/folder/foo?set=header&isnormal=1&params=evil; domain=${domain}; path=/folder; HttpOnly;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_httpOnlyWithNonHttpOnly: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; HttpOnly;",
                    set: "https://${subdomain}/folder/foo?set=js&isnormal=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_SecureWithNamelessNonSecure: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; Secure;",
                    set: "http://${subdomain}/folder/foo?set=header&isnamelessnormal=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateTossing
                },
                tossing_hostPrefixWithNamelessNonSecure: {
                    preset: "https://${domain}/folder/foo?set=header&ishost=1&params=good; path=/; HttpOnly;",
                    set: "https://${subdomain}/folder/foo?set=header&isnamelesshost=1&params=evil; domain=${domain}; path=/folder;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: (cookies) => {
                        return cookies.headers[0] == "${hostCookie}=evil";
                    }
                },
                // Eviction
                eviction_nonSecureWithNonSecure: {
                    preset: "http://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/;",
                    set: "http://${subdomain}/folder/foo?set=js&isoverflow=1&isnormal=1&params=evil; domain=${domain}; path=/;",
                    read: "http://${domain}/folder/foo?read=1",
                    validate: validateEviction
                },
                eviction_SecureWithNonSecure: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; Secure;",
                    set: "http://${subdomain}/folder/foo?set=js&isoverflow=1&isnormal=1&params=evil; domain=${domain}; path=/;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateEviction
                },
                eviction_SecureWithSecure: {
                    preset: "https://${domain}/folder/foo?set=header&isnormal=1&params=good; path=/; Secure;",
                    set: "https://${subdomain}/folder/foo?set=js&isoverflow=1&isnormal=1&params=evil; domain=${domain}; path=/; Secure;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: validateEviction
                },
                eviction_hostPrefixWithSecure: {
                    preset: "https://${domain}/folder/foo?set=header&ishost=1&params=good; path=/; Secure;",
                    set: "https://${subdomain}/folder/foo?set=js&isoverflow=1&params=evil; domain=${domain}; path=/; Secure;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: (cookies) => {
                        var evilFound = false;
                        var goodFound = false;
                        for(const c of cookies.headers) {
                            if(c == "${hostCookie}=good") {
                                return false;
                            }
                        }
                        return true;
                    }
                },
                eviction_hostPrefixWithNonSecure: {
                    preset: "https://${domain}/folder/foo?set=header&ishost=1&params=good; path=/; Secure;",
                    set: "http://${subdomain}/folder/foo?set=js&isoverflow=1&params=evil; domain=${domain}; path=/;",
                    read: "https://${domain}/folder/foo?read=1",
                    validate: (cookies) => {
                        var evilFound = false;
                        var goodFound = false;
                        for(const c of cookies.headers) {
                            if(c == "${hostCookie}=good") {
                                return false;
                            }
                        }
                        return true;
                    }
                }
            };

            (async () => {
                async function testWrapper(testName, test) {
                    var target;
                    // delete
                    for(const url of deleteURLs) {
                        target = window.open(url);
                        await delay();
                        target.close();
                        await delay();
                    }
                    // set
                    target = window.open(test.preset);
                    await delay();
                    target.close();
                    await delay();
                    target = window.open(test.set);
                    await delay();
                    target.close();
                    await delay();
                    // read
                    target = window.open(test.read);
                    await delay();
                    target.close();
                    await delay();
                    
                    appendResult(testName, test.validate(data), data);
                }

                document.getElementById('start').addEventListener("click", async () => {
                    var i = 0;
                    var testsLength = Object.keys(tests).length;
                    for (const [testName, test] of Object.entries(tests)) {
                        await testWrapper(testName, test);
                        document.getElementById('progress').setAttribute('value', (++i/testsLength) * 100);
                    }
                });
            })();
            </script>
              </body>
            </html>
        `);
    } else {
        res.writeHead(404, {});
        res.end('404 ' + req.url);
    }
});

server.listen(port, hostname, () => {
    console.log(`Server running at https://${domain}/`);
});
