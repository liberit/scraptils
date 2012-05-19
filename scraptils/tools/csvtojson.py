#!/usr/bin/env python

import csv, json, sys

reader = csv.DictReader( sys.stdin)
headers = csv.reader( sys.stdin).next()
reader.fieldnames=headers
for row in reader:
    print json.dumps(row).replace('\n','')
