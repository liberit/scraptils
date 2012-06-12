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

from scraptils.io import parse_json, readlines
from sys import stdin, stderr, exit
import re

disallowed_chars = re.compile('[^a-zA-Z_]', re.U)

def clean(field, maxwidth=40):
    global disallowed_chars
    return disallowed_chars.sub('_', field).lower()[:maxwidth]

def insert(model, table_name, data):
    assert isinstance(data, dict)
    ret = {}
    relations = {}
    for key, value in data.items():
        if key == '_name':
            continue
        key = clean(key)
        if isinstance(value, dict):
            item = insert(model, key, value)
            model['session'].add(item)
            if relations.get(key):
                relations[key].append(item)
            else:
                relations[key] = [item]
        elif isinstance(value, list):
            for i in value:
                item = insert(model, key, i)
                model['session'].add(item)
                if relations.get(key):
                    relations[key].append(item)
                else:
                    relations[key] = [item]
        else:
            ret[key] = value
    obj = model.get(table_name.capitalize())(**ret)
    for rel_name, rel in relations.items():
        getattr(obj, rel_name+'s').extend(rel)
    return obj

def argparser():
    import argparse
    argp = argparse.ArgumentParser(description='Scraptils SQLAlchemy database insert script')
    argp.add_argument('-i', '--input'
                     ,help      = 'Input file - default is STDIN'
                     ,metavar   = 'FILE'
                     ,default   = stdin
                     ,type      = argparse.FileType('r')
                     )
    argp.add_argument('-t', '--input-type'
                     ,help      = 'Input file type'
                     ,choices   = ('json', 'csv')
                     ,default   = 'json'
                     )
    argp.add_argument(help      = 'Sqlalchemy model file (model.py)'
                     ,metavar   = 'FILE'
                     ,dest      = 'model'
                     ,type      = argparse.FileType('r')
                     )
    return vars(argp.parse_args())

if __name__ == '__main__':
    args = argparser()
    model = {}
    try:
        exec(args['model'].read(), model)
    except:
        exit('[!] cannot import model (%s)' % args['model'].name)

    if args['input_type'] == 'json':
        for line in readlines(args['input']):
            item = insert(model, *parse_json(line))
            model['session'].add(item)

    elif args['input_type'] == 'csv':
        print >>stderr, '[!] TODO CSV support'
    print model['session'].commit()