import json
from subprocess import Popen, PIPE, STDOUT


def saextrct(mode,
             path_background,
             filterfile,
             time_range,
             channels,
             output_background,
             verbose):
    '''
    Function to extract a light curve file from background files
    '''

    if mode == 'binned':
        b = '0.0078125 \n'
    else:
        b = '16 \n'

    # Execute saextrct
    p = Popen(['saextrct'], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
              bufsize=1)

    # Give the required input
    # -----------------------
    # Input file name
    p.stdin.write('@' + path_background + '\n')
    # Input GTI files to be OR'd with INFILE
    p.stdin.write('APPLY \n')
    # Input GTI file to be AND'd with INFILE
    p.stdin.write(filterfile + ' \n')
    # Root name for output file
    p.stdin.write(output_background + ' \n')
    # Accumulate (ONE) or (MANY) Spectral/Light Curves
    p.stdin.write('ONE \n')
    # Name of TIME column
    p.stdin.write('TIME \n')
    # Name of COLUMN to be accumulated
    p.stdin.write('@./column_selection.txt \n')
    # Input the binsize in seconds
    p.stdin.write(b)
    # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
    p.stdin.write('BOTH \n')
    # Type of binning for LIGHTCURVE
    p.stdin.write('RATE \n')
    # Type of binning for SPECTRUM
    p.stdin.write('SUM \n')
    # Starting time for summation in seconds
    p.stdin.write('INDEF \n')
    # Ending time for summation in seconds
    p.stdin.write('INDEF \n')
    # Input time intervals t1-t2,t3-t4 in seconds
    p.stdin.write('@' + time_range + ' \n')
    # Minimum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Maximum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Input energy intervals to be retained 0-1,2-255
    p.stdin.write('INDEF \n')
    # Input channels for each bin 0-5,6-255
    p.stdin.write('INDEF \n')

    # Print output of program
    with p.stdout:
        for oline in iter(p.stdout.readline, b''):

            # Ensure an aborting error is caught and displayed
            if oline.strip()=='Aborting...':
                print 'Had to abort bkg \n'
            elif verbose is True:
                print '        ' + oline,
        p.stdout.close()
        p.wait()


def extract_light_curves(verbose=False):
    '''
    Function to extract all light curves from event & goodxenon files
    '''

    # Let the user know what's going to happen
    purpose = 'Extracting light curves'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Apply the necassary extractions for each obsid
    for obsid in d:
        if 'std2' in d[obsid]:
            mode = 'std2'

            # Set up dictionaries
            d[obsid][mode]['path_lc'] = []
            d[obsid][mode]['path_bkg_lc'] = []
            d[obsid][mode]['path_sp'] = []
            d[obsid][mode]['path_bkg_sp'] = []

            # For each path of a list of paths to event/goodmode mode
            # files (may be more than one if there are different
            # resolutions within one obsid)
            for i in range(len(d[obsid][mode]['path_list'])):

                # Define the parameters needed for input into seextrct
                path_data = d[obsid][mode]['path_list'][i]

                filterfile = d[obsid]['filter']['path_list']
                time_range = d[obsid]['filter']['time_range']
                channels = d[obsid][mode]['channels'][i]
                output = filterfile.split('time')[0] + mode

                if channels == '':
                    continue

                # Define the additional parameters for the background files
                path_background = d[obsid][mode]['background_path_list']
                output_background = filterfile.split('time')[0]+'background_'+mode

                # Ensure there is a channel range between which a
                # light curve can be extracted
                if channels != '':

                    # Add information to the dictionary
                    d[obsid][mode]['path_lc'].append(output + '.lc')
                    d[obsid][mode]['path_bkg_lc'].append(output_background + '.lc')
                    d[obsid][mode]['path_sp'].append(output + '.pha')
                    d[obsid][mode]['path_bkg_sp'].append(output_background + '.pha')

                    # Tell the user what you're about to embark on
                    if verbose:
                        print '    ', obsid, mode, '-->', 'Extracting lightcurve'

                    # Run the extraction program
                    saextrct(mode,
                             path_data,
                             filterfile,
                             time_range,
                             channels,
                             output,
                             verbose)

                    # Tell the user what you're about to embark on
                    if verbose:
                        print '    ', obsid, mode, '-->', 'Extracting background'

                    # Run the extraction program for the background
                    saextrct('std2',
                             path_background,
                             filterfile,
                             time_range,
                             channels,
                             output_background,
                             verbose)

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Extracted the lightcurves'
