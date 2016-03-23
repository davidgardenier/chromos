import json
import glob
import os
from subprocess import Popen, PIPE, STDOUT

def create_time_filters(verbose=False):
    '''
    Function to run the ftool maketime over all filter files (.xfl.gz files).
    Creates time_filter.gz files. Updates the dictionary with for instance the
    path to each time_filter file.
    '''

    # Print purpose of program
    purpose = 'Creating time filters'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Find all filter files and add to dictionary
    for obsid in d:
        d[obsid]['filter'] = {'paths':[]}
        d[obsid]['filter']['paths'] = glob.glob('./P' + obsid[:5] + '/' + obsid + '/stdprod/*.xfl.gz')

    # Run maketime over each filter file
    for obsid in d:
        for path in d[obsid]['filter']['paths']:

            # Give the output name & put into dictionary
            output = path.split('stdprod')[0] + 'time_filter.gti'
            d[obsid]['filter']['path_list'] = output

            # Ensure maketime doesn't complain about previous versions of the
            # output already being created
            try:
                os.system('rm ' + output)
            except OSError:
                continue

            # Execute maketime
            p = Popen(['maketime'], stdout=PIPE, stdin=PIPE,
                      stderr=STDOUT, bufsize=1)

            if verbose is True:
                print('----------\n Running maketime on ' + obsid)

            # Give the required input
            # -----------------------
            # Name of FITS file
            p.stdin.write(path + ' \n')
            # Name of output FITS file
            p.stdin.write(output + ' \n')
            # Selection expression.
            p.stdin.write('elv.gt.10.and.' +
                          'offset.lt.0.02.and.' +
                          'num_pcu_on.gt.1.and.' +
                          '(time_since_saa.gt.10.or.' +
                          'time_since_saa.lt.0.0).and.' +
                          'electron2.lt.0.1 \n')
            # Flag yes, if HK format is compact
            p.stdin.write('no \n')
            # Column containing HK parameter times
            p.stdin.write('TIME \n')

            # Print output of program
            if verbose is True:
                with p.stdout:
                    for line in iter(p.stdout.readline, b''):
                        print '    ' + line,
                    p.stdout.close()
                    p.wait()

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Created all time filters'
