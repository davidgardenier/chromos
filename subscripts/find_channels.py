# Function to determine the energy channel range needed for input during
# extraction. Requires the file energy_conversion_table.txt to determine the
# initial channel selection.
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

from datetime import datetime
from astropy.io import fits

MIN_E = 2.
MAX_E = 13.

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

            if channel.startswith(','):
                channel = channel[1:]
        
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
    import paths

    with open(paths.subscripts + 'energy_channel_conversion.txt', 'r') as txt:
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


def get_channel_range(mode, cer, path_event):
    '''
    Look inside each file to get the channel range it contains
    '''
    # Get the channels you're looking for
    abs_channels = cer.split('-')

    path = path_event

    # Get the list in which you want search for channels
    if mode == 'event':
        tevtb2 = fits.open(path)[1].header['TEVTB2']
        print tevtb2
        if 'C' not in tevtb2:
            try:
                # I think this fixes VLE (Very Long Event) data files hidden as event files.
                # Not entirely sure about the rel_channels (usually they're given in the 
                # header as 5-255, but presumably that doesn't mean it's all one bin?)
                tddes2 = fits.open(path)[1].header['TDDES2']
                rel_channels = tddes2.split('& C')[1][1:].split(']')[0].replace('~','-')
                rel_channels = ','.join([str(e) for e in range(int(rel_channels.split('-')[0]), int(rel_channels.split('-')[1])+1)])
            except:
                print 'ERROR: No channel information in this file'
                return float('NaN')
        else:
            # Cut out the channels
            rel_channels = tevtb2.split(',C')[1][1:].split(']')[0].replace('~','-')
    elif mode == 'binned':
        tddes2 = fits.open(path)[1].header['TDDES2']
        print tddes2
        rel_channels = tddes2.split('& C')[1][1:].split(']')[0].replace('~','-')
        if ',' not in rel_channels:
            return float('NaN')

    # Get a list of numbers to actually search through
    chs = []
    for cr in rel_channels.split(','):

        # Spent ages looking, but couldn't find what 0~4,(5:35) means, or (0-4),
        # (5:35). Am assuming ':' means all channel in that range (on basis of
        # an extracted spectrum), and not sure what () means
        if '(' in cr:
            cr = cr.split(')')[0].split('(')[1]
            if '-' in cr:
                crs = cr.split('-')
            if ':' in cr:
                crs = cr.split(':')
            cr = [e for e in range(int(crs[0]), int(crs[1])+1)]
        elif '-' in cr:
            cr = [e for e in range(int(cr.split('-')[0]), int(cr.split('-')[1])+1)]
        elif ':' in cr:
            crs = cr.split(':')
            cr = [e for e in range(int(crs[0]), int(crs[1])+1)]
        else:
            cr = [int(cr)]

        chs.append(cr)

    low_ch = int(abs_channels[0])
    high_ch = int(abs_channels[-1])

    # Find whether the absolute channels are in the relative channel range
    low_ind = [(i, c.index(low_ch)) for i, c in enumerate(chs) if low_ch in c]
    # If wanting mutually exclusive energies (so energy bands don't overlap)
    # then use the following line (only works for event and binned mode files)
    # low_ind = [(i+1, c.index(low_ch)+1) for i, c in enumerate(chs) if low_ch in c]
    high_ind = [(i, c.index(high_ch)) for i, c in enumerate(chs) if high_ch in c]

    # If not, return Nan
    if not low_ind or not high_ind:
        return float('NaN')
    # Else return a string in the original type of format (with dashes and
    # commas refering to different channel ranges, or different channels)
    else:
        ch_ranges = chs[low_ind[0][0]:high_ind[0][0]+1]
        ch_str = []
        for c in ch_ranges:
            if len(c) == 1:
                c = str(c[0])
            else:
                c = '-'.join([str(c[0]),str(c[-1])])
            ch_str.append(c)
        channels = ','.join(ch_str)

    # Ensure the lowest energy channel is not returned
    # See Gleissner T., Wilms J., Pottschimdt K. etc. 2004
    if channels.startswith('0'):
        channels = channels[4:] #Assuming channels doesn't do 0-19,etc
        
    if channels.startswith(','):
        channels = channels[1:]
        
    return channels


def find_channels():
    '''
    Function to determine the channel range needed for input during extraction.
    Requires the file energy_conversion_table.txt to determine the initial
    channel selection.
    '''

    purpose = 'Finding the correct channels for later extraction'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    d = defaultdict(list)
    for obsid, group in db.groupby(['obsids']):
        group = group.drop_duplicates('paths_data')

        print obsid
        for mode, path, time in zip(group.modes,group.paths_data,group.times):

            # Determine channels according to epoch
            abs_channels = calculated_energy_range(time,MIN_E,MAX_E)
            final_channels = abs_channels

            # Check in which fashion the channels are binned, and return these
            if mode == 'event' or mode == 'binned':
                bin_channels = get_channel_range(mode, abs_channels, path)
                final_channels = bin_channels

            print '   ', mode, '-->', final_channels

            d['paths_data'].append(path)
            d['energy_channels'].append(final_channels)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['energy_channels'])
    database.save(db)
    logs.stop_logging()
