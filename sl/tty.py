import fcntl
import signal
import struct
import termios


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
