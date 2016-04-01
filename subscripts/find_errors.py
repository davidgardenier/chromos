# Quick & dirt script to find where files have produced errors in the pipeline
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

# Could be adapted to look for nan values in the database, and use those to
# trace back why values haven't been calculated

def find_errors():
    '''
    Function to find errors in all log files, and to make a summary of them in
    a file.
    '''

    purpose = 'Finding errors'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    errorlog = paths.logs + 'errors.log'

    alllogs = glob.glob(paths.logs + '*.log')
    logs = [f for f in alllogs if f is not errorlog]

    for f in logs:
        with open(f, 'r') as log:
            for line in log:
                if 'ERROR' in line:
                    print line
                    # TODO print lines above and below to see cause of error
                    # TODO print file name, so you know what is going 
