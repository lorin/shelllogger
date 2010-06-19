#!/usr/bin/env python
"""

This script does a quick XML validation of all the files in ~/.shelllogger.

It returns nothing if all XML files found validate. 

"""
import os
from xml.parsers.expat import ExpatError
import xml.etree.ElementTree as ET 


def main(dirname):
    for fname in os.listdir(dirname):
         if fname.endswith('.xml'):
            try:
                ET.parse(os.path.join(dirname,fname))
                print "%s valid" % fname
            except ExpatError, e:
                print fname, 
                print e
            
if __name__ == '__main__':
    main(dirname=os.path.expanduser('~/.shelllogger'))