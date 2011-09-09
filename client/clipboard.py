import sys
from subprocess import Popen, PIPE


class SubprocessWriter(object):
    '''
    Writes to stdin of an external process.
    '''

    def __init__(self, cmd):
        self.cmd = cmd

    def set(self, text):
        '''
        Writes the text and returns True if the process exited with a return
        code of 0.
        '''

        proc = Popen(self.cmd, shell=True, stdout=PIPE, stdin=PIPE, \
            stderr=PIPE)

        proc.stdin.write(text)
        proc.stdin.close()

        return proc.wait() == 0


class Clipboard(object):
    '''
    Autodetects the current platform and tries to set the clipboard through a
    number of ways.
    '''

    def __init__(self):
        self.backends = []

        if sys.platform.startswith('linux'):
            self.backends = map(SubprocessWriter, ('xsel -pi', 'xclip'))

        if sys.platform == 'darwin':
            self.backends = [SubprocessWriter('pbcopy')]

        if sys.platform == 'win32':
            self.backends = [SubprocessWriter('clip')]

    def set(self, text):
        'Returns True if any of the backends succeeded.'

        return any(backend.set(text) for backend in self.backends)

def copy(text):
    return Clipboard().set(text)
