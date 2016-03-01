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
    Look inside each event mode file to get the channel range it contains
    '''
    # Get the channels you're looking for
    abs_channels = cer.split('-')

    path = path_event

    # Get the list in which you want search for channels
    if mode == 'event':
        tevtb2 = fits.open(path)[1].header['TEVTB2']
        # Cut out the channels
        rel_channels = tevtb2.split(',C')[1][1:].split(']')[0].replace('~','-')
    elif mode == 'binned':
        tddes2 = fits.open(path)[1].header['TDDES2']
        rel_channels = tddes2.split('& C')[1][1:].split(']')[0].replace('~','-')
        if ',' not in rel_channels:
            return float('NaN')
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
                if c < 300:
                    c = str(int(c) + 1)
                else:
                    return float('NaN')

        # Make sure you cut in the right places,
        # for the first index, just after a comma
        if i == 0:
            while rel_channels[index - 1] != ',':
                index -= 1
        # and for the last index just before a comma
        if i == 1:
            end = len(rel_channels)
            while rel_channels[index] != ',':
                index += 1
                if index == end:
                    break
        indexes.append(index)

    channel_ranges = rel_channels[indexes[0]:indexes[1]]

    return channel_ranges


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

        for mode, path, time in zip(group.modes,group.paths_data,group.times):

            abs_channels = calculated_energy_range(time,MIN_E,MAX_E)
            final_channels = abs_channels

            if mode == 'event' or mode == 'binned':
                bin_channels = get_channel_range(mode, abs_channels, path)
                final_channels = bin_channels

            print obsid, mode, '-->', final_channels

            d['paths_data'].append(path)
            d['energy_channels'].append(final_channels)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['energy_channels'])
    database.save(db)
