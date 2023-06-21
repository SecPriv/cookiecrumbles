Cookie Measurement
==================
This folder contains the dataset and processing scripts for the cookie measurement study presented in Section 4.4 "Measurement of Cookie Name Prefixes and Nameless Cookies".

Dataset
-------
The source dataset for the study is the [Archive dataset](https://httparchive.org/) using the optimized tables from [Web Almanac](https://almanac.httparchive.org/) via Google BigQuery. We queried the dataset for all cookies set by the top 100K sites in 2021 and 2022, according to measurements performed on July 1, 2021 and June 1, 2022. The queries are available in the files `data-2021-07-01.sql` and `data-2022-06-01.sql`. The resulting datasets are available under the directories `data-2021-07-01/` and `data-2022-06-01/`.


Processing
----------
The processing script `analyzer.py` is written in Python 3 and tested on a standard Ubuntu 22.04.2 LTS with Python 3.10.6. No additional Python modules are required to perform the analysis of the dataset.

The script takes as input the path to a directory containing the dataset. The script then performs the analysis and prints the results to the standard output. The script can be executed as follows:

    python3 analyzer.py <path-to-dataset>

The script should take around 1 minute to process the dataset and output the following information (executed on the dataset from June 1, 2022):

```
$ python3 ./analyzer.py data-2022-06-01
[*] ================================================================================
[*] Rank:
{"10000": {"origins_with_cookies": {"total": 5952, "normal": 5947, "host_prefix": 14, "secure_prefix": 19, "nameless": 6, "secure": 4005}, "total_cookies": {"normal": 25411, "host_prefix": 22, "secure_prefix": 37, "nameless": 6, "secure": 12733}, "hsts": {"total": 3190, "include_subdomains": 2038}}, "100000": {"origins_with_cookies": {"total": 58068, "normal": 57987, "host_prefix": 113, "secure_prefix": 109, "nameless": 86, "secure": 35098}, "total_cookies": {"normal": 200985, "host_prefix": 141, "secure_prefix": 199, "nameless": 86, "secure": 94592}, "hsts": {"total": 26203, "include_subdomains": 14777}}, "1000": {"origins_with_cookies": {"total": 732, "normal": 732, "host_prefix": 6, "secure_prefix": 1, "nameless": 1, "secure": 537}, "total_cookies": {"normal": 3483, "host_prefix": 8, "secure_prefix": 1, "nameless": 1, "secure": 1886}, "hsts": {"total": 502, "include_subdomains": 313}}}
[*] __Host- cookie names:
('__Host-next-auth.csrf-token', 26)
('__Host-GAPS', 23)
('__Host-csrf-token', 13)
('__Host-PHPSESSID', 10)
('__Host-SESSION_LEGACY', 5)
('__Host-SESSION', 5)
('__Host-sess', 4)
('__Host-SWAFS', 3)
('__Host-session', 3)
('__Host-js_csrf', 3)
('__Host-logged-out-session', 3)
('__Host-ss', 3)
('__Host-csrftoken', 3)
('__Host-sessionid', 3)
('__Host-SessionID', 3)
('__Host-SessionId', 2)
('__Host-sos_session', 2)
('__Host-aweb.displayname', 2)
('__Host-device_id', 2)
('__Host-IB2_JSESSIONID', 2)
('__Host-IB2_jsLogoutTime', 2)
('__Host-IB2_token', 2)
('__Host-color-scheme', 1)
('__Host-theme-options', 1)
('__Host-stripe.support_site.csrf', 1)
('__Host-DEVICE-ID', 1)
('__Host-_stkn', 1)
('__Host-t_vendome', 1)
('__Host-strc_vendome', 1)
('__Host-_OTCM', 1)
('__HOST-PHPSESSID', 1)
('__Host-sc-a-session', 1)
('__Host-sc-a-nonce', 1)
('__Host-X-Snap-Client-Cookie', 1)
('__Host-sc-a-session-skip-login', 1)
('__Host-cms-session', 1)
('__Host-frontend', 1)
('__Host-CSRF', 1)
('__Host-APPLOVINID', 1)
('__HOST-sp_fid', 1)
('__Host-blokkendoos_session', 1)
('__Host-airtable-session.sig', 1)
('__Host-airtable-session', 1)
('__Host-session_id', 1)
('__Host-rtg_region', 1)
('__Host-rtg_location', 1)
('__Host-rtg_distribution_index', 1)
('__Host-CSRF-REQUEST-TOKEN', 1)
('__Host-CSRF-TOKEN', 1)
('__Host-FF.AppSession', 1)
('__Host-YoncuSec', 1)
('__Host-route', 1)
('__Host-RCAPPID', 1)
('__Host-postcrossing', 1)
('__Host-_identity_session_same_site', 1)
('__Host-blade_sess', 1)
('__Host-login-form-errors', 1)
('__Host-fb_token', 1)
('__Host-ur_token', 1)
('__Host-UR_SESSID', 1)
('__Host-register-form-errors', 1)
('__Host-livechart_session', 1)
('__Host-_comolib_session', 1)
('__Host-session-id', 1)
('__Host-pub-sid', 1)
('__Host-nfr_session', 1)
('__Host-ariregweb', 1)
('__HOST-JSESSIONID', 1)
('__HOST-diplomeo', 1)
[*] __Secure- cookie names:
('__Secure-ska', 36)
('__Secure-anon_token', 36)
('__Secure-anon_csrf_token', 36)
('__Secure-next-auth.callback-url', 26)
('__Secure-id_hint', 8)
('__Secure-access_token', 8)
('__Secure-id_token', 8)
('__Secure-session_state', 8)
('__Secure-PHPSESSID', 7)
('__Secure-session_id', 4)
('__Secure-sid', 4)
('__Secure-wp_seraph_accel_sess_m', 4)
('__Secure-sndp-refresh', 4)
('__Secure-BizTrackProspectGuid', 4)
('__Secure-XWAFLB', 3)
('__Secure-BIGipServer', 2)
('__Secure-peyas.sid', 2)
('__Secure-peya.sid', 2)
('__Secure-TnetID', 2)
('__Secure-gag-SessionID', 2)
('__Secure-sessionid', 2)
('__Secure-sess', 1)
('__Secure-JSESSIONID', 1)
('__Secure-SID', 1)
('__Secure-next-auth.session-token', 1)
('__Secure-produzione-csrf', 1)
('__Secure-.AspNetCore.Antiforgery', 1)
('__Secure-YoncuSec', 1)
('__Secure-vlnt-csrf', 1)
('__Secure-vlnt-session', 1)
('__Secure-lang', 1)
('__SECURE-PHPSESSID', 1)
('__Secure-coppel-auth-session', 1)
('__Secure-tmi_csrf', 1)
('__Secure-SessionId', 1)
('__Secure-h2pcmv20fcf5d90', 1)
('__Secure-h2pcmv2d971594e', 1)
('__Secure-h2pcmv22b4b0a5b', 1)
('__Secure-h2pcmv2e6642afe', 1)
('__Secure-h2pcmv23e9e286d', 1)
('__Secure-h2pcmv216fbf104', 1)
('__Secure-schools_session', 1)
('__Secure-ASP.NET_SessionId_Intendent', 1)
('__Secure-vb-prosim_session_003', 1)
('__Secure-access-token', 1)
('__Secure-ab-group', 1)
('__Secure-user-id', 1)
('__Secure-refresh-token', 1)
('__Secure-billigermietwagen', 1)
('__Secure-csrf-key', 1)
[*] Nameless cookie values:
('HttpOnly', 50)
('', 16)
('Secure', 6)
('=', 5)
('ACookieAvailableCrossSite', 4)
('=0', 3)
('secure', 1)
('*', 1)
('^(.*)$ $1', 1)
('=1', 1)
('ASPSESSIONIDSESAAQDC', 1)
('=deleted', 1)
('(.*)', 1)
("'HttpOnly", 1)
('0', 1)
```

The output is divided into multiple sections:
* **Rank**: a JSON-like structure with a summary of cookie-related information per rank (1-1K, 1K-10K, 10K-100K). The `origins_with_cookies` field contains the number of origins with cookies, grouped by cookie security level (normal, secure, host_prefix, secure_prefix, nameless). The `total_cookies` field contains the total number of cookies, grouped by cookie security level.
* **__Host- cookie names__**: a list of __Host- cookie names, sorted by the number of origins where they are set.
* **__Secure- cookie names**: a list of __Secure- cookie names, sorted by the number of origins where they are set.
* **Nameless cookie values**: a list of cookie values for nameless cookies, sorted by the number of origins where they are set.


Visualization and Correspondance with the Paper
-----------------------------------------------
The content of Table 3 can be directly inferred from the `origins_with_cookies` fields in the output posted above. Similarly, Figure 4 can be generated using the `draw.py` script (`matplotlib` and `numpy` are required), after hardcoding the values obtained from the output of the analysis (see the `draw.py` script for details).

Table 4 corresponds to the top-10 entries in the lists of __Host- cookie names and nameless cookie values posted above.