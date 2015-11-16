#!/usr/bin/env python
"""
Fourth script in the workflow for producing WEST holdings update from
bibliographic records exported (in MARC21 binary) from Alma.

This script converts the MARCXML collected by west3... and converts the
data into MARC21 binary while preserving the unicode data as necessary.
"""
# -*- coding: utf-8 -*-

##########################################################################
# Copyright (c) 2015 Katherine Deibel
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED 'AS IS' AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
##########################################################################

from __future__ import print_function

import sys
import time
import os.path
import codecs

import pymarc

def usage(where=sys.stdout):
    """Print a usage statement for this script."""
    print('Convert MARCXML to MARC21 binary.',
          file=where)    
    print('Usage:', file=where)
    print('  west4_convert_XML_to_MARC21.py <file.xml>', file=where)
    print('Where:', file=where)
    print('  file.xml            MARCXML file)',
          file=where)
    print('Output:', file=where)
    print('  Generates a datestamped MARC21 file: wau.alma.archived <date>.mrc',
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

    # inputs
    inFile = argv[1]

    # filecheck inputs
    fileCheck(inFile)

    # output file
    outFile = 'wau.alma.archived.' + time.strftime("%Y%m%d") + '.mrc'


    # file streams
    writer = codecs.open(outFile, 'wb', 'utf-8')

    #------------------------------------------------------------------#
    # Read an MMS ID, make a REST Call, Store Both IDs
    #------------------------------------------------------------------#
    print('Reading MARCXML file...')
    records = pymarc.parse_xml_to_array(inFile)

    count = 0
    for rec in records:
        count += 1

        if count % 250 == 0:
            print('  Processing record #' + unicode(count) + '...')
            
        # force utf-8
        rec.force_utf8 = True
        # get string representation of marc
        marc = rec.as_marc()
        # decode character set
        marc = marc.decode('utf-8')
        
        # output
        writer.write(marc)

    # close the XML
    writer.write('</collection>\n')
    
    print('Finished. ' + unicode(count) + ' MARCXML records converted to MARC21 binary.')

if __name__ == '__main__':
    main(sys.argv)
