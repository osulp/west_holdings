#!/usr/bin/env python
"""
Second script in the workflow for producing WEST holdings update from
bibliographic records exported (in MARC21 binary) from Alma.

This script gathers Holding IDs associated with extracted MMS IDs.
"""
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import time
import os.path
import codecs

from lxml import etree

from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

def usage(where=sys.stdout):
    """Print a usage statement for this script."""
    print('Gather Holding IDs via REST using a list of MMS IDs.',
          file=where)    
    print('Usage:', file=where)
    print('  west2_gather_Holding_IDs.py <file.txt> <APIKEY>', file=where)
    print('Where:', file=where)
    print('  file.txt            List of MSS IDs (one / line)',
          file=where)
    print(' APIKEY               API key for accessing Alma REST APIs',
          file=where)
    print('Output:', file=where)
    print('  Generates a datestamped text file: holding-and-mss-ids.<date>.txt',
          file=where)
    print('  consisting of lines holding_id<tab>mms_id', file=where)

def fileCheck(filename):
    """Determines if file 'filename' exists."""
    if not os.path.isfile(filename):
        print('File: ' + filename + ' not found. Exiting...', file=sys.stderr)
        sys.exit(1)

def GetHoldingID(mmsID, apikey):
    """
    Make a REST call: Retrive Holdings List and return the value in
    the <holding_id> tag of the returned XML.
    """
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings'
    url = url.replace('{mms_id}',quote_plus(mmsID))    

    queryParams = '?' + urlencode({ quote_plus('apikey') : apikey  })

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()

    data_xml = etree.fromstring(response_body)

    return data_xml.findtext('.//holding_id')

def main(argv):
    if len(argv) != 3:
        usage(sys.stderr)
        sys.exit(1)

    # inputs
    inFile = argv[1]
    apikey = argv[2]

    # filecheck inputs
    fileCheck(inFile)

    # output file
    outFile = 'holding-and-mss-ids.' + time.strftime("%Y%m%d") + '.txt'


    # file streams
    reader = codecs.open(inFile, 'rt', 'utf-8')
    writer = codecs.open(outFile, 'wb', 'utf-8')

    #------------------------------------------------------------------#
    # Read an MMS ID, make a REST Call, Store Both IDs
    #------------------------------------------------------------------#
    print('Gathering Holding IDs...')
    count = 0
    for line in reader:
        count += 1

        if count % 250 == 0:
            print('  Gathering holding ID #' + unicode(count) + '...')
            
        # must strip mmsID to avoid any newlines
        mmsID = line.strip()
        holdingID = GetHoldingID(mmsID,apikey)
        writer.write(holdingID + u'\t' + mmsID + u'\n')        

    print('Finished. ' + unicode(count) + ' Holding ID(s) gathered.')

if __name__ == '__main__':
    main(sys.argv)
