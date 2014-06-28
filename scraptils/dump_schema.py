#!/usr/bin/env python
# -*- coding: utf-8 -*-
#    This file is part of composite data analysis tools (cdat)

#    composite data analysis tools (cdat) is free software: you can
#    redistribute it and/or modify it under the terms of the GNU
#    Affero General Public License as published by the Free Software
#    Foundation, either version 3 of the License, or (at your option)
#    any later version.

#    composite data analysis tools (cdat) is distributed in the hope
#    that it will be useful, but WITHOUT ANY WARRANTY; without even
#    the implied warranty of MERCHANTABILITY or FITNESS FOR A
#    PARTICULAR PURPOSE.  See the GNU Affero General Public License
#    for more details.

#    You should have received a copy of the GNU Affero General Public
#    License along with composite data analysis tools (cdat) If not,
#    see <http://www.gnu.org/licenses/>.

# (C) 2011 by Stefan Marsiske, <stefan.marsiske@gmail.com>
# (C) 2013 by Adam Tauber, <asciimoo@gmail.com>

import sys
import pprint
from itertools import izip_longest
from operator import itemgetter

def unws(txt):
    return u' '.join(txt.split())

def dump_schema(items, skip=[], title=None, format="text"):
    """
    Dump schema: takes a list of data structures and computes a
    probabalistic schema out of the samples, it prints out the result
    to the output.
    @param count is optional and in case your items list is some kind of cursor that has no __len__
    @param skip is an optional list of keys to skip on the top structure
    @param title is the name for the data structure to be displayed
    @param format <text|full-html|html> - html is default - full html adds a js/css header and a legend
    """
    ax={}
    count=0
    for item in items:
        ax=scan(dict([(k,v) for k,v in item.items() if k not in skip]),ax)
        count+=1
    if format=='text':
        print_schema(ax,0,count)
        return
    elif format=='full-html':
        print '%s<div class="schema">%s</div>%s' % (_html_header(),
                                                    '\n'.join([str(x) for x in html_schema(ax,0,count)]),
                                                    _html_footer())
    else:
        print '<div class="schema">%s</div>' % '\n'.join([str(x) for x in html_schema(ax,0,count)])

def type_name(o):
    return str(type(o)).split("'")[1]

def scan(d, node):
    """ helper for dump_schema"""
    if not 'types' in node:
        node['types']={}
    if hasattr(d, 'keys'):
        for k, v in d.items():
            if not 'items' in node:
                node['items']={}
            if not k in node['items']:
                node['items'][k]={'name':k}
            node['items'][k]=scan(v,node['items'][k])
    elif isinstance(d,str):
        d=d.decode('utf8')
    elif hasattr(d, '__iter__'):
        if not 'elems' in node:
            node['elems']={}
        for v in d:
            stype = type_name(v)
            node['elems'][stype]=scan(v,node['elems'].get(stype,{}))
    if isinstance(d, unicode):
        d=unws(d) or None
    mtype=type_name(d)
    tmp=node['types'].get(mtype,{'count': 0, 'example': None})
    tmp['count']+=1
    if d and not tmp['example'] and not isinstance(d,dict):
        tmp['example']=d
    node['types'][mtype]=tmp
    return node

def merge_dict_lists(node):
    # ultra ugly. see test code in arch
    if ('elems' in node and
        'items' in node and
        'items' in node['elems'].values()[0] and
        sorted(node['items'].keys())==sorted(node['elems'].values()[0]['items'].keys())):

        node['types']["list"]['count']+=node['types']["dict"]['count']
        node['elems']["dict"]['types']["dict"]['count']+=node['types']["dict"]['count']
        del node['types']["dict"]

        for k,v in node['items'].items():
            if not k in node['elems'].values()[0]['items']:
                node['elems'].values()[0]['items'][k]=v
                continue
            for tk, tv in v['types'].items():
                if tk in node['elems'].values()[0]['items'][k]['types']:
                    node['elems'].values()[0]['items'][k]['types'][tk]['count']+=tv['count']
                else:
                    node['elems'].values()[0]['items'][k]['types'][tk]=tv
        del node['items']
    return node

def print_schema(node,indent,parent,after_list=False):
    """ helper for dump_schema"""
    merge_dict_lists(node)
    for k,v in sorted(node['types'].items(),key=lambda x: x[1]['count'],reverse=True):
        nodestr = node.get('name', '')
        if nodestr: nodestr = '| '+nodestr.ljust(40-indent*2)
        # unicode after a list fix
        if after_list and nodestr == '' and k == 'unicode':
            print "{0:>5}%".format((v['count']*100)/parent), ' '*(indent*2+37), ('[%s]' % k).ljust(10),
        else:
            print "{0:>5}%".format((v['count']*100)/parent), '  '*indent, nodestr, ('<%s>' % k).ljust(10),
        if k=="list":
            print ''
            for x in node['elems'].values():
                print_schema(x,indent+1,v['count'],True)
        elif k=="dict":
            print ''
            if 'items' in node:
                for x in node['items'].values():
                    print_schema(x,indent+1,v['count'])
            #TODO else: # empty dict
        elif k=="unicode":
            print v['example'].encode('utf8')
        else:
            print v['example']

schematpl="<dl style='background-color: #{3:02x}{3:02x}{3:02x};'><dt>{1} <span class='p'>({0}%)</span></dt><dd> <div class='{4}'>{2}</div></dd></dl>"
def html_schema(node,indent,parent):
    """ helper for dump_schema"""
    merge_dict_lists(node)
    res=[]
    for k,v in sorted(node['types'].items(),key=lambda x: x[1]['count'],reverse=True):
        if k=="list":
            data="<ul>{0}</ul>".format(''.join(["<li>{0}</li>".format(y) for x in node['elems'].values() for y in html_schema(x,indent+1,v['count'])]))
            clss='contents'
        elif k=="dict":
            data="<ul>{0}</ul>".format(''.join(["<li>{0}</li>".format(y) for x in node['items'].values() for y in html_schema(x,indent+1,v['count'])]))
            clss='contents'
        elif k=="unicode":
            data="Example: {0}".format(v['example'].encode('utf8'))
            clss='example'
        elif k=="str":
            data="Example: {0}".format(v['example'])
            clss='example'
        else:
            data="Example: {0}".format(v['example'])
            clss= 'example'
        res.append(schematpl.format(int(float(v['count'])/parent*100 if k!="list" else v['count']),
                                    node.get('name','&lt;listitem&gt;'),
                                    data,
                                    256-int(64*(1 if v['count']>=parent else float(v['count'])/parent)),
                                    clss,
                                    ))
    return res

def _html_header():
    """ helper for html_schema"""
    return """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <style>
    dt { display: inline; cursor: pointer; color: #288; }
    dd { display: inline; margin-left: 0;}
    dl { margin-top: .4em; }
    ul { list-style: none; }
    .contents, .example { margin-left: 2em; background-color: white}
    .type { font-style: italic }
    .p { font-size: .8em }
    .schema-legend { font-size: .8em; font-style: italic; }
    </style>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.6.2.js"> </script>
    <script type="text/javascript">
    $(document).ready(function() {
       $('div.contents').hide();
       $('.schema > dl > dd > div.contents').show();
       $('dt').click(function() {
         $(this).parent().find('div.contents:first').toggle();
       });
    });
    </script>
    </head>
    <body>
    <div class="schema-legend">Click on the names to fold/expand levels. Percentages show probability of this field appearing under it's parent. In case of lists, percentage also shows average length of list.</div>
    """

def _html_footer():
    """ helper for html_schema"""
    return """
    </body>
    </html>
    """

def diff(old, new, path=[]):
    """a handy comparison function for composite data structures"""
    if old==None and new!=None:
        return [{'type': 'added', 'data': new, 'path': path}]
    elif new==None and old!=None:
        return [{'type': 'deleted', 'data': old, 'path': path}]
    if type(old) == str: old=unicode(old,'utf8')
    if type(new) == str: new=unicode(new,'utf8')
    if not type(old)==type(new):
        return [{'type': 'changed', 'data': (old, new), 'path': path}]
    elif hasattr(old,'keys'):
        res=[]
        for k in set(old.keys() + (new or {}).keys()):
            r=diff(old.get(k),(new or {}).get(k), path+[k])
            if r:
                res.extend(r)
        return res
    elif hasattr(old,'__iter__'):
        res=[]
        for item in filter(None,[diff(a,b,path+[(len(old) if len(old)<len(new) else len(new))-i]) for i,(a,b) in enumerate(izip_longest(reversed(old),reversed(new)))]):
            if type(item)==list:
                res.extend(item)
            else:
                res.append(item)
        return res
    elif old != new:
        return [{'type': 'changed', 'data': (old, new), 'path': path}]
    return

def printdict(d):
    """ helper function for formatdiff"""
    if type(d)==list:
        return u'<ul>%s</ul>' % '\n'.join(["<li>%s</li>" % printdict(v) for v in d])
    if not type(d)==dict:
        return "%s" % unicode(d)
    res=['']
    for k,v in [(k,v) for k,v in d.items() if k not in ['mepref','comref']]:
        res.append(u"<dl><dt>%s</dt><dd>%s</dd></dl>" % (k,printdict(v)))
    return '%s' % u'\n'.join(res)

def formatdiff(data):
    """ formats diffs to html """
    res=[]
    for di in sorted(sorted(data,key=itemgetter('path'))):
        if di['type']=='changed':
            res.append(u'<tr><td>change</td><td>%s</td><td>%s</td><td>%s</td></tr>' % ('/'.join([str(x) for x in di['path']]),printdict(di['data'][1]),printdict(di['data'][0])))
            continue
        if di['type']=='deleted':
            res.append(u"<tr><td>%s</td><td>%s</td><td></td><td>%s</td></tr>" % (di['type'], '/'.join([str(x) for x in di['path']]), printdict(di['data'])))
        if di['type']=='added':
            res.append(u"<tr><td>%s</td><td>%s</td><td>%s</td><td></td></tr>" % (di['type'], '/'.join([str(x) for x in di['path']]), printdict(di['data'])))

    return "<table><thead><tr width='90%%'><th>type</th><th>change in</th><th>new</th><th>old</th></tr></thead><tbody>%s</tbody></table>" % '\n'.join(res)

def test_diff():
    d2={ 'a': [ {'aa': 2, 'bb': 3 }, { 'aa': 1, 'bb':3 }, {'AA': 1, 'BB': { 'asdf': { 'asdf': 'qwer'}}}, {'Mm': [ 'a','b','c','d'] } ],
         'c': [ 0,1,2,3,4]}
    d1={ 'a': [ { 'aa': 1, 'bb':3 }, {'AA': 1, 'BB': { 'asdf': '2'}}, {'Mm': [ 'a','b','c','d'] } ],
         'b': { 'z': 9, 'x': 8 },
         'c': [ 1,2,3,4]}
    d=diff(d1,d2)
    pprint.pprint(d)
    print formatdiff(d)

def stripns(attr):
   ns = ['{http://www.w3.org/1999/xlink}',
         '{http://intragate.ec.europa.eu/transparencyregister/intws/20110715}']
   for n in ns:
       if attr.startswith(n):
           return attr[len(n):]
   return attr

def _xml2obj(elem,c=False):
    res={}
    if elem.text:
        #if c: print "text", stripns(elem.tag)
        res[stripns(elem.tag)]=unws(elem.text)
    if len(elem.attrib)>0:
        if stripns(elem.tag) in [stripns(x) for x in elem.attrib]:
            print >>sys.stderr, "attribute clashes with element", stripns(elem.tag), "suppressed attribute value", elem.attrib[stripns(elem.tag)]
        #if c: print "attr", stripns(elem.tag)
        res.update({stripns(attr): elem.attrib[attr] for attr in elem.attrib})
    kids=elem.xpath('./*')
    if len(kids)>0:
        if len(set((stripns(kid.tag) for kid in kids)))==len(kids):
            #if c: print "dict", stripns(elem.tag)
            tmp={}
            for kid in kids:
                kido=_xml2obj(kid, c=True)
                name=stripns(kid.tag)
                if not kido or not stripns(kid.tag) in kido:
                    continue
                tmp[name]=kido[name]
            res[stripns(elem.tag)]=tmp
        else:
            #if c: print "list", stripns(elem.tag)
            res[stripns(elem.tag)]=[_xml2obj(kid) for kid in kids if _xml2obj(kid)]
    if c: pprint.pprint(res), stripns(elem.tag)
    return res

def xml2obj(root):
    for elem in root.xpath('//t:resultList/*',
                           namespaces={'t': 'http://intragate.ec.europa.eu/transparencyregister/intws/20110715'}):
        yield _xml2obj(elem)

def test_dump(fname, html_only=False):
    from lxml.etree import parse
    root=None
    with open(fname, 'r') as fd:
        root=parse(fd)
    elements=xml2obj(root)
    if html_only:
        dump_schema(elements,title='lobbyregister',format='full-html')
    else:
        dump_schema(elements,title='lobbyregister',format='text')


def argparser():
    import argparse
    argp = argparse.ArgumentParser(description='Scraptils data schema analyzer')
    argp.add_argument('-i', '--input'
                     ,help      = 'Input file - default is STDIN'
                     ,metavar   = 'FILE'
                     ,default   = sys.stdin
                     ,type      = argparse.FileType('r')
                     )
    argp.add_argument('-l', '--limit'
                     ,help      = 'Limit the number of input lines'
                     ,default   = 0
                     ,type      = int
                     )
    argp.add_argument('-f', '--format'
                     ,help      = 'Output type'
                     ,choices   = ('text', 'html', 'full-html')
                     ,default   = 'text'
                     )
    return vars(argp.parse_args())


if __name__ == "__main__":
    #test_diff()
    from json import loads
    args = argparser()
    d = []
    lineno = 0
    while True:
        if args['limit'] > 0 and args['limit'] <= lineno:
            break

        line = args['input'].readline()

        if not line:
            break

        d.append(loads(line.strip()))
        lineno += 1

    dump_schema(d, format=args['format'])
