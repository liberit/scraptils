#!/usr/bin/env python
# -*- coding: utf-8 -*-
# converts a pdf into a csv file

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTRect
from pdfminer.converter import PDFPageAggregator
from operator import itemgetter
import sys, csv, cStringIO, codecs, os
from pbs import pdftotext

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
        self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else s
                              for s in row])
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


def pdf2csv(pdf):
    fp = open(pdf, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    # Supply the password for initialization.
    # (If no password is set, give an empty string.)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    writer = UnicodeWriter(sys.stdout)
    for pageno, page in enumerate(doc.get_pages()):
        interpreter.process_page(page)
        layout = device.get_result()
        hlines=[]
        vlines=[]
        for i in layout:
            if not type(i) == LTRect: continue
            hlines.append(int(i.x0))
            hlines.append(int(i.x1))
            vlines.append(int(layout.height - i.y0))
            vlines.append(int(layout.height - i.y1))
        hlines=filterclose(sorted(set(hlines)))
        vlines=filterclose(sorted(set(vlines)))
        i=0
        while(i<len(vlines)-1):
            if not vlines[i+1]-vlines[i]>10:
                i=i+1
                continue
            j=0
            row=[]
            while(j<len(hlines)-1):
                if not hlines[j+1]-hlines[j]>10:
                    j=j+1
                    continue
                row.append(' '.join(get_region(pdf,
                                               pageno+1,
                                               hlines[j]+1,
                                               vlines[i],
                                               hlines[j+1]-1,
                                               vlines[i+1]).split()))
                j=j+1
            writer.writerow(row)
            i=i+1
    fp.close()

def filterclose(lst):
    i=1
    tmp=[lst[0]]
    while i<len(lst):
        if lst[i]-2>tmp[-1]:
            tmp.append(lst[i])
        i=i+1
    return tmp

def get_region(pdf, page, x1,y1,x2,y2):
    # this is an extremely ugly hack. should be reimplemented with
    # some poppler like lib, which itself only supports getting
    # "selected" text, having some different logic than the
    # simple one used in pdftotext
    return pdftotext('-nopgbrk',
                     '-f', page,
                     '-l', page,
                     '-x', x1,
                     '-y', y1,
                     '-H', abs(y2-y1),
                     '-W', abs(x2-x1),
                     pdf,
                     '-'
                     )

if __name__=='__main__':
    pdf2csv(sys.argv[1])
