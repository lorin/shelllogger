===============================================
ShellLogger: Logs shell commands and timestamps
===============================================

Introduction
============
ShellLogger captures all user interactions with a shell. It is intended to be used for software engineering researchers who are interested in inferring programmer behavior from data that can be captured automatically during a programming session. It is similar to the Unix "script" program, with the following additional features:

- Automatically distinguishes between the text that was inputted by the user and the data that was output by the shell and other programs
- Records timestamps of when data was inputted by user and when the system responds
- Tracks directory information
- Actually deletes characters when user hits backspace, rather than capturing the backspace character.
- Can disable capturing output when certain terminal-based programs are invoked (e.g. Emacs, vi)
- Records the data in an XML file to facilitate parsing by other applications


Contact
=======
For questions about ShellLogger, please contact Lorin Hochstein: lorin@cse.unl.edu. 

Prerequisites
=============
ShellLogger requires Python 2.1 or higher. It works with either bash or tcsh. 

Installation
============

1. Copy `cli.py` to an accessible location (that's it!)

(Optionally:)

2. Modify the appropriate startup settings file (e.g. .profile, .cshrc) to invoke ShellLogger on startup, e.g.::

 	python /path/to/cli.py

3. If you want to change the location where ShellLogger puts files (default is ``~/.shelllogger`` directory), define and export a `SHELLLOGGERDIR` environment variable. 
For example, in a bash .profile file::

	export SHELLLOGGERDIR='/tmp'

In a tcsh .cshrc file::

	setenv SHELLLOGGERDIR '/tmp'


Using ShellLogger
=================
Usage::

  [~]$ cli.py <logfilename>

ShellLogger will begin logging until you exit the shell. Upon exit, a
log of the data named `<logfilename>` will be generated in the directory where
ShellLogger was invoked. If no logfile is specified, it will default to
``~/.shelllogger/log.<tstamp>.xml`` where `<tstamp>` is the UTC timestamp when
the shelllogger session was started. 

Program output
==============
The output of ShellLogger looks like the following:

<cli-logger>

<cli-logger-entry>
<invocation time="1185080805.408457"
current-directory="/Users/lorinh/shelllogger"
machine="Bender.local">
pwd
</invocation>
<result time="1185080805.408832">
/Users/lorinh/shelllogger
</result>
</cli-logger-entry>

<cli-logger-entry>
<invocation time="1185080806.856568"
current-directory="/Users/lorinh/shelllogger"
machine="Bender.local">
ls
</invocation>
<result time="1185080806.862642">
cli.py      package     readme.html readme.txt
</result>
</cli-logger-entry>

<cli-logger-entry>
<invocation time="1185080808.744830"
current-directory="/Users/lorinh/shelllogger"
machine="Bender.local">
cd package
</invocation>
<result time="1185080808.745676"></result>
</cli-logger-entry>

<cli-logger-entry>
<invocation time="1185080812.328699"
current-directory="/Users/lorinh/shelllogger/package"
machine="Bender.local">
cat README
</invocation>
<result time="1185080812.334055">
This directory contains the script for packaging up ShellLogger for distribution.
</result>
</cli-logger-entry>

<cli-logger-entry>
<invocation time="1185080813.616734"
current-directory="/Users/lorinh/shelllogger/package"
machine="Bender.local">
exit
</invocation>
<result time="1185080813.617144">
exit
</result>
</cli-logger-entry>
</cli-logger>


Specifying programs where output should not be captured
=======================================================
Most likely, you will not want to capture the output of terminal-based programs, such as Emacs or vi. If you plan to use such a program, and don't want its output captured, specify the program in the TERMINAL_APPS variable defined in `cli.py`.

Known bugs
==========

It has only been tested on a small number of systems, and terminal behavior varies widely, so certain things may not work on certain terminals. In particular, detecting backspace and shell termination are known to not work properly on some platforms right now.

Does not handle things properly if you move the cursor around using the arrows
keys or Control-A, Control-K. (It will handle backspace, though).



