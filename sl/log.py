import codecs
import os
import socket

import util
from states import BeginState


class Logger:
    """This class is responsible for writing the XML log file"""
    def __init__(self,logfilename, debugfilename):
        self.logfilename = logfilename
        self.logfile = open(logfilename,'w')
        self.logfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.logfile.write('<cli-logger machine="%s">\n\n' % socket.gethostname())
        self.buffer = ''
        self.cwd = os.getcwd()
        self.state = BeginState(self)
        self.debugfilename = debugfilename
        self.isLinux = False
        if self.debugfilename is not None:
            self.debugfile = codecs.open(debugfilename, encoding="utf-8", mode="w")
            self.debugfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            self.debugfile.write("<cli-debug>\n")
        else:
            self.debugfile = None

    def done(self):
        """Call when session is complete.
        
        Returns the name of the XML file
        
        """
        self.logfile.write("]]></result>\n</cli-logger-entry>\n</cli-logger>\n")
        self.logfile.close()
        if self.debugfilename is not None:
            self.debugfile.write("</cli-debug>")
        return self.raw_to_xml()
        
    def raw_to_xml(self):
        """Convert the .raw file, with illegal characters and escape keys, to a proper XML version.
        
        Returns the name of the XML file
        """
        xmlfilename = self.logfilename.replace('.raw','.xml')
        fout = codecs.open(xmlfilename, encoding="utf-8", mode="w")
        for line in codecs.open(self.logfilename,encoding="utf-8"):
            fout.write(util.sanitize(line))
            
        fout.close()
        return xmlfilename
        
    def input_from_shell(self,buf):
        if self.debugfile:
            self.debug_log(buf,True)
        self.state.input_from_shell(buf)
        self.state = self.state.next_state()

    def input_from_user(self,buf):
        if self.debugfile:
            self.debug_log(buf,False)
        self.state.input_from_user(buf)
        self.state = self.state.next_state()

    def write(self,buf):
        self.logfile.write(buf)
        
    def debug_log(self, buf, shell):
        """Record to the debug log"""

        # Handle Shell output
        if shell == True:
            self.debugfile.write("<shell><![CDATA[%s]]></shell>\n" % buf)

        # Handle User Input
        else:
            self.debugfile.write("<user><![CDATA[%s]]></user>\n" % buf)
