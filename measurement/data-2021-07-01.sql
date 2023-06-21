CREATE TEMPORARY FUNCTION getHeaders(payload STRING)
RETURNS STRING
LANGUAGE js AS """
  const parsed_headers = JSON.parse(payload);
  
  const resp_headers = parsed_headers.response.headers.filter(h => h.name.match(/(?:set-cookie|server|strict-transport-security)/i));
  const resp_cookies = parsed_headers.response.cookies;

  const req_headers = parsed_headers.request.headers.filter(h => h.name.match(/(?:cookie)/i));
  const req_cookies = parsed_headers.request.cookies;

  return JSON.stringify({resp_headers: resp_headers, resp_cookies: resp_cookies, req_headers: req_headers, req_cookies: req_cookies});
""";


SELECT
    req.rank AS rank,
    NET.HOST(req.page) AS origin,
    NET.REG_DOMAIN(req.page) AS regdomain,
    req.page AS url_from,
    req.url AS url_to, 
    getHeaders(payload) AS headers
FROM 
    `httparchive.almanac.requests` AS req
WHERE 
    date = '2021-07-01' AND
    rank <= 100000 AND
    (req.reqCookieLen > 0 OR req.respCookieLen > 0) AND
    NET.REG_DOMAIN(page) = NET.REG_DOMAIN(url) -- 1st party cookies