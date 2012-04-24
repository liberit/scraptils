#!/usr/bin/env python


from flask import Flask, request, render_template, redirect, flash
from htsql import HTSQL
from os import listdir


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
    columns = data.records[0].__fields__
    return render_template('data.html', data=data, cols=columns, db=db)


def __main__():
    app.run(debug           = True
           ,use_debugger    = True
           ,port            = 5001
           )

if __name__ in ('__main__', 'datainspector'):
    __main__()
