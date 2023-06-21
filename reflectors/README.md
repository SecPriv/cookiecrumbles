Testing Cookie Parsers (Server-side)
====================================
This folder contains the toolchain developed to automatically test server-side cookie parsers. The result of the analysis was used to identify the vulnerabilities reported in Section 4.2.2 "Server-Side Parsing Issues".


Toolchain
---------
The toolchain is composed of two main components:
* a set of **reflectors**, i.e., a minimal program implemented in one of the tested backends (PHP, ReactPHP, Werkzeug) that parses HTTP requests containing a Cookie header and returns a JSON dump of the cookie names and values.
* a simple **fuzzer** that generates variations of the Cookie header, sends the same request to all reflectors, and records any differences in the JSON dumps.

All reflectors are available in the `reflectors` folder and are provided as Docker images. The fuzzer is available as a single Python file `fuzz.py` in the current directory. Notice that all versions of the reflectors are pinned to the latest vulnerable versions released before our fixes. The exact versions are reported in the `Dockerfile` of each reflector.


Setup
-----
All reflectors can be built and run using `docker compose`:
```
$ docker compose up --build
```

This will start the reflectors listening on localhost on the following ports:
* PHP, 1700
* ReactPHP, 1701
* Werkzeug, 1702

Reflectors can be easily tested using `curl`:
```
$ for port in 1700 1701 1702; do curl -H "Cookie: foo=bar" "http://localhost:${port}"; echo; done
{"foo":"bar"}
{"foo":"bar"}
{"foo": "bar"}
```

The fuzzer has been tested on a standard Ubuntu 22.04.2 LTS running Python 3.10.6. The only dependency is the `requests` library, which can be installed using `pip install --user requests`. The fuzzer can be run as follows:
```
$ ./fuzz.py <output.csv>
```

The expected duration of the fuzzer is about 4 minutes on a modern laptop equipped with i7-1255U and 16GB of RAM. The output is a CSV file containing the following columns:
* Value of the `Cookie` header sent to the reflectors
* JSON dump returned by the PHP reflector
* JSON dump returned by the ReactPHP reflector
* JSON dump returned by the Werkzeug reflector

Exceptions and errors are reported as empty strings.


Evaluation
----------
The output of the fuzzer is deterministic and should correspond to the provided `fuzz_output.csv` file (sha256 `c5ad0d113461ed6ced3b7191768589106bd64552db36fcecc7b133f6ad1c267f`). The generated CSV file contains `18472` entries, mostly caused by discrepancies of PHP with respect to the other backends.

Instances of the vulnerabilities reported in Section 4.2.2 "Server-Side Parsing Issues" are listed in the table below:

| Line number |             CVE | `Cookie` header |               PHP |          ReactPHP |         Werkzeug |
|-------------|-----------------|-----------------|-------------------|-------------------|------------------|
|        9626 |  CVE-2022-31629 |       `.[a=foo` |  `{"__a": "foo"}` |  `{".[a": "foo"}` | `{".[a": "foo"}` |
|        4038 |  CVE-2022-36032 |       `%0a=foo` |  `{"%0a": "foo"}` |   `{"\n": "foo"}` | `{"%0a": "foo"}` |
|       12416 |  CVE-2023-23934 |       `==a=foo` |              `[]` |  `{"": "=a=foo"}` |   `{"a": "foo"}` |
