import json
import numpy as np
import matplotlib.pyplot as plt

def power_colour(path):
    '''
    Function to calculate the power colour values per power spectrum.
    Integrates between 4 areas under the power spectrum (variance), and takes
    the ratio of the variances to calculate the power colour values.
    '''

    # Define the frequency bands in Hz
    frequency_bands = [0.0039,0.031,0.25,2.0,16.0]

    # Import data
    try:
        all_data = np.loadtxt(path,dtype=float)
        inverted_data = np.transpose(all_data)
    except IOError:
        return

    # Give the columns their names
    power_spectrum = inverted_data[0]
    power_spectrum_error = inverted_data[1]
    frequency = inverted_data[2]
    frequency_error = inverted_data[3]
    power_spectrum_squared = inverted_data[4]
    number_of_segments = inverted_data[5][0]

    variances = []
    variance_errors = []
    index_frequency_bands = []

    # Convert frequency bands to index values from in the frequency list
    for fb in frequency_bands:
        index = min(range(len(frequency)), key=lambda i: abs(frequency[i]-fb))
        index_frequency_bands.append([index])

    # Group indexes into sets of style [low, high)
    for i, e in enumerate(index_frequency_bands[:-1]):
        e.append(index_frequency_bands[i+1][0]-1)

    del index_frequency_bands[-1]

    # Integrate the power spectra within the frequency bands
    bin_width = frequency[1]-frequency[0]

    for e in index_frequency_bands:
        variance = bin_width*sum(power_spectrum[e[0]:e[1]])
        variances.append(variance)

        # Calculate errors on the variance
        # (see appendix Heil, Vaughan & Uttley 2012)
        # M refers to the number of segments
        one_over_sqrt_M = 1/float(np.sqrt(number_of_segments))
        prop_std = sum(power_spectrum_squared[e[0]:e[1]])
        variance_error = bin_width*one_over_sqrt_M*np.sqrt(prop_std)
        variance_errors.append(variance_error)

    pc1 = variances[2]/float(variances[0])
    pc2 = variances[1]/float(variances[3])

    pc1_error = np.sqrt((variance_errors[2]/float(variances[2]))**2 + (variance_errors[0]/float(variances[0]))**2)*pc1
    pc2_error = np.sqrt((variance_errors[1]/float(variances[1]))**2 + (variance_errors[3]/float(variances[3]))**2)*pc2

    # Applying similar filter to Lucy, only plotting if variance constrained
    # within 3sigma

    for i, e in enumerate(variance_errors):
        v = variances[i]

        if v - 3*e > 0:
            constrained = True
        else:
            constrained = False
            break

    return pc1, pc1_error, pc2, pc2_error, constrained


def create_power_colours(print_output=False):
    '''
    Function calculate the power colours values from power spectra.
    '''

    # Let the user know what's going to happen
    purpose = 'Calculating power colours'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    pc_1 = []
    pc_1_error = []
    pc_2 = []
    pc_2_error = []
    obsids = []
    modes = []
    constraints = []

    # If a path to a power spectrum can be found, calculate the power colours
    for obsid in d:
        for mode in d[obsid]:
            if 'path_ps' in d[obsid][mode]:

                path = d[obsid][mode]['path_ps'][0]

                output = power_colour(path)

                if output is not None:

                    if print_output:
                        print '    ', obsid, mode

                    pc1, pc1err, pc2, pc2err, constrained = output

                    pc_1.append(pc1)
                    pc_2.append(pc2)
                    pc_1_error.append(pc1err)
                    pc_2_error.append(pc2err)
                    obsids.append(obsid)
                    modes.append(mode)
                    constraints.append(constrained)

    # Sort the power colours
    srt_list = []
    for i in range(len(pc_1)):
        srt_list.append((pc_1[i],
                         pc_2[i],
                         pc_1_error[i],
                         pc_2_error[i],
                         obsids[i],
                         modes[i],
                         constraints[i]))

    sorted_list = sorted(srt_list, key=lambda obsid: obsid[4])
    pc1, pc2, pc1_error, pc2_error, obsids, modes, constraints = zip(*sorted_list)

    # Define colour for plotting
    #color=iter(plt.cm.rainbow(np.linspace(0,1,len(pc1))))

    # Remove instances where obsids have both a goodxenon and event mode file
    # Choose for goodxenon above event mode file
    obsids = np.array(obsids)

    i_del = []

    for io, o in enumerate(obsids):

        ii = np.where(obsids == o)[0]

        if len(ii)>1:

            ms = [modes[l] for l in ii]

            if ms.count('event') > 1:
                print 'WARNING: Multiple event modes present'

            elif 'goodxenon' in ms and 'event' in ms:
                i_del.append(ii[ms.index('event')])

            else:
                print 'WARNING: Multiple data modes, but not both gx and event'

    # Ugly way of deleting unwanted elements
    pc1 = [pc1[i] for i in range(len(pc1)) if i not in i_del]
    pc1_error = [pc1_error[i] for i in range(len(pc1_error)) if i not in i_del]
    pc2 = [pc2[i] for i in range(len(pc2)) if i not in i_del]
    pc2_error = [pc2_error[i] for i in range(len(pc2_error)) if i not in i_del]
    obsids = [obsids[i] for i in range(len(obsids)) if i not in i_del]
    modes = [modes[i] for i in range(len(modes)) if i not in i_del]
    constraints = [constraints[i] for i in range(len(constraints)) if i not in i_del]

    for i in range(len(pc1)):

        if modes[i] == 'goodxenon':
            colour = 'r'
        if modes[i] == 'event':
            colour = 'b'

        if constraints[i] is True:
            plt.errorbar(pc1[i], pc2[i], xerr=pc1_error[i], yerr=pc2_error[i],
                         ls='none', marker='x', c=colour, label=obsids[i])
        else:
            continue

    plt.xscale('log', nonposx='clip')
    plt.yscale('log', nonposy='clip')
    plt.xlim([0.001, 1000])
    plt.ylim([0.001, 1000])
    #plt.legend()
    plt.show()
    #plt.savefig('./pwr_colours.png')

    # Write power colours to file
    f = open('./pwr_colours.dat', 'w')

    for i, value in enumerate(pc1):
        line = (repr(pc1[i]) + ' ' +
                repr(pc2[i]) + ' ' +
                obsids[i] + ' ' +
                modes[i] + ' ' +
                str(constraints[i]) + '\n')
        f.write(line)

    f.close()

    print '---> Calculated power colours'
