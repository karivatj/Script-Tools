# !/usr/bin/python
#  -*- coding: utf-8 -*-

import sys
import comtypes.client
from optparse import OptionParser

def convert(inputfilename, outputfilename, word):
    doc = word.Documents.Open(inputfilename)
    doc.SaveAs(outputfilename, FileFormat=wdFormatPDF)
    doc.Close()
    return 0  

if __name__== "__main__":
    parser = OptionParser(usage="Usage: %prog [OPTIONS]\nTry '%prog --help' for more information.", version="%prog 1.0")
    parser.add_option("--input",
                  action="store",
                  dest="input",
                  default="",
                  help="input filename",) 
    parser.add_option("--output",
                  action="store",
                  dest="output",
                  default="",
                  help="output filename")             
    (options, args) = parser.parse_args()

    inputfilename  = options.input
    outputfilename = options.output

    print(inputfilename)
    print(outputfilename)
    if inputfilename == "" or outputfilename == "":
        sys.exit(1)
    try:
        print(outputfilename)
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False
        result = convert(inputfilename, outputfilename, word)
        sys.exit(result)
    except Exception as e:
        sys.exit(2)