import os
import glob
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from collections import defaultdict
from astropy.io import fits

# -----------------------------------------------------------------------------
# ------------------------- Extract lightcurves -------------------------------
# -----------------------------------------------------------------------------


def energy_to_channel(epoch, table, energy):
    '''
    Function determine which channel corresponds best to an energy

    Arguments:
     - epoch in which measurement took place
     - table in which to look
     - energy which needs to be converted to a channel number

    Output:
     - channel number closest to the energy given
    '''

    # Split between the epochs 1&2&3&4 and 5.
    # Epoch 5 has two columns for different PCU1 and the others, however only
    # the latter column is taken, which strictly speaking is only for PCU123,4

    if epoch < 5:
        column = epoch + 1
    else:
        column = -1

    # Make a list of energies
    energies = [float(i.split()[column]) for i in table]

    # Compare the energy value to the energies list
    for i, e in enumerate(energies):
        if e > energy:

            # Check which element is closer to the energy
            above = energies[i]-energy
            below = energies[i-1]-energy

            # Return the associated channel number of that energy
            if abs(above) < abs(below):
                channel = table[i].split()[0]
            else:
                channel = table[i-1].split()[0]

            # Ensure the lowest energy channel is not returned
            # See Gleissner T., Wilms J., Pottschimdt K. etc. 2004
            if channel == '0-4':
                channel = table[1].split()[0]

            # Return the channel
            return channel


def calculated_energy_range(date,min_energy,max_energy):
    '''
    Import the channel energy conversion table, and return the required channel
    range in a format suitable for seextrct.

    Requires:
     - ./energy_channel_conversion.txt

    Arguments:
     - date at which the observation took place (in form 2001-06-28T15:36:23)
     - lowest energy in keV
     - highest energy in keV

    Output:
     - Channel range
    '''

    with open('./../../../scripts/subscripts/energy_channel_conversion.txt', 'r') as txt:
        text = list(txt)
        stop_dates = [x + y for x, y in zip(text[2].split()[2:6], text[3].split()[2:6])]
        end_dates = [datetime.strptime(t, '%m/%d/%y(%H:%M)') for t in stop_dates]
        
        if len(date) == 8:
            date = datetime.strptime(date, '%d/%m/%y')
        else:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

        if date < end_dates[0]:
            epoch = 1
        elif date < end_dates[1]:
            epoch = 2
        elif date < end_dates[2]:
            epoch = 3
        elif date < end_dates[3]:
            epoch = 4
        else:
            epoch = 5

        lower_range = energy_to_channel(epoch, text[12:], min_energy)
        upper_range = energy_to_channel(epoch, text[12:], max_energy)

    return str(lower_range) + '-' + str(upper_range)


def group_files(object_name):
    '''
    Function to group together multiple event and background files per obsid
    in a single file, to be able to give to saextrct and seextrct a single
    input.

    Arguments:
     - object_name

    Output:
     - Directionary with paths to the event_mode_*.list files and the
       <object_name>_bkg.list files
    '''

    event_modes = []

    # Find files with list of event mode files
    for f in glob.glob('./*/' + object_name + '.E_*.list'):
        event_modes.append(f)
            
    # Set up lists of data we want as output
    paths = {'event':[],'bkg':[]}
    dates = []

    for e in event_modes:
        d = defaultdict(list)
        t = defaultdict(list)

        # In each event mode file, split per obsid
        with open(e, 'r') as f:
            for line in f:
                obsid = line.split()[0].split('/')[0]
                path =  os.getcwd() + '/P' + obsid[:5] + '/' + line.split()[0]
                # Save the observation time and date
                t[obsid].append(line.split()[2])
                d[obsid].append(path)

        for key in d:

            # Define variables
            obsid = d[key][0].split('/')[6]
            timing = e.split('_')[1]
            path = d[key][0].split('pca')[0]
            
            # Write to file
            f = open(path + 'event_mode_' + timing + '.list', 'w')
            f.write('\n'.join(d[key]))
            f.close()

            # Save path to file and dates
            paths['event'].append(path + 'event_mode_' + timing + '.list')
            # Note I only save the first date of a series within an obsid
            dates.append(min(t[key]))

    # Find all bkg files, and make a list per obsid
    bkg_files = glob.glob('./*/*/' + object_name + '_bkg_?')

    d = defaultdict(list)

    for line in bkg_files:
        path = line.replace('./',os.getcwd() + '/')
        d[line.split('/')[2]].append(path)

    for key in d:
        path = d[key][0][:-2]
        f = open(path + '.list', 'w')
        f.write('\n'.join(d[key]))
        f.close()

    paths['bkg'] = ['/'.join(i.split('/')[:-1]) + '/' + object_name+'_bkg.list' for i in paths['event']]

    return paths, dates


def get_channel_range(cer, path_events):
    
    # Get the channels you're looking for
    abs_channels = cer.split('-')
    
    # Get the paths of the files
    paths = []
    with open(path_events) as p:
        for line in p:
            paths.append(line.strip())
    
    # Save all channel ranges to ensure none have changed
    channel_ranges = []
    
    for path in paths:
        # Get the list in which you want search for channels
        tevtb2 = fits.open(path)[1].header['TEVTB2']
        
        # Cut out the channels
        rel_channels = tevtb2.split(',C')[1][1:].split(']')[0].replace('~','-')
        
        # Indexes between which the abs channels are.
        indexes = []
        
        # For each absolute channel
        for i, c in enumerate(abs_channels):
            # Find the index of the closest value
            while True:
                try:
                    # If in the list, that's fine
                    index = rel_channels.index(c)
                    break
                except:
                    # Else keep adding to the value
                    c = str(int(c) + 1)
            
            # Make sure you cut in the right places,
            # for the first index, just after a comma
            if i == 0:
                while rel_channels[index - 1] != ',':
                    index -= 1
            # and for the last index just before a comma
            if i == 1:
                while rel_channels[index] != ',':
                    index += 1
            indexes.append(index)
        
        channel_ranges.append(rel_channels[indexes[0]:indexes[1]])
    
    return max(channel_ranges)

def seextrct(path_events, date, time_resolution, low_e, high_e, print_output):
    
    # First calculate the absolute energy range on basis of date
    cer = calculated_energy_range(date, low_e, high_e)
    # Then check for the corresponding range in the header of each event mode
    # file
    channel_range_from_file = get_channel_range(cer, path_events) 

    # Execute seextrct with the required bitfile
    p = Popen(['seextrct','bitfile=./../../../scripts/subscripts/bitfile_M'],
              stdout=PIPE, stdin=PIPE, stderr=STDOUT,
              bufsize=1)
              
    # Give the required input
    # -----------------------
    # Input file name
    p.stdin.write('@' + path_events + '\n')
    # Input GTI files to be OR'd with INFILE
    p.stdin.write('- \n')
    # Input GTI file to be AND'd with INFILE
    p.stdin.write('basic_' + time_resolution + '.gti \n')
    # Root name for output file
    p.stdin.write('firstlight_' + time_resolution + ' \n')
    # Name of TIME column
    p.stdin.write('TIME \n')
    # Name of COLUMN to be accumulated
    p.stdin.write('Event \n')
    # Input the binsize in seconds
    p.stdin.write('0.0078125 \n')
    # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
    p.stdin.write('LIGHTCURVE \n')
    # Type of binning for LIGHTCURVE
    p.stdin.write('RATE \n')
    # Type of binning for SPECTRUM
    p.stdin.write('SUM \n')
    # Starting time for summation in seconds
    p.stdin.write('INDEF \n')
    # Ending time for summation in seconds
    p.stdin.write('INDEF \n')
    # Input time intervals t1-t2,t3-t4 in seconds
    p.stdin.write('INDEF \n')
    # Minimum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Maximum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Input energy intervals to be retained 0-1,2-255
    p.stdin.write(channel_range_from_file + ' \n')
    # Input channels for each bin 0-5,6-255
    p.stdin.write('INDEF \n')

    # Print output of program
    with p.stdout:
        for oline in iter(p.stdout.readline, b''):

            # Ensure an aborting error is caught and displayed
            if oline.strip()=='Aborting...':
                print 'Had to abort while working on a file of type ' + time_resolution + '\n'
            elif print_output is True:
                print oline,
        p.stdout.close()
        p.wait()


def saextrct(path_bkg, date, time_resolution, low_e, high_e, print_output):
    '''
    #Function to extract a light curve file from background files
    '''

    # Let you know which file it's working on
    if print_output is True:
        print '-----------------------\n Working on background file\n-----------------------'

    # Execute saextrct
    p = Popen(['saextrct'], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
              bufsize=1)

    # Give the required input
    # -----------------------
    # Input file name
    p.stdin.write('@' + path_bkg + '\n')
    # Input GTI files to be OR'd with INFILE
    p.stdin.write('APPLY \n')
    # Input GTI file to be AND'd with INFILE
    p.stdin.write('basic_' + time_resolution + '.gti \n')
    # Root name for output file
    p.stdin.write('background_' + time_resolution + ' \n')
    # Accumulate (ONE) or (MANY) Spectral/Light Curves
    p.stdin.write('ONE \n')
    # Name of TIME column
    p.stdin.write('TIME \n')
    # Name of COLUMN to be accumulated
    p.stdin.write('GOOD \n')
    # Input the binsize in seconds
    p.stdin.write('16 \n')
    # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
    p.stdin.write('LIGHTCURVE \n')
    # Type of binning for LIGHTCURVE
    p.stdin.write('RATE \n')
    # Type of binning for SPECTRUM
    p.stdin.write('SUM \n')
    # Starting time for summation in seconds
    p.stdin.write('INDEF \n')
    # Ending time for summation in seconds
    p.stdin.write('INDEF \n')
    # Input time intervals t1-t2,t3-t4 in seconds
    p.stdin.write('INDEF \n')
    # Minimum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Maximum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Input energy intervals to be retained 0-1,2-255
    p.stdin.write(calculated_energy_range(date,low_e,high_e) + ' \n')
    # Input channels for each bin 0-5,6-255
    p.stdin.write('INDEF \n')

    # Print output of program
    with p.stdout:
        for oline in iter(p.stdout.readline, b''):

            # Ensure an aborting error is caught and displayed
            if oline.strip()=='Aborting...':
                print 'Had to abort while working on a file of type ' + time_resolution
            elif print_output is True:
                print oline,
        p.stdout.close()
        p.wait()
        
def extract_light_curve(object_name, extract_event_mode=True,
                        extract_background=True, print_output=False):
    '''
    Function to extract lightcurves for each obsid. These are placed in the
    obsid folders with the file name firstlight_<unit of time>.lc. While some
    errors will be caught, print output if unsure.

    Creates:
     - lightcurves files in each obsid folder, per time bin

    Arguments:
     - object_name: name of object
     - extract_event_mode: whether the function should execute seextrct to
                          extract the data to a light curve
     - extract_background: whether the function should exectute seaxtrct to
                          extract the background to data
     - print_output: prints the output of the seextrct program
    '''
    
    current_path = os.getcwd()
    paths, dates = group_files(object_name)

    for i in range(len(paths['event'])):

        # Defining corresponding event and bkg files
        e = paths['event'][i]
        b = paths['bkg'][i]
        d = dates[i]

        os.chdir('/'.join(e.split('/')[:-1]))

        # Let you know which file it's working on
        if print_output is True:
            print ('-----------------------\n ' +
                  'Working on ' + e.split('/')[6] +
                  '\n-----------------------')

        # Time resolution
        time_resolution = e.split('_')[-1][:-5]

        # Energy range
        low_e = 2
        high_e = 13
        
        if extract_event_mode:
            file_name = e.split('/')[-1]
            seextrct(file_name, d, time_resolution, low_e, high_e, print_output)
        if extract_background:
            bkg_name = b.split('/')[-1]
            saextrct(bkg_name, d, time_resolution, low_e, high_e, print_output)

    os.chdir(current_path)
    print '----------- \n ---> Created lightcurves'
