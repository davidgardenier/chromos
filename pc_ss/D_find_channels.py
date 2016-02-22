import json
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

    with open('./../scripts/pc_ss/energy_channel_conversion.txt', 'r') as txt:
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
            return ''
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
                    return ''

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


def find_channels(verbose=False):
    '''
    Function to determine the channel range needed for input during extraction.
    Requires the file energy_conversion_table.txt to determine the initial
    channel selection.
    '''
    # Let the user know what's going to happen
    purpose = 'Finding the correct channels for later extraction'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)


    for obsid in d:

        # In case of 'event' mode, determine the binned channels (extract from
        # header of eventmode file)
        if 'event' in d[obsid].keys():
            d[obsid]['event']['channels'] = []

            # For each path calculate the absolute channels, and then the
            # binned channel range
            for i, path in enumerate(d[obsid]['event']['paths']):
                abs_channels = calculated_energy_range(d[obsid]['event']['times'][i],MIN_E,MAX_E)
                bin_channels = get_channel_range('event', abs_channels, path)
                d[obsid]['event']['channels'].append(bin_channels)

                if verbose:
                    print'    ', 'E', obsid, '-->', bin_channels

        # In case of 'std2' mode, determine the absolute channels (from the
        # energy conversion table)
        if 'std2' in d[obsid].keys():
            d[obsid]['std2']['channels'] = []

            # For each path calculate the absolute channels
            for i, path in enumerate(d[obsid]['std2']['paths']):
                abs_channels = calculated_energy_range(d[obsid]['std2']['times'][i],MIN_E,MAX_E)
                d[obsid]['std2']['channels'].append(abs_channels)

                if verbose:
                    print '    ', 'S', obsid, '-->', abs_channels

        # In case of 'goodxenon' mode, determine the absolute channels
        if 'goodxenon' in d[obsid].keys():
            d[obsid]['goodxenon']['channels'] = []

            # For each path calculate the absolute channels, and then the
            # binned channel range
            for i, path in enumerate(d[obsid]['goodxenon']['paths']):
                abs_channels = calculated_energy_range(d[obsid]['goodxenon']['times'][i],MIN_E,MAX_E)
                d[obsid]['goodxenon']['channels'].append(abs_channels)

                if verbose:
                    print '    ', 'G', obsid, '-->', abs_channels

        # In case of 'binned' mode, determine the absolute channels (from the
        # energy conversion table)
        if 'binned' in d[obsid].keys():
            d[obsid]['binned']['channels'] = []

            # For each path calculate the absolute channels
            for i, path in enumerate(d[obsid]['binned']['paths']):
                abs_channels = calculated_energy_range(d[obsid]['binned']['times'][i],MIN_E,MAX_E)
                bin_channels = get_channel_range('binned', abs_channels, path)
                d[obsid]['binned']['channels'].append(bin_channels)
                if verbose:
                    print '    ', 'B', obsid, '-->', bin_channels

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Calculated the required energy ranges'
