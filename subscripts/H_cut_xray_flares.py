import json
import numpy as np
import matplotlib.pyplot as plt
#import sys

def cut_flare(lc, bkg_lc, resolution, mode):
    '''
    Function to detect whether an x-ray flare is present in a file. If so,
    it will cut around it 300*(1/128)s to the left, and 80000*(1/128)s to the
    right. This choice was made by eye comparisons of the average level before
    and after the flare.
    '''

    try:
        rate, t, dt, n_bins, error = np.loadtxt(lc, dtype=float, unpack=True)
    except IOError:
        return 'IOError'

    # Calculate the mean rate
    mean_rate = np.mean(rate)
    std = np.std(rate, ddof=1)

    # Compute the limit above which a X-ray flare must exist
    limit = mean_rate + 7*std

    ind_to_del = []

    try:
        n_bins = int(n_bins[0])
    except IndexError:
        return

    j = 0
    upper_limit = 80000

    while j < n_bins - 1:

        if rate[j] > limit and rate[j+1] > limit:
            ind_to_del.extend([l for l in range(j,max(j-300,0),-1)])
            ind_to_del.extend([l for l in range(j,min(j+upper_limit,n_bins))])
            j += upper_limit
        else:
            j += 1


    # If X-ray flares were detected
    if len(ind_to_del) > 0:

        # Read in the rebinned_background and the rates of the corrected rates
        try:
            bkg_rate = np.loadtxt(bkg_lc, dtype=float)
        except IOError:
            print '    ', 'Failed to locate background file'
            return

        # Remove the X-ray events
        rate = np.delete(rate, ind_to_del)
        bkg_rate = np.delete(bkg_rate, ind_to_del)
        t = np.delete(t, ind_to_del)
        error = np.delete(error, ind_to_del)

        n_bins = len(rate)
        bkg_n_bins = len(bkg_rate)

        # Names for output
        new_file = lc.split('bkg')[0] + 'xray_corrected_' + mode
        bkg_file = lc.split('bkg')[0] + 'xray_corrected_bkg_' + mode

        if mode != 'std2':
            new_file += '_' + resolution
            bkg_file += '_' + resolution

        # Write the X-ray flare corrected rates to a file
        with open(new_file, 'w') as out_file:
            for i in range(n_bins):
                line = [repr(rate[i]),
                        repr(t[i]),
                        str(dt[0]),
                        str(n_bins),
                        repr(error[i])]
                out_file.write(' '.join(line) + '\n')

        # Write the background X-ray flare corrected rates to a file
        with open(bkg_file, 'w') as out_file:
            for i in range(n_bins):
                out_file.write(repr(bkg_rate[i]) + '\n')

        return new_file, bkg_file

    else:
        return


def cut_xray_flares(print_output=False):
    '''
    Function to find X-ray flares in a light curve by finding when the rate
    exceeds more than 7sigma, and then cut around it. Write output to a file
    in an obsid-folder with the name corrected_rate_minus_xray_flare_
    <timingresolution>.dat if an X-ray flare was detected
    '''

    # Let the user know what's going to happen
    purpose = 'Cutting X-ray flares'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # For print statements
    template = "{0:14} {1:8} {2:1} {3:20}"

    # For each path to a light curve
    for obsid in d:
        for mode in d[obsid]:

            if 'path_bkg_corrected_lc' in d[obsid][mode] and mode !='std2':

                d[obsid][mode]['path_xray_corrected_lc'] = []
                d[obsid][mode]['path_xray_corrected_bkg_lc'] = []

                for i in range(len(d[obsid][mode]['path_bkg_corrected_lc'])):

                    bkg = d[obsid][mode]['path_rebinned_bkg'][i]
                    lc = d[obsid][mode]['path_bkg_corrected_lc'][i]

                    if mode != 'std2':
                        resolution = d[obsid][mode]['resolutions'][i]
                    else:
                        resolution = ''

                    result = cut_flare(lc, bkg, resolution, mode)

                    if result is None or result == 'IOError':
                        d[obsid][mode]['path_xray_corrected_lc'].append('')
                        d[obsid][mode]['path_xray_corrected_bkg_lc'].append('')

                        if print_output:
                            statement = (obsid,
                                         mode,
                                         resolution,
                                         '--> No X-ray flare')
                            print template.format(*statement)
                    else:
                        d[obsid][mode]['path_xray_corrected_lc'].append(result[0])
                        d[obsid][mode]['path_xray_corrected_bkg_lc'].append(result[1])

                        if print_output:
                            statement = (obsid,
                                         mode,
                                         resolution,
                                         '--> Found X-ray flare')
                            print template.format(*statement)

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Corrected lightcurves for X-ray flares'
