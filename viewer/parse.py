#!/usr/bin/env python
"""
Parses a logfile

"""
import xml.etree.ElementTree as ET 

import sys
import time
def main(fname):
	print "<html>"
	print "<script type='text/javascript' src='http://shelllogger.googlecode.com/svn/trunk/viewer/toggleIt.js'></script>"
	tree = ET.parse(fname)
	root = tree.getroot()
	usertime = None
	userinput = None
	for child in root.getchildren():
		print "<div>"
		usertime = None
		userinput = None
		for node in child.getchildren():
			if node.tag == "invocation":
				print "<div>"
				timestamp = node.get("time")
				machine = node.get("machine")
				dir = node.get("current-directory")
				usertime = time.ctime(float(timestamp))
				userinput = node.text 
			else:
				print "<tt>"
				print usertime + "[<a href='javascript:toggleIt(" + timestamp + ");'>+</a>]" + userinput
				print "</tt>"
				print "<div id=" + timestamp +" style='display: none'>"
				print "<tt>"
				timestamp = node.get("time")
				if node.text:
					print "<pre>" + node.text + "</pre><br>"
				print time.ctime(float(timestamp)) 
				print "</tt>"
			print "</div>"
		print "</div>"
	print "</html>"

if __name__ == '__main__':
	main(sys.argv[1])
