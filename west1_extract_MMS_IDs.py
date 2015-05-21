#!/usr/bin/env python
"""
First script in the workflow for producing WEST holdings update from
bibliographic records exported (in MARC21 binary) from Alma.

This script extracts the MMS IDs from the exported MARC file.
"""
# -*- coding: utf-8 -*-

from __future__ import print_function

import pymarc
from pymarc import MARCReader

import sys
import time
import os.path
import codecs

def usage(where=sys.stdout):
    """Print a usage statement for this script."""
    print('Extract MMS IDs from a MARC21 file.',
          file=where)    
    print('Usage:', file=where)
    print('  west1_extract_MMS_IDs.py <file.mrc>', file=where)
    print('Where:', file=where)
    print('  file.mrc            Binary MARC21 export of items',
          file=where)
    print('Output:', file=where)
    print('  Generates a datestamped text file: extracted-mms-ids.<date>.txt',
          file=where)

def fileCheck(filename):
    """Determines if file 'filename' exists."""
    if not os.path.isfile(filename):
        print('File: ' + filename + ' not found. Exiting...', file=sys.stderr)
        sys.exit(1)

def main(argv):
    if len(argv) != 2:
        usage(sys.stderr)
        sys.exit(1)

    # input file
    inMarcFile = argv[1]

    # filecheck inputs
    fileCheck(inMarcFile)

    # output file
    outFile = 'extracted-mms-ids.' + time.strftime("%Y%m%d") + '.txt'

    # marc writer
    writer = codecs.open(outFile, 'wb', 'utf-8')

    #------------------------------------------------------------------#
    # Parse the MARC file for the MMS IDs
    #------------------------------------------------------------------#

    print('Extracting MMS IDs...')
    marcReader = MARCReader(file(inMarcFile),
                            to_unicode=True, force_utf8=True)    

    count = 0
    for record in marcReader:
        count += 1
        if count % 250 == 0:
            print('  Extracting MMS ID #' + unicode(count) + '...')
            
        writer.write(record['001'].value() + u'\n')


    print('Finished. ' + unicode(count) + ' MMS ID(s) extracted.')

if __name__ == '__main__':
    main(sys.argv)
