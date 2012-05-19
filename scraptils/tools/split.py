#!/usr/bin/env python
# -*- coding: utf-8 -*-
# extracts single pages from pdfs.

from pyPdf import PdfFileWriter, PdfFileReader
import sys

output = PdfFileWriter()
input1 = PdfFileReader(file(sys.argv[1], "rb"))

# add page 1 from input1 to output document, unchanged
output.addPage(input1.getPage(int(sys.argv[2])))

# print how many pages input1 has:
#print "document1.pdf has %s pages." % (input1.getNumPages())

# finally, write "output" to document-output.pdf
outputStream = file(sys.argv[3], "wb")
output.write(outputStream)
