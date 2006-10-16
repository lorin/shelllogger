#!/usr/bin/env python
#
# ShellLogger: Unix shell command invocation logger
#
# Usage: cli.py <logfilename>
#
#
# Upon invocation, it will spawn a new shell (either tcsh or bash, depending upon
# SHELL variable).
#
# If no logfilename is specified, commands are logged to
#  .shelllogger/log.<tstamp>.xml 
#
# The script currently depends upon the following prompts being set by the user
# in .bashrc and .cshrc, respectively
#
# bash prompt: PS1='[\w]$ '
# tcsh prompt: set prompt='[%~]$ '
#
# Much code borrowed from
# http://groups.google.com/group/comp.lang.python/msg/de40b36c6f0c53cc
#
# 

import fcntl
import sys
import os
import pty
import re
import select
import signal
import socket
import struct
import termios
import time
import errno


# Fix for older versions of Python
try:
    True
except NameError:
    True,False = 1,0

# These are applications that use the terminal in such a way that
# it is better to not capture their output
TERMINAL_APPS = ['vi','vim','emacs','pico','nano','joe']

   

class TTY:
    def __init__(self):
        self.iflag, self.oflag, self.cflag, self.lflag, \
            self.ispeed, self.ospeed, self.cc = termios.tcgetattr(0)
    def raw(self):
        # ISIG - passes Ctl-C, Ctl-Z, etc. to the child rather than generating signals
        raw_lflag = self.lflag & ~(termios.ICANON|termios.ECHO|termios.ISIG)
        raw_iflag = self.iflag & ~(termios.ICRNL|termios.IXON)
        raw_cc = self.cc[:]
        raw_cc[termios.VMIN] = 1
        raw_cc[termios.VTIME] = 0
        termios.tcsetattr(0, termios.TCSANOW, [raw_iflag, self.oflag,
                                               self.cflag, raw_lflag,
                                               self.ispeed, self.ospeed,
                                               raw_cc])
    def restore(self):
        termios.tcsetattr(0, termios.TCSANOW, [self.iflag, self.oflag,
                                               self.cflag, self.lflag,
                                               self.ispeed, self.ospeed,
                                               self.cc])

class ChildWindowResizer:
    """Informs the child process that the window has been resized."""

    def __init__(self,child_fd):
        self.child_fd = child_fd
        signal.signal(signal.SIGWINCH,self.signal_handler)

    def signal_handler(self,sig,data):
        """Signal handler that gets installed"""
        self.resize_child_window()

    def resize_child_window(self):
        """Tells the child process to resize its window"""
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(0,termios.TIOCGWINSZ,s)
        fcntl.ioctl(self.child_fd,termios.TIOCSWINSZ,x)


def run_shell():
    """Launch the appropriate shell.

    It will be either bash or tcsh depending on what the user is currently running.
    It checks the SHELL variable to figure it out.
    """
    shell = os.path.basename(os.environ['SHELL'])
    if shell not in ['bash','tcsh']:
        raise ValueError, "Unsupported shell (only works with bash and tcsh)"
    os.execvp(shell,(shell,))
    

def main(logfilename=None):
    # Check for recursive call
    env_var = 'ShellLogger'
    if os.environ.has_key(env_var):
        # Recursive call, just exit
        return

    os.environ[env_var]='1'
    print "ShellLogger enabled"

    if logfilename is None:
        # Default: .shelllogger/log.<tstamp>.lxml

        # Try to create the .shelllogger directory
        dirname = os.path.expanduser('~/.shelllogger')
        try:
            os.mkdir(dirname)
            print "Creating ~/.shelllogger directory for storing logfile"
        except OSError, e:
            # If it's anything but "File exists",then we're in trouble.
            # We'll just re-raise the exception for now
            if e.errno != errno.EEXIST:
                raise e

        logfilename = os.path.join(dirname,'log.%d.xml' % time.time())

    pid, fd = pty.fork()
    
    # Python won't return -1, rather will raise exception.
    if pid == 0:    # child process
        try:
            run_shell()
        except:
            # must not return to caller.
            os._exit(0)

    # parent process
    input = TTY()
    
    input.raw()

    resizer = ChildWindowResizer(fd)
    resizer.resize_child_window()

    bufsize = 1024

    try:
        logger = Logger(logfilename)

        while True:
            delay = 1           
            exit = 0
            try:
                r, w, e = select.select([0, fd], [], [], delay)
            except select.error, se:
                # When the user resizes the window, it will generate a signal
                # that will be handled, which will cause select to be
                # interrupted. 
                if se.args[0]==errno.EINTR:
                    continue
                else:
                    raise
	    for File in r:
		if File == 0:
		    first_user_input = 1
		    from_user = os.read(0, bufsize)
		    os.write(fd, from_user)
		    logger.input_from_user(from_user)

		elif File == fd:
		    try:
			from_shell = os.read(fd, bufsize)
			os.write(1, from_shell)
			logger.input_from_shell(from_shell)
			if from_shell=='':
			    exit = 1
		    except OSError:
			# On Linux, os.read throws an OSError
			# when data is done
			exit = 1

            if exit==1:
                break

        logger.done()

    except:
            input.restore()
            raise
    input.restore()
    print "ShellLogger data stored in " + logfilename

class Logger:
    def __init__(self,logfilename):
        self.logfile = open(logfilename,'w')
        self.logfile.write("<cli-logger>\n\n")
        self.buffer = ''
        self.cwd = os.getcwd()
        self.state = BeginState(self)
        # Regex filter. This is a nightmare because I can't
        # use raw strings, because I need to use escape sequences.
        self.filter = re.compile('''(
        \x07              |   # bell
        \x1b\\[H\x1b\\[2J |   # clear screen
        \x1b\\[m          |   # color
        \x1b\\[\\d\\dm    |   # color
        \x1b\\[\\d\\d;\\d\\dm # color
        )''',re.X)

        # Characters emitted when the user hits backspace.
        # This will probably vary from terminal to terminal, and
        # this list should grow is new terminals are encountered.
	self.BACKSPACES = ['\x08\x1b[K',
			   '\x08 \x08']

        

    def done(self):
        self.logfile.write("</result>\n</cli-logger-entry>\n</cli-logger>\n")
        self.logfile.close()

    def input_from_shell(self,buf):
        self.state.input_from_shell(buf)
        self.state = self.state.next_state()

    def input_from_user(self,buf):
        self.state.input_from_user(buf)
        self.state = self.state.next_state()

    def write(self,buf):
        self.logfile.write(buf)

    def write_filtered(self,buf):
        # Write to file, filtering out control characters

        # First, handle the backspaces.
        for BACKSPACE in self.BACKSPACES:
            try:
                while True:
                    ind = buf.index(BACKSPACE) 
                    buf = ''.join((buf[0:ind-1],buf[ind+len(BACKSPACE):]))
            except:
                pass
        
        self.logfile.write(self.filter.sub('',buf))


# regex for matching the prompt
# this is used to identify the data directory
re_prompt = re.compile(r'^\[(.*)\]\$ $')

def is_enter(buf):
    # Check if buffer consists entirely of \n or \r
    for c in buf:
        if c!='\n' and c!='\r':
            return False
    return True


class BeginState:
    def __init__(self,logger):
        self.logger = logger
        self.saw_shell_input = False

    def input_from_shell(self,buf):
        # If it's the prompt, then it's just the very first shell
        m = re_prompt.match(buf) 
        if m is not None:
            self.logger.cwd = os.path.expanduser(m.group(1))
            return

        # If the user just hit enter, we don't log it
        if is_enter(buf):
            return
        self.saw_shell_input = True
        # Stick the data in a buffer
        self.logger.buffer = buf

    def input_from_user(self,buf):
        # We don't actually care about input from the user,
        # we just use shell echos
        pass

    def next_state(self):
        if self.saw_shell_input:
            return UserTypingState(self.logger)
        else:
            return self

class UserTypingState:
    def __init__(self,logger):
        self.logger = logger
        self.seen_cr = False
        self.program_invoked = None

    def input_from_shell(self,buf):
        if is_enter(buf):
            self.seen_cr = True
            self.program_invoked = self.logger.buffer.split()[0]
            self.logger.write('''<cli-logger-entry>
<invocation time="%f"
current-directory="%s"
machine="%s">\n''' % (time.time(),self.logger.cwd,socket.gethostname()))
            self.logger.write_filtered(self.logger.buffer)
            self.logger.write('\n')
            self.logger.write('</invocation>\n')
        else:
            self.logger.buffer += buf
    
    def input_from_user(self,buf):
        # Don't need to take any action
        pass

    def next_state(self):
        if self.seen_cr:
            if self.program_invoked in TERMINAL_APPS:
                return WaitingForShellNoOutputState(self.logger)
            else:
                return WaitingForShellState(self.logger)

                
        else:
            return self

class WaitingForShellState:
    def __init__(self,logger):
        self.logger = logger
        self.seen_shell_input = False
        self.seen_prompt = False

    def input_from_shell(self,buf):
        # Check for the case of no input, just a shell prompt
        m = re_prompt.match(buf)
        if m is not None:
            # Empty result
            self.logger.write('<result time="%f"></result>\n</cli-logger-entry>\n\n' % time.time())
            self.logger.cwd = os.path.expanduser(m.group(1))
            self.seen_prompt = True
            return
        else:
            self.seen_shell_input = True
            self.logger.write('<result time="%f">\n' % time.time())
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write_filtered(buf)
        
    def input_from_user(self,buf):
        pass

    def shell_output_state(self,logger):
        return ShellOutputState(logger)

    def next_state(self):
        if self.seen_prompt:
            return BeginState(self.logger)
        elif self.seen_shell_input:
            return self.shell_output_state(self.logger)
        else:
            return self


class WaitingForShellNoOutputState(WaitingForShellState):
    def write_output_to_log(self,buf):
        pass

    def shell_output_state(self,logger):
        return ShellOutputNoOutputState(logger)
    

        
class ShellOutputState:
    def __init__(self,logger):
        self.logger = logger
        self.saw_prompt = False


    def input_from_shell(self,buf):
        # Check if it's the prompt
        m = re_prompt.match(buf)
        if m is not None:
            # It's the prompt!
            self.saw_prompt = True
            self.logger.cwd = os.path.expanduser(m.group(1))
            self.logger.write("</result>\n</cli-logger-entry>\n\n")
        else:
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write_filtered(buf)

    def input_from_user(self,buf):
        pass

    def next_state(self):
        if self.saw_prompt:
            return BeginState(self.logger)
        else:
            return self

class ShellOutputNoOutputState(ShellOutputState):
    def write_output_to_log(self,buf):
        pass
    
        

if __name__ == '__main__':
    if len(sys.argv)==1:
        main()
    else:
        main(sys.argv[1]) 
