#!/usr/bin/python3

import os
import io
import re
import sys
import csv
import json
import gzip
import json
from enum import Enum

# increase the csv field size limit to handle large entries
csv.field_size_limit(sys.maxsize)

# base regexps for cookie prefixes and nameless cookies
REGEXP_HOST   = re.compile(r'^__Host-', re.IGNORECASE)
REGEXP_SECURE = re.compile(r'^__Secure-', re.IGNORECASE)
REGEXP_NAMELESS_HEADER = re.compile(r'^=|^[^=]+?;', re.IGNORECASE)
REGEXP_SECURE_ATTRIBUTE = re.compile(r'\s*secure\s*', re.IGNORECASE)
REGEXP_HSTS_SUBDOMAINS = re.compile(r'includeSubDomains', re.IGNORECASE)

cookies = dict()
servers = dict()
hstss   = dict()

class CookieType(Enum):
    NORMAL = 1
    HOST_PREFIX = 2
    SECURE_PREFIX = 3
    NAMELESS = 4

class Cookie:
    def __init__(self, name, value, cookie_type, raw):
        self.name = name
        self.value = value
        self.cookie_type = cookie_type
        self.raw = raw
        self.secure = False
    
        self.validate_secure()
    
    def validate_secure(self):
        # check if the cookie has the secure flag
        for part in self.raw.split(';')[1:]:
            if REGEXP_SECURE_ATTRIBUTE.match(part):
                self.secure = True
                break

    def __eq__(self, other):
        return self.name == other.name and self.cookie_type == other.cookie_type
    
    def __hash__(self):
        return hash((self.name, self.cookie_type))

    def __str__(self):
        return repr({'name': self.name, 'value': self.value,
                     'cookie_type': self.cookie_type,
                     'secure': 1 if self.secure else 0, 'raw': self.raw})


def parse_set_cookie(cookie):
    cookie_name = ''
    cookie_value = ''
    cookie_type = CookieType.NORMAL

    # match nameless cookies first, since '__Host-foo; Secure' is a nameless cookie
    if REGEXP_NAMELESS_HEADER.match(cookie):
        cookie_type = CookieType.NAMELESS
    elif REGEXP_HOST.match(cookie):
        cookie_type = CookieType.HOST_PREFIX
    elif REGEXP_SECURE.match(cookie):
        cookie_type = CookieType.SECURE_PREFIX
    
    cookie_parts = cookie.split(';')
    cookie_name_value = cookie_parts[0]

    if cookie_type == CookieType.NAMELESS:
        cookie_value = cookie_name_value
    else:
        eq_index = cookie_name_value.find('=')
        cookie_name = cookie_name_value[:eq_index]
        cookie_value = cookie_name_value[eq_index+1:]
        
    return Cookie(cookie_name, cookie_value, cookie_type, cookie)


def process_dir(dirname):
    for fname in sorted(os.listdir(dirname)):
        parse_csv(os.path.join(dirname, fname))

def parse_csv(fname):
    with gzip.open(fname, 'r') as f:
        # remove NULL bytes from the CSV file
        data = f.read().replace(b'\0', b'')
        f = io.StringIO(data.decode('utf-8')) 
        reader = csv.DictReader(f)
        for row in reader:
            # parse response headers
            headers = json.loads(row['headers'])
            for h in headers['resp_headers']:
                if re.match('set-cookie', h['name'], re.IGNORECASE):
                    cookie = parse_set_cookie(h['value'])
                    try:
                        cookies[(row['rank'], row['origin'])].add(cookie)
                    except KeyError:
                        cookies[(row['rank'], row['origin'])] = {cookie}
                elif re.match('server', h['name'], re.IGNORECASE):
                    try:
                        servers[(row['rank'], row['origin'])].add(h['value'])
                    except KeyError:
                        servers[(row['rank'], row['origin'])] = {h['value']}
                elif re.match('strict-transport-security', h['name'], re.IGNORECASE):
                    try:
                        hstss[(row['rank'], row['origin'])].add(h['value'])
                    except KeyError:
                        hstss[(row['rank'], row['origin'])] = {h['value']}

def print_occurrences(l):
    res_dict = dict()
    res_list = []

    for e in l:
        try:
            res_dict[e] += 1
        except KeyError:
            res_dict[e] = 1
    
    for k, v in res_dict.items():
        res_list.append((k, v))
    res_list.sort(key = lambda x: x[1], reverse=True)

    for e in res_list:
        print(e)


def analysis():
    ranks = dict()
    cookies_names = {
        # names
        'host_prefix': [],
        'secure_prefix': [],
        # values
        'nameless': []
    }

    for rank_origin, cookies_set in cookies.items():
        try:
            rank, _ = rank_origin
            ranks[rank]
        except KeyError:
            ranks[rank] = {
                'origins_with_cookies': {
                    'total': 0,
                    'normal': 0,
                    'host_prefix': 0,
                    'secure_prefix': 0,
                    'nameless': 0,
                    'secure': 0
                },
                'total_cookies': {
                    'normal': 0,
                    'host_prefix': 0,
                    'secure_prefix': 0,
                    'nameless': 0,
                    'secure': 0
                },
                'hsts': {
                    'total': 0,
                    'include_subdomains': 0
                }
            }

        cookies_found = False
        cookies_normal_found = False
        cookies_host_prefix_found = False
        cookies_secure_prefix_found = False
        cookies_nameless_found = False
        cookies_secure_found = False

        for cookie in cookies_set:
            cookies_found = True

            if cookie.secure:
                cookies_secure_found = True
                ranks[rank]['total_cookies']['secure'] += 1

            if cookie.cookie_type == CookieType.NORMAL:
                cookies_normal_found = True
                ranks[rank]['total_cookies']['normal'] += 1
            elif cookie.cookie_type == CookieType.HOST_PREFIX:
                cookies_host_prefix_found = True
                ranks[rank]['total_cookies']['host_prefix'] += 1
                cookies_names['host_prefix'].append(cookie.name)
            elif cookie.cookie_type == CookieType.SECURE_PREFIX:
                cookies_secure_prefix_found = True
                ranks[rank]['total_cookies']['secure_prefix'] += 1
                cookies_names['secure_prefix'].append(cookie.name)
            elif cookie.cookie_type == CookieType.NAMELESS:
                cookies_nameless_found = True
                ranks[rank]['total_cookies']['nameless'] += 1
                cookies_names['nameless'].append(cookie.value)

        if cookies_found:
            ranks[rank]['origins_with_cookies']['total'] += 1
        if cookies_normal_found:
            ranks[rank]['origins_with_cookies']['normal'] += 1
        if cookies_host_prefix_found:
            ranks[rank]['origins_with_cookies']['host_prefix'] += 1
        if cookies_secure_prefix_found:
            ranks[rank]['origins_with_cookies']['secure_prefix'] += 1
        if cookies_nameless_found:
            ranks[rank]['origins_with_cookies']['nameless'] += 1
        if cookies_secure_found:
            ranks[rank]['origins_with_cookies']['secure'] += 1

        try:
            # add the number of HSTS headers
            hsts_found = False
            hsts_include_subdomains_found = False
            for hh in hstss[rank_origin]:
                hsts_found = True
                if REGEXP_HSTS_SUBDOMAINS.search(hh):
                    hsts_include_subdomains_found = True
                    break
            if hsts_found:
                ranks[rank]['hsts']['total'] += 1
            if hsts_include_subdomains_found:
                ranks[rank]['hsts']['include_subdomains'] += 1
        except KeyError:
            pass

    print('[*] ' + '='*80)
    print('[*] Rank:')
    print(json.dumps(ranks))
    print('[*] __Host- cookie names:')
    print_occurrences(cookies_names['host_prefix'])
    print('[*] __Secure- cookie names:')
    print_occurrences(cookies_names['secure_prefix'])
    print('[*] Nameless cookie values:')
    print_occurrences(cookies_names['nameless'])


def main():
    if len(sys.argv) != 2:
        print(f'Usage: python3 {sys.argv[0]} <csv_directory>')
        sys.exit(1)
    
    process_dir(sys.argv[1])
    analysis()


if __name__ == '__main__':
    main()