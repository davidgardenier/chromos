import os
import glob
from subprocess import Popen, PIPE

def find_data(obj, verbose=False):
    '''
    Create a list with all obsids, and feed it into Phil's xtescan2 program
    to find where each data file is located. Creates a file named
    <object>.obsid.list containing the paths to the different modes in each
    P<number> folder.

    Arguments:
     - obj: Object name
     - verbose: Give output of xtescan2 or not
    '''
    purpose = 'Determine file types'
    print purpose + '\n' + '='*len(purpose)

    root = os.getcwd()

    for e in glob.glob('./P*'):
        os.chdir(e)

        # Find obsid folders
        obsids = [o.split('/')[-1] for o in glob.glob('./*-*-*-*')]
        with open('./obsids.list','w') as f:
            f.write('\n'.join(obsids))

        # Execute Phil's script to determine location of files
        command = ['csh','./../../scripts/pc_ss/xtescan2','obsids.list', obj]
        p = Popen(command, stdout=PIPE)

        if verbose:
            for line in p.stdout:
                print '    ' + line

        p.wait()
        os.chdir(root)

    print '--> Determined file types'
