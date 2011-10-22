"""
ShellLogger: Unix shell command invocation logger

Usage: shelllogger [-s, --sanitize outfilename] <logfilename>

Upon invocation, it will spawn a new shell (either tcsh or bash, depending upon
SHELL variable).

Directory can be specified by setting (and exporting) the SHELLLOGGERDIR 
environment variable to a directory which will contain the XML logfiles.

If no logfilename is specified, commands are logged to
 .shelllogger/log.<tstamp>.xml 

The script will automatically change the prompt upon startup to one of the following:

bash prompt: PS1='[SL \w]$ '
tcsh prompt: set prompt='[SL %~]$ '

If called with the -s option, it will parse <logfilename> as if it was a raw file and
remove all escape characters, printing to standard out. 

Much of the terminal-related logic comes from example code posted 
to comp.lang.python by Donn Cave. Used here with his permission.
For the original post, see: 
http://groups.google.com/group/comp.lang.python/msg/de40b36c6f0c53cc
"""

import errno
import os
import pty
import re
import select
import time

# Shelllogger-local packages
import log
import tty
import util

BASH_PROMPT = "PS1='[SL \w]$ ' \n"
TCSH_PROMPT = "set prompt='[SL %~]$ ' \n"
SHELL_PROMPTS = {'bash':BASH_PROMPT,'tcsh':TCSH_PROMPT}

# We set this environment variable to indicate we're in shelllogger
ENV_VAR = "ShellLogger"


def get_log_dir():
    """Retrieve the name of the directory that will store the logfiles.
    
    If the SHELLLOGGERDIR environment variable is set, use that.
    Otherwise, default to ~/.shelllogger"""
    env_var = "SHELLLOGGERDIR"
    if os.environ.has_key(env_var):
        return os.environ[env_var]
    else:
        return os.path.expanduser('~/.shelllogger')

def check_recursive():
    """Check if shelllogger has been called recursively"""
    return os.environ.has_key(ENV_VAR)

def default_logfilename(dirname):
    """Returns (logfilename, debugfilename)

    This will also create the log directory if it does not exist"""
    try:
        os.mkdir(dirname)
        print "Creating %s directory for storing logfile" % dirname
    except OSError, e:
        # If it's anything but "File exists",then we're in trouble.
        # We'll just re-raise the exception for now
        if e.errno != errno.EEXIST:
            raise e

    logfilename = os.path.join(dirname,'log.%d.raw' % time.time())
    debugfilename = os.path.join(dirname,'log.%d.debug' % time.time())
    return (logfilename, debugfilename)


def is_child(pid):
    """Returns true if it's the child process after a fork"""
    return pid==0

def run_child_shell():
    """Run the shell in the child process.

    This function will not return"""
    try:
        util.run_shell()
    finally:
        # must not return to caller.
        os._exit(0)

def start_recording(logfilename, debug):

    # Check for recursive call 
    if check_recursive():
        return # this becomes a no-op if we're already in shelllogger

    # Set environment variable to prevent recursive calls
    os.environ[ENV_VAR]='1'
    print "ShellLogger enabled"

    # TODO: Handle the case where debug is true but a logfilename is specified
    if logfilename is None and debug==True:
        raise ValueError, "Don't yet support debug mode with specified logfilename"

    if logfilename is None:
        (logfilename, debugfilename) = default_logfilename(get_log_dir())

    if not debug:
        debugfilename = None

    pid, fd = pty.fork()
    
    if is_child(pid):
        run_child_shell() # This won't return

    # parent process
    input = tty.TTY()
    
    input.raw()

    resizer = tty.ChildWindowResizer(fd)
    resizer.resize_child_window()

    bufsize = 1024

    try:
        logger = log.Logger(logfilename, debugfilename)
       
        if debug:
            print "Warning, shelllogger running in debug mode. All keystrokes will be logged to a plaintext file. Do not type in any passwords during this session!"

        # Set the shell prompt properly
        os.write(fd,SHELL_PROMPTS[util.get_shell()])

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
                        from_shell = ''
                        os.write(1, from_shell)
                        logger.input_from_shell(from_shell)
                        exit = 1

            if exit==1:
                break

        xmlfilename = logger.done()

    except:
        input.restore()
        raise
    input.restore()
    print "ShellLogger data stored in " + xmlfilename
