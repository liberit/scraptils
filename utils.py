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

# (C) 2012 Stefan Marsiske <s@ctrlc.hu>

import urllib2, cookielib, time, sys, json
from lxml.html.soupparser import parse
from lxml.etree import tostring
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()),
                              urllib2.ProxyHandler({'http': 'http://localhost:8123/'}))
opener.addheaders = [('User-agent', 'liberit/0.1')]

def fetch(url, retries=5, ignore=[], params=None):
    # url to etree
    try:
        f=opener.open(url, params)
    except (urllib2.HTTPError, urllib2.URLError), e:
        if hasattr(e, 'code') and e.code>=400 and e.code not in [504, 502]+ignore:
            print >>sys.stderr, "[!] %d %s" % (e.code, url)
            raise
        if retries>0:
            timeout=4*(6-retries)
            print >>sys.stderr, "[!] failed: %d %s, sleeping %ss" % (e.code, url, timeout)
            time.sleep(timeout)
            f=fetch(url,retries-1, ignore=ignore)
        else:
            raise
    return parse(f)

def dateJSONhandler(obj):
    if hasattr(obj, 'isoformat'):
        return unicode(obj.isoformat())
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def jdump(d):
    return json.dumps(d, indent=1, default=dateJSONhandler, ensure_ascii=False)

def unws(txt):
    return u' '.join(txt.split())

def getFrag(url, path):
    return fetch(url).xpath(path)

