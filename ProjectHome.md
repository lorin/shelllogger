# About ShellLogger #

ShellLogger captures all user interactions with a shell. It is intended to be used for software engineering researchers who are interested in inferring programmer behavior from data that can be captured automatically during a programming session. It is similar to the Unix 'script' program, but provides additional features such as XML output, distinguishing user input from system output and tracking the user's current directory.

ShellLogger is one tool in  a [suite of tools](http://hpcs.cs.umd.edu/index.php?id=3) originally built by the [Development Time Working Group ](http://hpcs.cs.umd.edu) of the High Productivity Computing Systems project.


There is a FrequentlyAskedQuestions page.

## Install ##

Shelllogger can be installed using pip or easy\_install:

```
$ pip install shelllogger
```

If you want to install it via source, do:

```
$ python setup.py install
```

## Usage ##

To invoke ShellLogger:

```
$ shelllogger
```

This will spawn a new shell, where all of the visible input and output will be captured. The prompt will contain the letters `SL` to indicate that ShellLogger is running and capturing output, for example:

```
[SL ~/svnbuild]$
```

Upon exit, an XML file will be placed in the ~/.shelllogger directory.

## Viewing output ##

You can transform a shelllogger XML file to an HTML for viewing using the `sl-view` program:

```
$ sl-view ~/.shelllogger/log.1318338297.xml > output.html
```
