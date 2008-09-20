#!/bin/bash -x
mkdir shelllogger
cp ../readme.txt ../shelllogger ../setup.py shelllogger/
rst2html.py shelllogger/readme.txt > shelllogger/readme.html
svnversion > shelllogger/VERSION
zip shelllogger-r`svnversion` shelllogger/*
rm -rf shelllogger/
