#!/usr/bin/env python3
#
# Author: Kari Vatjus-Anttila <kari.vatjusanttila@gmail.com
#
# For conditions of distribution and use, see copyright notice in LICENSE
#

import sys
import argparse

import CacheIO
import CacheSourceContainer
import CacheProductionContainer

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="Input file to be read", type=str, default="")
parser.add_argument("--production", help="Defines if the input XML is a Caché Production", action='store_true')
parser.add_argument("--source", help="Defines if the input XML contains Caché Source code", action='store_true')
parser.add_argument("--plantuml", help="if set, output plantUML graph from the data", action='store_true')
parser.add_argument("--graphml", help="if set, output graphML graph from the data", action='store_true')
parser.add_argument("--verbose", help="if set, output debug to console", action='store_true')
args = parser.parse_args()

if __name__ == '__main__':
    container = None
    if args.input is "":
        print("Please define the input file to be processed")
        sys.exit()
    if args.production is False and args.source is False:
        print("Please define what type of file is the input")
        sys.exit()
    if args.production is True:
        container = CacheProductionContainer.CacheProductionContainer()
    else:
        container = CacheProductionContainer.CacheSourceContainer()

    cacheio = CacheIO.CacheIO(container)
    cacheio.importFromFile(args.input)

    # debug
    if args.verbose:
        print()
        print("All done")
        print("Container contents")
        print(container.toString())

    if args.plantuml:
        cacheio.exportPlantUML()
    if args.graphml:
        cacheio.exportGraphML()