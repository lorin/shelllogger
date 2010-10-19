#!/usr/bin/env python
"""
Parses a logfile

"""
import xml.etree.ElementTree as ET 

import sys
import time

toggleIt = '''
// Created by Jeremy Archuleta
// Department of Computer Science at Virginia Tech
// Email: jsarch@vt.edu
function toggleIt( whichLayer )
{
  var elem, vis;
  if( document.getElementById ) // this is the way the standards work
    elem = document.getElementById( whichLayer );
  else if( document.all ) // this is the way old msie versions work
      elem = document.all[whichLayer];
  else if( document.layers ) // this is the way nn4 works
    elem = document.layers[whichLayer];
  vis = elem.style;
  // if the style.display value is blank we try to figure it out here
  if(vis.display==''&&elem.offsetWidth!=undefined&&elem.offsetHeight!=undefined)
    vis.display = (elem.offsetWidth!=0&&elem.offsetHeight!=0)?'block':'none';
  vis.display = (vis.display==''||vis.display=='block')?'none':'block';
}

//JSARCH
function show( whichLayer )
{
  var elem, vis;
  if( document.getElementById ) // this is the way the standards work
    elem = document.getElementById( whichLayer );
  else if( document.all ) // this is the way old msie versions work
      elem = document.all[whichLayer];
  else if( document.layers ) // this is the way nn4 works
    elem = document.layers[whichLayer];
  vis = elem.style;
  vis.display = 'inline';
}

function hide( whichLayer )
{
  var elem, vis;
  if( document.getElementById ) // this is the way the standards work
    elem = document.getElementById( whichLayer );
  else if( document.all ) // this is the way old msie versions work
      elem = document.all[whichLayer];
  else if( document.layers ) // this is the way nn4 works
    elem = document.layers[whichLayer];
  vis = elem.style;
  vis.display = 'none';
}
//JSARCH
'''

def main(fname):
	print "<html>"
	print "<script type='text/javascript'>"
	print toggleIt
	print"</script>"
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

