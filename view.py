#!/usr/bin/env python
"""
Parses a logfile

"""
import xml.etree.ElementTree as ET 

import re
import sys
import time

css = '''


td 
{ 
    vertical-align: top; 
    font-family:monospace;
}

h1 { font-size: 1.2em; margin: .67em 0 }

div.entry
{
    font-family:monospace;
}

span.time
{
    display:none;
}


div.output
{
    border-style: solid;
    border-width: 1px;
    padding-left:5px;
    padding-right:5px;

}

'''

toggleIt = '''
// Created by Jeremy Archuleta
// Department of Computer Science at Virginia Tech
// Email: jsarch@vt.edu
function toggleIt( whichLayer )
{
  var elem, vis, link;
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

  vis.display = (vis.display == '' || vis.display=='block') ? 'none' : 'block';

  link = document.getElementById('expand-' + whichLayer);
  link.innerHTML = (link.innerHTML=='+' ? '-' : '+');

}

'''

def format_time(timestamp):
    """Takes a timestamp float and produces the time string"""
    fmt = "%m/%d/%Y %H:%M:%S"
    return time.strftime(fmt, time.localtime(timestamp))

def remove_multiline_escapes(s):
    """Takes an input that has backslashes to do multilines and removes them"""
    return s.replace('\\\n> ', '')
    
def clean_multiline_escapes(s):
    """Takes an input that has backslashes to do multilines and adds brs"""
    return s.replace('\\\n> ', '\\<br>\n> ')

    
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
    return float(root[0][0].attrib['time'])


def prompt(dirname, homedir):
    """Calculate a prompt given the current directory and home directory"""
    return "[%s]$ " % dirname.replace(homedir,'~')

def main(fname):
    print "<html>"
    print "<head>"
    print "<style type='text/css'>"
    print css
    print "</style>"
    print "<script type='text/javascript'>"
    print toggleIt
    print "</script>"
    print "</head>"
    print "<body>"
    tree = ET.parse(fname)
    print "<h1>Log date: %s</h1>"  % format_time(start_time(tree))
    
    print "<p>Click on the <b>+</b> links to view the output for the given shell command.</p>"

    root = tree.getroot()
    usertime = None
    userinput = None
    dir = None
    homedir = None
    first = True
    for child in root.getchildren():
        usertime = None
        userinput = None
        # Invocation
        print "<table>"
        for node in child.getchildren():
            print "<div class='entry'>"
            print "<tr>"
            if node.tag == "invocation":
                timestamp = node.get("time")
                machine = node.get("machine")
                dir = node.get("current-directory")
                usertime = format_time(float(timestamp))
                userinput = clean_multiline_escapes(node.text)
                if first:
                    homedir = dir
                    userinput = clean_first_entry(userinput)
                    first = False
            else:
                # Show the user time
                print "\t<span class='time'>"
                print usertime
                print "\t</span>"
                print "<td>"
                print "<a style='text-decoration: none;' href='javascript:toggleIt(" + timestamp + ");'><span class='expand' id='expand-%s'>+</span></a>" % timestamp 
                print "</td>"
                print "<td>"
                # Show the user input
                print "\t<span class='input'>"
                print prompt(dir, homedir) + userinput
                print "</span>"
                print "\t<div class='output' id=" + timestamp +" style='display: none'>"
                timestamp = node.get("time")
                if node.text:
                    print "<pre>" + node.text + "</pre>"
                #print format_time(float(timestamp)) 
                print "\t</div>" # class:output
                print "</td>"
            print "</tr>"
            print "</div>" # class:entry
    print "</table>"
    print "<hr />"
    print "<i>Generated by <a href='http://shelllogger.googlecode.com'>ShellLogger</a>.</i>"
    print "</body>"
    print "</html>"

if __name__ == '__main__':
    main(sys.argv[1])

