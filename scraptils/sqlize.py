#!/usr/bin/env python

# -*- coding: utf-8 -*-
#    This file is part of liberit.

#    liberit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    liberit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with liberit.  If not, see <http://www.gnu.org/licenses/>.

# (C) 2012 Adam Tauber <asciimoo@faszkorbacs.hu>


import json
from sqlalchemy import create_engine, Boolean, Integer, Float, String, Table, MetaData, Column, ForeignKey
import sys
from tempfile import mkstemp
from os import unlink

pytypes  = (bool, int, float, unicode)
sqltypes = (Boolean, Integer, Float, String)

def discover(table, data, schema=None):
    def mkstruct(): return {'_m2m': [], '_m2o': []}
    if not schema:
        schema = {table: mkstruct()}
    elif not schema.has_key(table):
        schema[table] = mkstruct()

    for key, value in data.items():
        if isinstance(value, dict):
            sub = discover(key, value)
            if sub:
                schema.update(sub)
                schema[table]['_m2o'].append(sub.keys()[0])
        elif isinstance(value, list):
            for i in value:
                # TODO
                pass
        elif type(value) in pytypes:
            if schema[table].has_key(key):
                if sqltypes.index(schema[table][key]) < pytypes.index(type(value)):
                    schema[table][key] = sqltypes[pytypes.index(type(value))]
            else:
                schema[table][key] = sqltypes[pytypes.index(type(value))]
        else:
            print '[!] Error - cannot handle value "%r" - %r' % (value, type(value))
    return schema

def read_json(data):
    try:
        chunk = json.loads(data)
    except Exception, e:
        print '[E] Cannot parse %r\n   %r' % (data, e.message)
        return {}
    return chunk

def parse_json(data, default_name='data'):
    chunk = read_json(data)
    name = chunk.get('_name')
    if name:
        chunk.pop('_name')
    else:
        name = default_name

    return (name, chunk)

def readlines(infile, outfile=None):
    l = infile.readline()
    while l:
        if outfile:
            outfile.write(l)
        yield l
        try:
            l = infile.readline()
        except Exception, e:
            print '[E] Error reading %s: %r' % (infile.name, e.message)
            l = None

def createschema(struct, metadata):
    for table_name, fields in struct.items():
        columns = [Column(x, y) for x,y in fields.items() if not x.startswith('_')]
        if fields['_m2o']:
            columns.extend(Column(x+'id', Integer, ForeignKey('%s.id' % x)) for x in fields['_m2o'])
        t = Table(table_name
                 ,metadata
                 ,Column('id', Integer, primary_key=True)
                 ,*columns
                 )



def insert_flat(table, data, meta, db):
    #connections = []
    for key, value in data.items():
        if isinstance(value, dict):
            #connections.append((key, value))
            data.pop(key)
        elif isinstance(value, list):
            data.pop(key)
    if not len(data): return
    d = meta.tables[table].insert(data)
    db.execute(d)
    # session.add(d)
    return d

def argparser():
    import argparse
    argp = argparse.ArgumentParser(description='Scraptils JSON SQLizer')
    argp.add_argument('-i', '--input'
                     ,help      = 'Input file - default is STDIN'
                     ,metavar   = 'FILE'
                     ,default   = sys.stdin
                     ,type      = argparse.FileType('r')
                     )
    argp.add_argument('-d', '--db'
                     ,help      = 'Database connection string - default is sqlite:///data.sqlite'
                     ,default   = 'sqlite:///data.sqlite'
                     )
    argp.add_argument('-t', '--type'
                     ,help      = 'Insertion type'
                     ,choices   = ('flat', 'recursive')
                     ,default   = 'flat'
                     )
    argp.add_argument('-v', '--verbose'
                     ,action    = 'count'
                     ,help      = 'Verbosity level - default is 3'
                     ,default   = 3
                     )
    return vars(argp.parse_args())


if __name__ == '__main__':
    #r = parse_json(json.dumps({'_name': 'data_table', 'test_int': 6, 'test_float': 4.4, 'test_str': 'asdf', 'conn_table': {'test_bool': True}}))
    #print parse_json(json.dumps({'_name': 'data_table', 'test_int': 6, 'test_float': 4.4, 'test_str': 'asdf', 'conn_table': {'test_bool': True}}), r)
    args = argparser()
    schema = {}
    tmp_file_name = mkstemp(prefix='sqlize_')[1]
    tmp_file = open(tmp_file_name, 'w')
    for line in readlines(args['input'], tmp_file):
        schema = discover(*parse_json(line), schema=schema)
    tmp_file.close()
    print schema
    engine = create_engine(args['db'], echo=True)
    meta = MetaData()
    meta.bind = engine
    createschema(schema, meta)
    print meta.sorted_tables
    meta.create_all()
    tmp_file = open(tmp_file_name)
    if args['type'] == 'flat':
        with engine.begin() as trans:
            for line in readlines(tmp_file):
                insert_flat(*parse_json(line), meta=meta, db=trans)
    else:
        #TODO
        pass
    unlink(tmp_file_name)
