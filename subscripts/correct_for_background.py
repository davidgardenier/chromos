def read_light_curve(path):
    '''
    Function to read the data from the lightcurve fits files.

    Input parameters:
     - path: path of the lightcurve

    Output parameters:
     - rate: rate of photons per second
     - t: time grid of the observation
     - dt: time resolution; usually 1/128. for RXTE data
     - n_bins: number of time bins in the total observation.
     - error: error on the rate of photons per second
    '''
    from astropy.io import fits

    hdulist = fits.open(path)
    # Header stuff
    header = hdulist[1].header
    n_bins = header['NAXIS2']
    dt = header['TIMEDEL']
    # Data stuff
    data = hdulist[1].data
    t = data['TIME']
    rate = data['RATE']
    error = data['ERROR']

    return rate, t, dt, n_bins, error


def rebin(path_obsid, path_lc, path_bkg, mode, resolution):
    '''
    Function to rebin lbackgrounds and correct lightcurves for them
    '''
    import numpy as np
    
    try:
        rate, t, dt, n_bins, error = read_light_curve(path_lc)
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = read_light_curve(path_bkg)
    except IOError:
        print 'ERROR: No lightcurve!'
        return float('NaN'), float('Nan')

    # Output
    path_rebinned_bkg = path_obsid + 'rebinned_bkg_lc_' + mode #TODO
    path_bkg_corrected_lc = path_obsid + 'bkg_corrected_lc_' + mode

    if mode != 'std2':
        path_rebinned_bkg += '_' + resolution
        path_bkg_corrected_lc += '_' + resolution

        # Set up an array for the rebinned background data
        rebinned_bkg_rate = []
        upper_index = 0

        # For each datapoint of the actual light curve
        for k in range(n_bins):
            # If its time value is smaller than the background time
            if t[k] <= bkg_t[0]:
                # Then always take the rate value of the smallest bkg time
                rebinned_bkg_rate.append(bkg_rate[0])
            # If its time value is larger than the background time
            elif t[k] >= bkg_t[-1]:
                # Then take the rate value of the last background time
                rebinned_bkg_rate.append(bkg_rate[-1])
            else:
                # If the time value is larger than the background time upper
                # index
                if t[k] > bkg_t[upper_index]:

                    # Add to the index, so the next line can be calculated
                    upper_index += 1

                    # Keep adding if there's a large gap - you only want to
                    # start where the rate begins
                    while t[k] - bkg_t[upper_index] > bkg_dt:
                        upper_index += 1

                    # Logically, the lower index is one less
                    lower_index = upper_index - 1
                    # The x-coordinates of the line:
                    x = [bkg_t[lower_index], bkg_t[upper_index]]
                    # The y-coordinates of the line
                    y = [bkg_rate[lower_index], bkg_rate[upper_index]]

                # Add the necessary rate value
                rebinned_bkg_rate.append(np.interp(t[k], x, y))

        # Write the rebinned background data to a file
        with open(path_rebinned_bkg, 'w') as out_file:
            for n in range(n_bins):
                out_file.write(repr(rebinned_bkg_rate[n]) + '\n')

        # Correct the rate for the background
        bkg_corrected_lc = rate - rebinned_bkg_rate

    else:
        bkg_corrected_lc = rate - bkg_rate
        # Write the rebinned background data to a file
        with open(path_rebinned_bkg, 'w') as out_file:
            for n in range(n_bins):
                out_file.write(repr(bkg_rate[n]) + '\n')

    # Write the background corrected data to a file
    with open(path_bkg_corrected_lc, 'w') as out_file:
        for n in range(n_bins):
            out_file.write(repr(bkg_corrected_lc[n]) + ' ' +
                           repr(t[n]) + ' ' +
                           repr(dt) + ' ' +
                           str(n_bins) + ' ' +
                           repr(error[n]) + '\n')

    return path_rebinned_bkg, path_bkg_corrected_lc


def correct_for_background():
    '''
    Function to intrapolate background files to correct various mode files for
    the corresponding background count rate
    '''

    purpose = 'Accounting for backgrounds'
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
    for path_lc, group in db.groupby('lightcurves'):
        
        # Layer background subtraction is done in xspec, so skip these
        if path_lc.endswith('per_layer.lc'):
            continue
        
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        path_bkg = group.lightcurves_bkg.values[0]    
        res = group.resolutions.values[0]
        mode = group.modes.values[0]
        if (mode == 'gx1' or mode == 'gx2'):
            mode = 'gx'
        print obsid, mode, res
        
        # Rebin, and create a corrected version
        paths = rebin(path_obsid, path_lc, path_bkg, mode, res)
        rebinned_bkg = paths[0]
        bkg_corrected_lc = paths[1]
        
        d['lightcurves'].append(path_lc)
        d['rebinned_bkg'].append(rebinned_bkg)
        d['bkg_corrected_lc'].append(bkg_corrected_lc)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['rebinned_bkg','bkg_corrected_lc'])
    print db.info()
    database.save(db)
    logs.stop_logging()
