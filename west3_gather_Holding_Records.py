#!/usr/bin/env python
"""
Third script in the workflow for producing WEST holdings update from
bibliographic records exported (in MARC21 binary) from Alma.

This script gathers Holding Records based on gathered Holding/MSS ids.
Also makes sure the holding ID is placed in the 001 field and the MMS
ID in the 004 field.

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

from lxml import etree
from copy import deepcopy

from urllib2 import Request, urlopen
from urllib import urlencode, quote_plus

def usage(where=sys.stdout):
    """Print a usage statement for this script."""
    print('Gather Holding Records via REST using a list of Holding and MMS IDs.',
          file=where)    
    print('Usage:', file=where)
    print('  west3_gather_Holding_IDs.py <file.txt> <APIKEY>', file=where)
    print('Where:', file=where)
    print('  file.txt            List of Holding/MSS IDs (Holding\tMMS per line)',
          file=where)
    print(' APIKEY               API key for accessing Alma REST APIs',
          file=where)
    print('Output:', file=where)
    print('  Generates a datestamped MARCXML file: wau.alma.archived <date>.xml',
          file=where)
    print('  consisting of lines holding_id<tab>mms_id', file=where)

def fileCheck(filename):
    """Determines if file 'filename' exists."""
    if not os.path.isfile(filename):
        print('File: ' + filename + ' not found. Exiting...', file=sys.stderr)
        sys.exit(1)

def GetHoldingXML(mmsID, holdingID, apikey):
    """
    Make a REST call: Retrive Holdings List and return received XML.
    """    
    url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/{mms_id}/holdings/{holding_id}'
    url = url.replace('{mms_id}',quote_plus(mmsID))
    url = url.replace('{holding_id}',quote_plus(holdingID))

    queryParams = '?' + urlencode({ quote_plus('apikey') : apikey })

    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()

    return etree.fromstring(response_body)

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
    outFile = 'wau.alma.archived.' + time.strftime("%Y%m%d") + '.xml'


    # file streams
    reader = codecs.open(inFile, 'rt', 'utf-8')
    writer = codecs.open(outFile, 'wb', 'utf-8')

    #------------------------------------------------------------------#
    # Read an MMS ID, make a REST Call, Store Both IDs
    #------------------------------------------------------------------#
    print('Gathering Holding Records...')

    # master xml - no longer used
    # marcXML = etree.XML('<collection></collection>')

    writer.write('<collection>\n')

    count = 0
    for line in reader:
        count += 1

        if count % 250 == 0:
            print('  Gathering holding record #' + unicode(count) + '...')
            
        # must strip to avoid any newlines
        ids = line.strip().split('\t')
        holdingID = ids[0].strip()
        mmsID = ids[1].strip()
        
        holdingXML = GetHoldingXML(mmsID, holdingID, apikey)

        # add/replace 001 field with holdingID
        if holdingXML.find('.//controlfield[@tag="001"]') is None:
            cf001 = etree.Element('controlfield', tag='001')
            cf001.text = holdingID
            holdingXML.find('record').insert(1,cf001)            
        else:
            holdingXML.find('.//controlfield[@tag="001"]').text = holdingID

        # replace/add 004 field with mmsID
        if holdingXML.find('.//controlfield[@tag="004"]') is None:
            cf004 = etree.Element('controlfield', tag='004')
            cf004.text = mmsID
            # find the tag that 004 should come before
            i = 0            
            cfields = holdingXML.findall('.//controlfield')
            while i < len(cfields) and int(cfields[i].get('tag')) < 4:
                i = i + 1
            # the ith control field is where you should insert 004 before
            # this is actually <record>'s (i+1)-child as leader is 0th
            holdingXML.find('record').insert(i+1, cf004)                
        else:
            holdingXML.find('.//controlfield[@tag="004"]').text = mmsID

        #marcXML.append( deepcopy( holdingXML.find('record') ) )

        # write as we go
        writer.write('  ' + '  '.join(etree.tostring(holdingXML.find('record'), pretty_print=True).splitlines(True)))

    # close the XML
    writer.write('</collection>\n')
    
    print('Finished. ' + unicode(count) + ' Holding Records(s) gathered.')

if __name__ == '__main__':
    main(sys.argv)
