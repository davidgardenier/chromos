import json
import glob
from subprocess import Popen, PIPE, STDOUT

def create_background(print_output=False):
    '''
    Function to create a background files for each standard2 data file, and
    create a list of paths directing to these piles. Uses the ftool pcabackest
    to create the backgrounds. One for event mode files, one for goodxenon 
    (must be gain corrected)
    '''
    
    # Let the user know what's going to happen
    purpose = 'Creating background files for each obsid'
    print purpose + '\n' + '='*len(purpose)
    
    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)
    
    # Create a background for each obsid
    for obsid in d:
        event_mode = False
        goodxenon_mode = False
        
        if 'event' in d[obsid].keys():
            d[obsid]['event'] = {'background_paths':[]}
            event_mode = True
            # Set up a counter to determine the number of background files per obsid
            n_e = 0
            
        # Background files are slightly different for GoodXenon, as you 
        # shouldn't correct for gain corrections
        if 'goodxenon' in d[obsid].keys():
            d[obsid]['goodxenon'] = {'background_paths':[]}
            goodxenon_mode = True
            n_g = 0

        # For each standard2 file
        for path in d[obsid]['std2']['paths']:
            
            # Add to the counter
            if event_mode:
                n_e += 1
                output = path.split('pca')[0] + 'background_event_mode_' + str(n_e)
                # Determine the output names of the background
                d[obsid]['event']['background_paths'].append(output)

                # Set up the command for pcabackest
                pcabackest = ['pcabackest',
                              'infile=' + path,
                              'outfile=' + output,
                              'filterfile=' + d[obsid]['filter']['paths'][0],
                              'modelfile=./../scripts/subscripts/pca_bkgd_cmbrightvle_eMv20051128.mdl',
                              'saahfile=./../scripts/subscripts/pca_saa_history.gz',
                              'modeltype=both',
                              'interval=16',
                              'propane=no',
                              'layers=no',
                              'gaincorr=yes',
                              'gcorrfile=caldb',
                              'fullspec=yes',
                              'interp=yes',
                              'syserr=no',
                              'clobber=yes',
                              'mode=no']
                
                # Execute pcabackest
                p = Popen(pcabackest, stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)

                # Print output of program
                if print_output is True:
                    with p.stdout:
                        for line in iter(p.stdout.readline, b''):
                            print '    ' + line,
                        p.stdout.close()
                        p.wait()
                
                # Write the paths to each background files which has just been created
                # to a file for input during the extraction of the light curve
                list_with_paths = d[obsid]['event']['background_paths'][0].split('background')[0] + 'paths_background_event_mode'
                # Add the path to the dictionary
                d[obsid]['event']['background_path_list'] = list_with_paths
                # Write the list of paths to file
                with open(list_with_paths, 'w') as text:
                    text.write('\n'.join(d[obsid]['event']['background_paths']))
                         
            if goodxenon_mode:
                n_g += 1
                output = path.split('pca')[0] + 'background_goodxenon_mode_' + str(n_g)
                d[obsid]['goodxenon']['background_paths'].append(output)

                # Set up the command for pcabackest
                pcabackest = ['pcabackest',
                              'infile=' + path,
                              'outfile=' + output,
                              'filterfile=' + d[obsid]['filter']['paths'][0],
                              'modelfile=./../scripts/subscripts/pca_bkgd_cmbrightvle_eMv20051128.mdl',
                              'saahfile=./../scripts/subscripts/pca_saa_history.gz',
                              'modeltype=both',
                              'interval=16',
                              'propane=no',
                              'layers=no',
                              'gaincorr=no',
                              'fullspec=yes',
                              'interp=yes',
                              'syserr=no',
                              'clobber=yes',
                              'mode=no']

                # Execute pcabackest
                p = Popen(pcabackest, stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)

                # Print output of program
                if print_output is True:
                    with p.stdout:
                        for line in iter(p.stdout.readline, b''):
                            print '    ' + line,
                        p.stdout.close()
                        p.wait()
    
                # Write the paths to each background files which has just been created
                # to a file for input during the extraction of the light curve
                list_with_paths = d[obsid]['goodxenon']['background_paths'][0].split('background')[0] + 'paths_background_goodxenon_mode'
                
                # Add the path to the dictionary
                d[obsid]['goodxenon']['background_path_list'] = list_with_paths
                
                # Write the list of paths to file
                with open(list_with_paths, 'w') as text:
                    text.write('\n'.join(d[obsid]['goodxenon']['background_paths']))

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))
        
    print '---> Created a background for all files' 
