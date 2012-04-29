#!/usr/bin/env python


from flask import Flask, request, render_template, redirect, flash, jsonify, Response
from htsql import HTSQL
from os import listdir
import cStringIO, csv, codecs


DB_DIR = './data'

app = Flask(__name__)
app.secret_key = 'yourveryverysecretkeystring'


def connect(db_string):
    return HTSQL(db_string)

def loadsqlites(path):
    return dict((db.replace('.sqlite', ''), 'sqlite:%s/%s' % (path, db)) for db in listdir(path) if db.endswith('.sqlite'))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/q', methods=['POST'])
def query_redirect():
    q_str = request.form.get('query')
    return redirect('/q/'+q_str)

@app.route('/q/<string:db>/<path:q>', methods=['GET'])
def do_query(db, q):
    (data, columns, q) = query(request, db, q)
    return render_template('data.html', data=data, cols=columns, db=db, query=q)

@app.route('/csv/<string:db>/<path:q>', methods=['GET'])
def csv_query(db, q):
    (data, columns, q) = query(request, db, q)
    fd = cStringIO.StringIO()
    writer = UnicodeWriter(fd)
    writer.writerow(columns)
    writer.writerows(data)
    fd.seek(0)
    return Response( response=fd.read(), mimetype="text/csv" )

@app.route('/json/<string:db>/<path:q>', methods=['GET'])
def json_query(db, q):
    (data, columns, q) = query(request, db, q)
    return jsonify({'count': len(data.records), 'data': data.records})

def query(request, db, q):
    global DB_DIR
    filters = request.url.replace(request.base_url, '', 1)
    dbs = loadsqlites(DB_DIR)
    if not dbs.has_key(db):
        return '[!] missing db'
    htsql = HTSQL(dbs[db])
    if filters and ('?' in q):
        filters = '&%s' % filters.strip()[1:]
    q = '/%s%s' % (q, filters or '')
    data = htsql.produce(str(q))
    return (data, data.records[0].__fields__, q)

def __main__():
    app.run(debug           = True
           ,use_debugger    = True
           ,port            = 5001
           )

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    src: http://docs.python.org/library/csv.html#writer-objects
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else s for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

if __name__ in ('__main__', 'datainspector'):
    __main__()
