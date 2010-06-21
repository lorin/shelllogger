import pexpect
import re
import unittest

class TestShellLogger(unittest.TestCase):
    def test_run_exit(self):
        """
        [lorin@macbook shelllogger]$ ./shelllogger 
        ShellLogger enabled
        PS1='[\w]$ '
        [lorin@macbook shelllogger]$ PS1='[\w]$ '
        [~/shelllogger]$
        ...
        [~/shelllogger]$ exit
        logout
        ShellLogger data stored in /Users/lorin/.shelllogger/log.1277044716.xml        

        """
        
        child = pexpect.spawn('python shelllogger')
        self.assertEqual(child.readline(),"ShellLogger enabled\r\n")
        varcommand = "PS1='[\\w]$ '\r\r\n"
        self.assertEqual(child.readline(), varcommand)
        self.assertTrue(child.readline().endswith(varcommand))
        child.sendline("exit")
        
        # TODO: Check that the XML output is valid
        
    


if __name__ == '__main__':
    unittest.main()
    


