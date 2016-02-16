import sys
import paths
import os
from datetime import datetime

class Logger(object):
    def __init__(self, filename):
        self.filename = filename
        self.terminal = sys.stdout
        self.log = open(self.filename, 'w')
        self.log.write(str(datetime.now()) + '\n')

    def write(self, message):
        if paths.terminal_output:
            self.terminal.write(message)
        self.log.write(message)

def output(filename):
    logfile = paths.logs + filename + '.log'
    if not os.path.exists(logfile):
        open(logfile, 'w')
    sys.stdout = Logger(logfile)
