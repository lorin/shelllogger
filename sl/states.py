"""
State machine states

"""

import codecs
import os
import re
import time

import util

# regex for matching the prompt
# this is used to identify the data directory
re_prompt = re.compile(r'(.*)^\[SL (.*)\]\$ $', re.MULTILINE | re.DOTALL | re.IGNORECASE)
mac_prompt = re.compile(re.compile(r'(?:.*)\[SL (.*)\](.*)(\$)?',re.MULTILINE | re.DOTALL | re.IGNORECASE))
linux_prompt = re.compile(r'(?:.*)\[SL (.*)\]\$',re.MULTILINE | re.DOTALL | re.IGNORECASE)

isFirst = True

# These are applications that use the terminal in such a way that
# it is better to not capture their output
TERMINAL_APPS = ['vi','vim','emacs','pico','nano','joe']



class BeginState:
    def __init__(self,logger):
        self.logger = logger
        self.saw_shell_input = False

    def input_from_shell(self,buf):
        # If it's the prompt, then it's just the very first shell
        m = re_prompt.match(buf) 
        if m is not None:
            self.logger.cwd = os.path.expanduser(m.group(2))
            return
        # If the user just hit enter, we don't log it
        if util.is_enter(buf):
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
        if(buf.startswith('\x0D') or buf.startswith('\r')):
            self.logger.isLinux = True
            self.seen_cr = True
            self.program_invoked = self.logger.buffer.split()[0]
            self.logger.write('''<cli-logger-entry>
<invocation time="%f"
current-directory="%s"><![CDATA[''' % (time.time(),self.logger.cwd))
            self.logger.write(self.logger.buffer)
            self.logger.write(']]></invocation>\n')
            self.logger.buffer = buf;    
               
        elif util.is_enter(buf) and len(self.logger.buffer)>0 and ( self.logger.buffer[-1]!='\\' or 'logout' in buf ):
            self.seen_cr = True
            self.program_invoked = self.logger.buffer.split()[0]
            self.logger.write('''<cli-logger-entry>
<invocation time="%f"
current-directory="%s"><![CDATA[''' % (time.time(),self.logger.cwd))
            self.logger.write(self.logger.buffer)
            self.logger.write(']]></invocation>\n')
        else:
            self.logger.buffer += buf
    
    def input_from_user(self,buf):
        # Don't need to take any action
        global isFirst
        if(isFirst):
            isFirst = False
            self.logger.buffer = ''
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
            try:
                self.logger.write('<result time="%f"></result>\n</cli-logger-entry>\n\n' % time.time())
                self.logger.cwd = os.path.expanduser(m.group(2))
                self.seen_prompt = True
                return
            except:
               m = mac_prompt.match(buf)
               if m is not None:
                   self.logger.cwd = os.path.expanduser(m.group(1))
                   self.logger.write('</result>\n</cli-logger-entry>\n\n' % time.time())
                   self.seen_prompt = True
                   return
        else:
            self.seen_shell_input = True
            self.logger.write('<result time="%f"><![CDATA[\n' % time.time())
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write(buf)
        
    def input_from_user(self,buf):
         if self.logger.isLinux:
            m = linux_prompt.match(self.logger.buffer.strip())
            if m is not None:
                self.logger.cwd = os.path.expanduser(m.group(1))
                self.logger.write('<result time="%f"></result>\n</cli-logger-entry>\n\n' % time.time())
                self.seen_prompt = True

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
    """
    In this state, we do not want to capture any output. The typical case
    is when the user has invoked an interactive program such as a 
    text editor.
    """


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
        mac = mac_prompt.match(buf)
        linux = linux_prompt.match(buf)
        if m is not None:
            # It's the prompt!
            self.saw_prompt = True
            try: 
               self.logger.cwd = os.path.expanduser(m.group(2))
               self.write_output_to_log(m.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
            except:
               m = mac_prompt.match(buf)
               if m is not None:
                   self.logger.cwd = os.path.expanduser(m.group(1))
                   self.logger.write('</result>\n</cli-logger-entry>\n\n' % time.time())
                   self.seen_prompt = True
        elif mac is not None:
               self.logger.cwd = os.path.expanduser(mac.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
        elif linux is not None:
               self.logger.cwd = os.path.expanduser(linux.group(1))
               self.logger.write("]]></result>\n</cli-logger-entry>\n\n")
        else:
            self.write_output_to_log(buf)

    def write_output_to_log(self,buf):
        self.logger.write(buf)

    def input_from_user(self,buf):
        if(self.logger.isLinux):
            self.logger.isLinux = False         
            self.saw_prompt = True

    def next_state(self):
        if self.saw_prompt:
            return BeginState(self.logger)
        else:
            return self

class ShellOutputNoOutputState(ShellOutputState):
    """

    TODO: This is a dead state, which is clearly incorrect.
    """
    def write_output_to_log(self,buf):
        pass

def sanitize_file(infilename, outfilename):
    """Strip all control characters and non-UTF-8 characters from a file.
    
    Prints the output to standard out"""
    fout = codecs.open(outfilename, encoding="utf-8", mode="w")
    for line in codecs.open(infilename, encoding="utf-8"):
        fout.write(util.sanitize(line))
