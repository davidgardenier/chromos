import json
import glob
import os
from subprocess import Popen, PIPE, STDOUT

def create_response(verbose=False):
    '''
    Function to create response files on basis of extracted std2 spectra
    '''

    # Print purpose of program
    purpose = 'Creating response files'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Find all filter files and add to dictionary
    for obsid in d:
        if 'std2' in d[obsid]:

            mode = 'std2'
            sp = d[obsid][mode]['path_sp'][0]
            bkg_sp = d[obsid][mode]['path_bkg_sp'][0]
            fltr = d[obsid]['filter']['paths'][0]

            root = sp.split('std2')[0]
            output = root + mode + '.rsp'
            bkg_output = root + 'background_' + mode + '.rsp'
            d[obsid][mode]['rsp'] = [output]
            d[obsid][mode]['bkg_rsp'] = [bkg_output]

            print obsid, output, bkg_output

            # Set up the command for pcarsp

            pcarsp = ['pcarsp',
                      '-f' + sp, #Input
                      '-a' + fltr, #Filter file
                      '-n' + output, #Output file
                      '-s'] #Use smart std2 mode

            # Set up the command for pcarsp
            bkgpcarsp = ['pcarsp',
                         '-f' + bkg_sp, #Input
                         '-a' + fltr, #Filter file
                         '-n' + bkg_output, #Output file
                         '-s'] #Use smart std2 mode

            # Execute pcarsp
            for s in [pcarsp, bkgpcarsp]:
                p = Popen(s,
                          stdout=PIPE,
                          stdin=PIPE,
                          stderr=STDOUT,
                          bufsize=1)

                # Print output of program
                if verbose:
                    with p.stdout:
                        for line in iter(p.stdout.readline, b''):
                            print '    ' + line,
                        p.stdout.close()
                        p.wait()

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Created a response file for all files'