# !/usr/bin/python
#  -*- coding: utf-8 -*-

import comtypes.client
import os
import sys
from optparse import OptionParser

wdFormatPDF = 17

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

    if inputfilename == "" or outputfilename == "":
        print("No input / output filename given.")
        sys.exit(1)
    try:
        print(outputfilename)
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False
        result = convert(inputfilename, outputfilename, word)
        print("Conversion done.")
        sys.exit(result)
    except Exception as e:
        print(e)
        sys.exit(2)
