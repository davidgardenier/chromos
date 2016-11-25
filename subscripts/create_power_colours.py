# Functions to integrate under power spectra to create power colours
# Written by David Gardenier, davidgardenier@gmail.com


def power_colour(path):
    '''
    Function to calculate the power colour values per power spectrum.
    Integrates between 4 areas under the power spectrum (variance), and takes
    the ratio of the variances to calculate the power colour values.
    '''
    import numpy as np

    # Define the frequency bands in Hz
    #frequency_bands = [0.0039,0.031,0.25,2.0,16.0]
    # If you wish to shift the frequency bands by 5
    #frequency_bands = [0.0195,0.155,1.25,10.0,80.0]
    # If you wish to shift the frequency bands by 4
    frequency_bands = [0.0156,0.124,1.0,8.0,64.0]

    # Import data
    try:
        all_data = np.loadtxt(path,dtype=float)
        inverted_data = np.transpose(all_data)
    except IOError:
        print 'ERROR: Power spectrum not present'
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

    pc1_error = np.sqrt((variance_errors[2]/float(variances[2]))**2 +
                        (variance_errors[0]/float(variances[0]))**2)*pc1
    pc2_error = np.sqrt((variance_errors[1]/float(variances[1]))**2 +
                        (variance_errors[3]/float(variances[3]))**2)*pc2

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


def create_power_colours():
    '''
    Function to generate power spectral density based on RXTE lightcurves.
    '''

    # Let the user know what's going to happen
    purpose = 'Creating Power Colours'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    from math import isnan
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    # Get database
    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    d = defaultdict(list)
    for ps, group in db.groupby('power_spectra'):

        # Determine parameters
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        mode = group.modes.values[0]
        res = group.resolutions.values[0]

        print obsid, mode, res

        # Calculate power colour
        output = power_colour(ps)

        if output:
            pc1, pc1err, pc2, pc2err, constraint = output

            d['power_spectra'].append(ps)
            d['pc1_s4'].append(pc1)
            d['pc1_err_s4'].append(pc1err)
            d['pc2_s4'].append(pc2)
            d['pc2_err_s4'].append(pc2err)
            d['lt3sigma_s4'].append(constraint)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['pc1_s4','pc1_err_s4','pc2_s4','pc2_err_s4','lt3sigma_s4'])
    print 'DBNUNIQUE\n', db.apply(pd.Series.nunique)
    database.save(db)
    logs.stop_logging()
