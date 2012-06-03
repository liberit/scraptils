#!/usr/bin/env python


from flask import Flask, request, render_template, redirect, jsonify, Response, abort
from htsql import HTSQL
from os import listdir
import cStringIO, csv, codecs, json


DB_DIR = './data'
DBS = {}
def empty_meta():
    return {'scraper'     : {'source': '', 'license': ''}
           ,'title'       : ''
           ,'description' : ''
           ,'license'     : 'ODBL'
           ,'author'      : {'title': 'liberit', 'url': 'http://liberit.hu'}
           ,'deftable'    : 'data'
           ,'run_every'   : '1d'
           }

app = Flask(__name__)
app.secret_key = 'yourveryverysecretkeystring'


def connect(db_string):
    return HTSQL(db_string)

def loadsqlites(path):
    global DBS, DB_DIR, EMPTY_META
    sqlites = dict((db[:-len('.sqlite')], {'connection': 'sqlite:%s/%s' % (path, db), 'meta': {}}) for db in listdir(path) if db.endswith('.sqlite'))

    for db in sqlites.keys():
        sqlites[db]['name']  = db
        try:
            f=open('%s/%s.json' % (DB_DIR, db),'r')
            sqlites[db]['meta']  = json.load(f)
            f.close()
        except:
            sqlites[db]['meta'] = empty_meta()
            sqlites[db]['meta']['deftable'] = db
            sqlites[db]['meta']['title'] = db
    DBS.update(sqlites)
    return DBS




#@app.route('/', methods=['GET'])
#def index():
#    return render_template('index.html')

@app.route('/q', methods=['POST'])
def query_redirect():
    q_str = request.form.get('query')
    return redirect('/q/'+q_str)

@app.route('/', methods=['GET'])
def datasets():
    global DBS
    return render_template('datasets.html', dbs=DBS.values())

@app.route('/reload', methods=['GET'])
def reload():
    global DB_DIR
    loadsqlites(DB_DIR)
    return redirect('/')

@app.route('/q/<string:db_name>/<path:q>', methods=['GET'])
def html_query(db_name, q):
    global DBS
    db = DBS.get(db_name)
    if not db:
        abort(404)
    (data, columns, q) = query(request, db_name, q)
    columns = json.dumps([{'id': '_'.join(x.split()), 'name': x, 'field': x, 'sortable': True} for x in columns])
    return render_template('data.html', data=json.dumps([dict(zip(x.__fields__, [y for y in x])) for x in data]), cols=columns, db=db['name'], query=q, meta=db['meta'])

@app.route('/csv/<string:db>/<path:q>', methods=['GET'])
def csv_query(db, q):
    (data, columns, q) = query(request, db, q)
    fd = cStringIO.StringIO()
    writer = UnicodeWriter(fd)
    writer.writerow(columns)
    writer.writerows(data)
    fd.seek(0)
    return Response(response=fd.read(), mimetype="text/csv")

@app.route('/sqlite/<string:db>', methods=['GET'])
def sqlite_download(db):
    try:
        f=open('%s/%s.sqlite' % (DB_DIR, db),'r')
    except:
        abort(404)
    return Response(response=f.read(), mimetype="application/sqlite")

@app.route('/json/<string:db>/<path:q>', methods=['GET'])
def json_query(db, q):
    (data, columns, q) = query(request, db, q)
    return jsonify({'count': len(data.records), 'data': data.records})

def query(request, db, q):
    global DBS
    if not DBS.has_key(db):
        abort(404)
    filters = request.url.replace(request.base_url, '', 1)
    htsql = HTSQL(DBS[db]['connection'])
    if filters and ('?' in q):
        filters = '&%s' % filters.strip()[1:]
    q = '/%s%s' % (q, filters or '')
    data = htsql.produce(str(q))
    return (data, data.records[0].__fields__, q)

def __main__():
    global DB_DIR
    loadsqlites(DB_DIR)
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
