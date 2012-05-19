#!/usr/bin/env python
# -*- coding: utf-8 -*-
# shows the cells as calculated by pdf2csv in pngs

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTRect, LTLine
from pdfminer.converter import PDFPageAggregator
from operator import itemgetter
import sys, os
import Image, ImageDraw

def pdf2csv(fp):
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    doc = PDFDocument()
    # Connect the parser and document objects.
    parser.set_document(doc)
    doc.set_parser(parser)
    # Supply the password for initialization.
    # (If no password is set, give an empty string.)
    doc.initialize('')
    # Check if the document allows text extraction. If not, abort.
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for pageno, page in enumerate(doc.get_pages()):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        #import code; code.interact(local=locals());
        hlines=[]
        vlines=[]
        for i in layout:
            if not type(i) in (LTRect, LTLine): continue
            hlines.append(int(i.x0))
            hlines.append(int(i.x1))
            vlines.append(int(layout.height - i.y0))
            vlines.append(int(layout.height - i.y1))
        hlines=filterclose(sorted(set(hlines)))
        vlines=filterclose(sorted(set(vlines)))
        print hlines
        print vlines
        print (layout.width, layout.height)
        i=0
        im = Image.new('1', (int(layout.width), int(layout.height)))
        draw = ImageDraw.Draw(im)
        while(i<len(vlines)-1):
            if not vlines[i+1]-vlines[i]>5:
                i=i+1
                continue
            j=0
            while(j<len(hlines)-1):
                if not hlines[j+1]-hlines[j]>5:
                    j=j+1
                    continue
                draw.rectangle([(int(hlines[j]),int(vlines[i])),(int(hlines[j+1]),int(vlines[i+1]))], outline=1)
                j=j+1
            i=i+1
        del draw
        fp=open("out%s.png" % pageno,'wb')
        im.save(fp,"PNG")
        fp.close()

def filterclose(lst):
    if not lst: return lst
    i=1
    tmp=[lst[0]]
    while i<len(lst):
        if lst[i]-2>tmp[-1]:
            tmp.append(lst[i])
        i=i+1
    return tmp

if __name__=='__main__':
    fp = open(sys.argv[1], 'rb')
    pdf2csv(fp)
    fp.close()
