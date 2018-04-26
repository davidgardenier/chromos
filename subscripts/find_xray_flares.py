# Functions to detect when an X-ray flare happens and to cut around it
# OUTDATED: Use Phil's new script to find obsids with flares
# Written by David Gardenier, 2015-2016


def cut_flare(path_obsid, lc, bkg_lc, res, mode):
    '''
    Function to determine if xray flare is present, and if so, to cut it from
    the lightcurve and bkg lightcurve before trying to calculate power colours
    '''

    import numpy as np

    try:
        rate, t, dt, n_bins, error = np.loadtxt(lc, dtype=float, unpack=True)
    except IOError:
        print 'ERROR: No lightcurve file'
        return

    # Calculate the mean rate
    mean_rate = np.mean(rate)
    std = np.std(rate, ddof=1)

    # Compute the limit above which a X-ray flare must exist
    limit = mean_rate + 7*std

    ind_to_del = []

    try:
        n_bins = int(n_bins[0])
    except IndexError:
        print 'ERROR: Lightcurve file empty'
        return

    j = 0
    upper_limit = 80000
    ind_limits = []
    while j < n_bins - 1:

        if rate[j] > limit and rate[j+1] > limit:
            ind_to_del.extend([l for l in range(j,max(j-300,0),-1)])
            ind_to_del.extend([l for l in range(j,min(j+upper_limit,n_bins-1))])
            ind_limits.append(max(j-300,0))
            ind_limits.append(min(j+upper_limit,n_bins-1))
            j += upper_limit
        else:
            j += 1

    # If X-ray flares were detected
    if len(ind_to_del) > 0:

        # Determine between which times a flare took place
        time_limits = [t[i] for i in ind_limits]
        flare_times = str(time_limits[0])
        for i,e in enumerate(time_limits[1:]):
            if not i%2:
                flare_times += '-' + str(e)
            else:
                flare_times += ',' + str(e)

        # Read in the rebinned_background and the rates of the corrected rates
        try:
            bkg_rate = np.loadtxt(bkg_lc, dtype=float)
        except IOError:
            print 'ERROR: Failed to locate background file'
            return

        # Remove the X-ray events
        rate = np.delete(rate, ind_to_del)
        bkg_rate = np.delete(bkg_rate, ind_to_del)
        t = np.delete(t, ind_to_del)
        error = np.delete(error, ind_to_del)

        n_bins = len(rate)
        bkg_n_bins = len(bkg_rate)

        # Names for output
        new_file = path_obsid + 'noflarelc_' + mode + '_' + res
        bkg_file = path_obsid + 'noflarebkg_' + mode + '_' + res

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

        return new_file, bkg_file, flare_times

    else:
        return


def cut_xray_flares():
    '''
    Function to find X-ray flares in a light curve by finding when the rate
    exceeds more than 7sigma, and then cut around it. Write output to a file
    in an obsid-folder with the name corrected_rate_minus_xray_flare_
    <timingresolution>.dat if an X-ray flare was detected
    '''

    # Let the user know what's going to happen
    purpose = 'Determining X-ray flares'
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

    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    d = defaultdict(list)
    for path_lc, group in db.groupby('bkg_corrected_lc'):

        # Set parameters
        obsid = group.obsids.values[0]
        path_bkg = group.rebinned_bkg.values[0]
        res = group.resolutions.values[0]
        mode = group.modes.values[0]
        path_obsid = group.paths_obsid.values[0]
        print obsid, mode, res

        # Calculate whether flare present
        result = cut_flare(path_obsid, path_lc, path_bkg, res, mode)

        if result:
            print 'Flare between:', result[2]
            d['bkg_corrected_lc'].append(path_lc)
            d['lc_no_flare'].append(result[0])
            d['bkg_no_flare'].append(result[1])
            d['flare_times'].append(result[2])

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['lc_no_flare','bkg_no_flare','flare_times'])
    database.save(db)
    logs.stop_logging()
