#!/usr/bin/env python

import csv, json, sys, chardet

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        try:
            yield dict([(key, unicode(value, chardet.detect(value)['encoding'] or "ascii")) for key, value in row.iteritems()])
        except UnicodeDecodeError:
            yield dict([(key, unicode(value, "latin2")) for key, value in row.iteritems()])

if len(sys.argv)>1:
   delim=sys.argv[1]
else:
   delim=';'
headers = csv.reader(sys.stdin, delimiter=delim).next()
reader = UnicodeDictReader(sys.stdin,fieldnames=headers, delimiter=delim)
for row in reader:
    print json.dumps(row).replace('\n','').encode('utf8')
