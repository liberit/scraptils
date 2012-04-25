#!/usr/bin/env python

import csv, json, sys

reader = csv.DictReader( sys.stdin)
headers = reader.next()
reader.fieldnames=headers
print json.dumps( [ row for row in reader ] )
