"""
Utility functions
"""

import os
import re

def is_printable(c):
    """
    Returns true if c is a printable character. 
    
    We do this by checking for ord value above 32 (space),
    as well as CR (\r), LF (\n) and tab (\t)
    
    """
    return ord(c)>=32 or c in ['\r','\n', '\t']

def sanitize(buf, 
             backspaces=['\x08\x1b[K', '\x08 \x08'], 
             escape_regex=re.compile(r'\x1b(\[|\]|\(|\))[;?0-9]*[0-9A-Za-z](.*\x07)?')):
    """Filter control characters out of the string buf, given a list of control codes
    that represent backspaces, and a regex of escape sequences.
    
    backspaces are characters emitted when the user hits backspace. 
    This will probably vary from terminal to terminal, and
    this list should grow as new terminals are encountered.
    
    escape_regex is a Regex filter to capture all escape sequences.
    Modified from: http://wiki.tcl.tk/9673
    """
    # Filter out control characters

    # First, handle the backspaces.
    for backspace in backspaces:
        try:
            while True:
                ind = buf.index(backspace) 
                buf = ''.join((buf[0:ind-1],buf[ind+len(backspace):]))
        except:
            pass
            
    strip_escapes = escape_regex.sub('',buf)
    
    # strip non-printable ASCII characters

    clean = ''.join([x for x in strip_escapes if is_printable(x)])
    return clean

def get_shell():
  return os.path.basename(os.environ['SHELL'])

def run_shell():
    """Launch the appropriate shell as a login shell

    It will be either bash or tcsh depending on what the user is currently running.
    It checks the SHELL variable to figure it out.
    """
    shell = get_shell()
    if shell not in ['bash','tcsh']:
        raise ValueError, "Unsupported shell (only works with bash and tcsh)"
    os.execvp(shell,(shell,"-l"))

