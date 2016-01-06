import json
import glob
from subprocess import Popen, PIPE, STDOUT

def create_background(verbose=False):
    '''
    Function to create a background files for each standard2 data file, and
    create a list of paths directing to these piles. Uses the ftool pcabackest
    to create the backgrounds.
    '''

    # Let the user know what's going to happen
    purpose = 'Creating background files for each obsid'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Create a background for each obsid
    for obsid in d:
        std2_mode = False

        # Background files for std2 are similar to those of GoodXenon
        if 'std2' in d[obsid].keys():
            d[obsid]['std2']['background_paths'] = []
            std2_mode = True
            n_s = 0

        # For each standard2 file
        for path in d[obsid]['std2']['paths']:

            if std2_mode:
                n_s += 1
                output = path.split('pca')[0] + 'background_std2_mode_' + str(n_s)
                d[obsid]['std2']['background_paths'].append(output)

                # Set up the command for pcabackest
                pcabackest = ['pcabackest',
                              'infile=' + path,
                              'outfile=' + output,
                              'filterfile=' + d[obsid]['filter']['paths'][0],
                              'modelfile=./../scripts/pc_ss/pca_bkgd_cmbrightvle_eMv20051128.mdl',
                              'saahfile=./../scripts/pc_ss/pca_saa_history.gz',
                              'modeltype=both',
                              'interval=16',
                              'propane=no',
                              'layers=yes',
                              'gaincorr=no',
                              'fullspec=no',
                              'interp=yes',
                              'syserr=no',
                              'clobber=yes',
                              'mode=no']

                # Execute pcabackest
                p = Popen(pcabackest, stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)

                # Print output of program
                if verbose:
                    with p.stdout:
                        for line in iter(p.stdout.readline, b''):
                            print '    ' + line,
                        p.stdout.close()
                        p.wait()

                # Write the paths to each background files which has just been created
                # to a file for input during the extraction of the light curve
                list_with_paths = d[obsid]['std2']['background_paths'][0].split('std2')[0] + 'paths_background_std2_mode'

                # Add the path to the dictionary
                d[obsid]['std2']['background_path_list'] = list_with_paths

                # Write the list of paths to file
                with open(list_with_paths, 'w') as text:
                    text.write('\n'.join(d[obsid]['std2']['background_paths']))

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Created a background for all files'
