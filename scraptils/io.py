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
from sys import stderr

def readlines(infile, outfile=None):
    l = infile.readline()
    while l:
        yield l
        try:
            l = infile.readline()
        except Exception, e:
            print >> stderr, '[E] Error reading %s: %r' % (infile.name, e.message)
            l = None

def read_json(data):
    try:
        chunk = json.loads(data)
    except Exception, e:
        print >> stderr, '[E] Cannot parse %r\n   %r' % (data, e.message)
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

# TODO!!
def parse_csv(infile, default_name='data'):
    field_names  = map(unicode.strip, infile.readline().decode('utf-8').split(','))
    field_values = map(unicode.strip, infile.readline().decode('utf-8').split(','))
    ret = dict(zip(field_names, field_values))
    name = ret.get('_name')
    if name:
        ret.pop('_name')
    else:
        name = default_name

    return (name, ret)

