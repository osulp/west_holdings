# WEST Holdings Scripts (aka Getting Holdings Records from Alma #

For our commitment to services like WEST, we have to provide holding records. Unfortunately, there is no direct way to export holding records from Alma. Using ideas from [Bill Kelm's approach](https://github.com/hatfieldlibrary/alma-holdings-records), this repository contains a series of scripts for extracting holding records via the Alma REST APIs.

## Usage ##
Kelm's approach uses an Analytic to get the MMS and Holding IDs for the desired records. This approach instead starts with an Alma set.

### Generate and Export a Set ###
1. Create a set in Alma of the desired items.
2. Export said set using the *Export Bibliographic Records* job to generate a MARC21 file (holdings information does not need to be added).

### Extraction and API Calls ###
To get the holding records, both an MMS ID and a Holding ID are needed for the [Retrieve Holdings Record](https://developers.exlibrisgroup.com/alma/apis/bibs/) web service. To get these two IDs, the following is performed:

1. Extract the MMS ID from the '001' fields in the exported MARC data
2. Use the MMS ID and call the [Retrieve Holdings List](https://developers.exlibrisgroup.com/alma/apis/bibs/) web service and extract the Holding IDs from the returned XML
3. Use the two IDs to get the holdings record via the *Retrieve Holdings Record* web service. 
4. Convert the returned XML data back into MARC21 (while skipping over records lacking a 583 field).

Each of the above steps corresponds to the scripts: *west1_...*, *west2_...*, *west3_...*, and *west4...*. Although they could be combined into one script, the distinct sequence of steps is more amenable to working with a large number of items. In our case, 4000+ items makes steps 2 and 3 take nearly an hour each since each item represents one REST request per step.

## Additional Notes ##
* Each script contains help information (run the script with no arguments) to get particulars).
* Scripts *west2_...* and *west3_...* require an APIKEY (as an argument) in order to access the web services.
* Script *west1_...* requires the PyMARC library.
* Scripts *west2_...* and *west3_...* require the lxml library.
* Due to the slowness of the REST requests, both scripts *west2_...* and *west3_...* are prime candidates for parallelism. 
* Script *west3_...* returns the holding records in MARCXML format. *west4...* converts the data into MARC21 binary.
* *west4_...* also filters out records that lack a 583 field as such records are guaranteed to not be part of the WEST commitment.
* The provided code is streamlined for WEST. As such, script *west3_...* additionally places the Holding ID in the '001' field and the MMS ID in the '004' field.

##License##

This code is released under the OpenBSD license:

Copyright (c) 2015 Katherine Deibel

Permission to use, copy, modify, and distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.