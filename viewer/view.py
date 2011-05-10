#!/usr/bin/env python
"""
Parses a logfile

"""
import xml.etree.ElementTree as ET 

import re
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

def format_time(timestamp):
    """Takes a timestamp float and produces the time string"""
    fmt = "%m/%d/%Y %H:%M:%S"
    return time.strftime(fmt, time.localtime(timestamp))

def remove_multiline_escapes(s):
    """Takes an input that has backslashes to do multilines and removes them"""
    return s.replace('\\\n> ', '')
    
def clean_first_entry(s):
    """For the first entry, it removes some text about setting the prompt
    that always ends up in the shell"""
    regexp = re.compile(r'PS1.*\]\$ ', flags=re.DOTALL)
    return regexp.sub('', s)
    
def start_time(tree):
    """Retrieve a timestamp with the start time of the log
    
    <cli-logger-entry>
        <invocation time="1305039088.575128"
            current-directory="/Users/lorin/dev"><![CDATA[PS1='[SL \w]$ '
                [lorin@bender dev]$ PS1='[SL \w]$ '
                [SL ~/dev]$ ls]]>
        </invocation>
        <result time="1305039088.578396"><![CDATA[]]></result>
    </cli-logger-entry>

    """
    root = tree.getroot()
    return root[0][0].attrib['time']


def main(fname):
	print "<html>"
	print "<head>"
	print "<script type='text/javascript'>"
	print toggleIt
	print "</script>"
	print "</head>"
	print "<body>"
	print "<h1>ShellLogger transcript</h1>"
	tree = ET.parse(fname)
	print "Started: " +  format_time(start_time(tree))
	
	root = tree.getroot()
	usertime = None
	userinput = None
	for child in root.getchildren():
		print "<div>"
		usertime = None
		userinput = None
		first = True
		for node in child.getchildren():
			if node.tag == "invocation":
				print "<div>"
				timestamp = node.get("time")
				machine = node.get("machine")
				dir = node.get("current-directory")
				usertime = format_time(float(timestamp))
				userinput = remove_multiline_escapes(node.text )
				if first:
				    userinput = clean_first_entry(userinput)
				    first = False
			else:
				print "<tt>"
				print usertime + "[<a href='javascript:toggleIt(" + timestamp + ");'>+</a>]" + userinput
				print "</tt>"
				print "<div id=" + timestamp +" style='display: none'>"
				print "<tt>"
				timestamp = node.get("time")
				if node.text:
					print "<pre>" + node.text + "</pre><br>"
				print format_time(float(timestamp)) 
				print "</tt>"
			print "</div>"
		print "</div>"
	print "</body>"
	print "</html>"

if __name__ == '__main__':
	main(sys.argv[1])

