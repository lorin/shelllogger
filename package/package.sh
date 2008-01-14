#!/bin/bash -x
cp ../readme.txt ../cli.py .
rst2html.py readme.txt > readme.html
svnversion > VERSION
zip shelllogger-r`svnversion` cli.py readme.txt readme.html VERSION
rm readme.txt readme.html cli.py
