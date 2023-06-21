#!/usr/bin/env python3

import sys
import csv
import json
from itertools import product
import requests

HOST = 'http://localhost'
SERVICES = {
    'php':      1700,
    'reactphp': 1701,
    'werkzeug': 1702
}


def next_key():
    """Generate possible 3-character cookie keys."""

    charset = '\'01abAB!"#$%&\\()*+,-./:;<=>?@[]^_`{|}~ '
    for x in product(list(charset), repeat=3):
        yield ''.join(x)


def main(csv_file):
    """Fuzz the services and write output differences into a CSV file."""
    
    with open(csv_file, 'w', newline='') as csv_file:
        fieldnames = ['cookie'] + list(SERVICES.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for k in next_key():
            cookie = f'{k}=foo'
            services = dict()
            for service, port in SERVICES.items():
                try:
                    r = requests.get(f'{HOST}:{port}/', headers={'Cookie': cookie})
                    services[service] = json.dumps(json.loads(r.text))
                except Exception:
                    services[service] = ''
            
            if len(set(services.values())) > 1:
                print(f'Found difference for {cookie}')
                writer.writerow({**{'cookie': cookie}, **services})


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <outfile.csv>')
        sys.exit(1)
    
    main(sys.argv[1])