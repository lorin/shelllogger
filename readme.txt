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
For questions about ShellLogger, please contact Lorin Hochstein: lorinh@gmail.com. 

Prerequisites
=============
ShellLogger requires Python 2.1 or higher. It works with either bash or tcsh. 

Installation
============

1. python setup.py install (you need root access for this)

(Optionally:)

2. Modify the appropriate startup settings file (e.g. .profile, .cshrc) to invoke ShellLogger on startup, by adding it to the *end* of the file, e.g.::

 	python /usr/local/bin/shelllogger

If you want to avoid requiring the user to type "exit" twice to logout (once to exit ShellLogger, and again to exit the parent shell), you can add the following code::

	# in bash
	if [ -z "$ShellLogger" ]
	   then
	   exit
	fi
	
	# in tcsh
	if !($?ShellLogger) then
		exit
	endif
		
Make sure you get this part right. If the "exit" is unconditionally executed in this file, the poor user will log out automatically as soon as they log in!


3. If you want to change the location where ShellLogger puts files (default is ``~/.shelllogger`` directory), define and export a `SHELLLOGGERDIR` environment variable::

	# in bash
	export SHELLLOGGERDIR='/Users/lorin/mydata/shelllogger'

	# in tcsh
	setenv SHELLLOGGERDIR '/Users/lorin/mydata/shelllogger'

Putting it all together, your bash .profile would end with::

	export SHELLLOGGERDIR='/Users/lorin/mydata/shelllogger'
	python /Users/lorin/scripts/shelllogger
	if [ -z "$ShellLogger" ]
	   then
	   exit
	fi

Your tcsh .cshrc would then end with::

	setenv SHELLLOGGERDIR '/Users/lorin/mydata/shelllogger'
	python /Users/lorin/scripts/shelllogger
	if !($?ShellLogger) then
		exit
	endif


Using ShellLogger
=================
Usage::

  [~]$ shelllogger <logfilename>

ShellLogger will begin logging until you exit the shell. Upon exit, a
log of the data named `<logfilename>` will be generated in the directory where
ShellLogger was invoked. If no logfile is specified, it will default to
``~/.shelllogger/log.<tstamp>.xml`` where `<tstamp>` is the UTC timestamp when
the shelllogger session was started. 

Program output
==============
The output of ShellLogger looks like the following::

	<cli-logger>
	
	<cli-logger-entry>
	<invocation time="1185080805.408457"
	current-directory="/Users/lorinh/shelllogger"
	machine="Bender.local">
	pwd
	</invocation>
	<result time="1185080805.408832"><![CDATA[
	/Users/lorinh/shelllogger
	]]></result>
	</cli-logger-entry>
	
	<cli-logger-entry>
	<invocation time="1185080806.856568"
	current-directory="/Users/lorinh/shelllogger"
	machine="Bender.local">
	ls
	</invocation>
	<result time="1185080806.862642"><![CDATA[
	shelllogger      package     readme.html readme.txt
	]]></result>
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
	<result time="1185080812.334055"><![CDATA[
	This directory contains the script for packaging up ShellLogger for distribution.
	]]></result>
	</cli-logger-entry>
	
	<cli-logger-entry>
	<invocation time="1185080813.616734"
	current-directory="/Users/lorinh/shelllogger/package"
	machine="Bender.local">
	exit
	</invocation>
	<result time="1185080813.617144"><![CDATA[
	exit
	]]></result>
	</cli-logger-entry>
	</cli-logger>


Specifying programs where output should not be captured
=======================================================
Most likely, you will not want to capture the output of terminal-based programs, such as Emacs or vi. If you plan to use such a program, and don't want its output captured, specify the program in the TERMINAL_APPS variable defined in `shelllogger`.

Known bugs
==========

It has only been tested on a small number of systems, and terminal behavior varies widely, so certain things may not work on certain terminals. In particular, detecting backspace and shell termination are known to not work properly on some platforms right now.

Does not handle things properly if you move the cursor around using the arrows
keys or Control-A, Control-K. (It will handle backspace, though).



