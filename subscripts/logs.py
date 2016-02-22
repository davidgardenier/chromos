# Program to capture any output normally directed to the terminal and save it
# to a log. In the paths file you can choose to turn off terminal output, upon
# which this program will only log the terminal output without displaying it.
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import sys
import paths
import os
from datetime import datetime

class Logger(object):
    def __init__(self, filename, output):
        self.filename = filename
        self.output = output
        if self.output == 'output':
            self.terminal = sys.stdout
            self.log = open(self.filename, 'w')
            self.log.write(str(datetime.now()) + '\n')
        if self.output == 'error':
            self.terminal = sys.stderr
            self.log = open(self.filename, 'a')
            self.log.write(str(datetime.now()) + '\n')

    def write(self, message):
        if paths.terminal_output:
            self.terminal.write(message)
        self.log.write(message)

def output(filename):
    if not os.path.exists(paths.logs):
        os.makedirs(paths.log)

    logfile = paths.logs + filename + '.log'
    if not os.path.exists(logfile):
        open(logfile, 'w')

    sys.stdout = Logger(logfile, 'output')
    sys.stderr = Logger(logfile, 'error')
