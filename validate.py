#!/usr/bin/env python
"""

This script does a quick XML validation of all the files in ~/.shelllogger.

It returns nothing if all XML files found validate. 

"""
import os
from optparse import OptionParser
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET 


def main(dirname):
    print "Directory:", dirname
    for fname in os.listdir(dirname):
         if fname.endswith('.xml'):
            try:
                ET.parse(os.path.join(dirname,fname))
                print "%s valid" % fname
            except ExpatError, e:
                print fname, 
                print e
            
if __name__ == '__main__':
    usage = "usage: %prog [DIR]"
    description = "Chceks that files with .xml extension in DIR are valid XML"
    epilog = "If no directory is specified, will use DIR=~/.shelllogger"
    parser = OptionParser(usage=usage, description=description, epilog=epilog)
    (options, args) = parser.parse_args()
    if len(args)>1:
        parser.error("incorrect number of arguments")
    
    main(dirname=os.path.expanduser('~/.shelllogger'))