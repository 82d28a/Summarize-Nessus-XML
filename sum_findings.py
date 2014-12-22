#!/usr/bin/python

import xml.etree.ElementTree as ET
import csv
import sys
import codecs
import cStringIO


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def write_results(results_table, out_filename):
    try:
        with open(out_filename, 'wb') as csvfile:
            sum_write = UnicodeWriter(csvfile)
            for row in results_table:
                sum_write.writerow(row)
    except IOError as e:
        print "Error writing csv file. Check for permissions and/or path."
        exit()


def get_sum_from_xml(filename):
    results_table = [["script_name", "description", "cvss_base_score", "solution"]]

    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except:
        print "Error reading/parsing XML file. Likely XML file is mangled in some way. Check the XML file."
        exit()

    for child in root:
        row = ["", "", "", ""]
        for gchild in child:

            if gchild.tag == "script_name":
                row[0] = gchild.text

            if gchild.tag == "attributes":
                for ggchild in gchild:

                    if ggchild[0].text == "description":
                        row[1] = ggchild[1].text

                    elif ggchild[0].text == "cvss_base_score":
                        row[2] = ggchild[1].text

                    elif ggchild[0].text == "solution":
                        row[3] = ggchild[1].text
        results_table.append(row)

    return results_table

if __name__ == "__main__":
    if len(sys.argv) == 3:
        results = get_sum_from_xml(sys.argv[1])
        write_results(results, sys.argv[2])
    else:
        print "USAGE: python {} source_xml_file destination_csv_file".format(sys.argv[0])
        exit()