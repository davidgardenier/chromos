# Functions to create power spectra from lightcurves
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def power_spectrum(path_lc, path_bkg, path_std1, npcu):

    import numpy as np
    import numpy.fft as fft
    import math
    import deadtime as deadt

    try:
        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = np.loadtxt(path_lc,dtype=float,unpack=True)
        bkg_rate = np.loadtxt(path_bkg, dtype=float, unpack=True)
    except IOError:
        print 'ERROR: Lightcurve does not exist'
        return

    # Check whether there are any counts
    if sum(rate) < 10:
        print 'ERROR: Lightcurve has zero count rate'
        return

    # Determine the number of bins
    try:
        n_bins = int(n_bins[0])
    except IndexError:
        print 'ERROR: No data in lightcurve file'
        return

    # Determine the (time) width of each bin
    dt = dt[0]

    # Express the length of each segment size in units of dt
    n = 512/dt
    # n should already be a power of 2 - but in case if isn't
    # this line will round it off to the nearest power of 2
    n_seg = pow(2, int(math.log(n, 2) + 0.5))

    # Whether you wish subtract white noise
    noise_subtraction = True

    # A list with indexes of segment end points
    segment_endpoints = []

    # The length of a segment starts at zero
    length = 0

    # Calculate where the data should be cut
    for j in xrange(1, n_bins):

        # Check for gaps; in case of a gap, set length to zero.
        if (t[j] - t[j-1]) < 1.5*dt:
            length = length+1
        else:
            length = 0

        # Check if the length has reached the required segment size
        if length == n_seg:

            # If so, add the endpoint to the endpoint list
            segment_endpoints.append(j)
            # And reset the length to zero:
            length = 0

    # Calculating the number of segments
    number_of_segments = len(segment_endpoints)
    # Stop calculations if no segments can be found
    if number_of_segments == 0:
        print 'WARNING: No segments found'
        return

    # Initialise the power spectrum array
    power_spectrum = np.zeros((n_seg))
    # Necessary for errors on power colour values
    power_spectrum_squared = np.zeros((n_seg))
    
    # Calculate the corresponding frequency grid
    # (assuming that dt is the same for all)
    frequency = fft.fftfreq(n_seg, dt)

    # Calculate the error on the frequencies
    frequency_error = (1.0/(2*dt*float(n_seg)))*np.ones(n_seg/2 - 1)

    # Initialise rate arrays
    rate_tot = []
    bkg_tot = []

    # For each segment
    for j in xrange(number_of_segments):
        # Make an array containing the segment of the light curve
        segment = rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]
        bkg_segment = bkg_rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]

        # Calculate the fast Fourier transform
        four_trans = fft.fft(segment, n_seg, 0)

        # Calculate the normalisation of the powerspectrum
        # (rms normalisation)
        norm = (2*dt)/(float(n_seg)*(np.mean(segment)**2))

        # Add the normalisation of the square of the FFT
        # to the power spectrum
        power_spectrum += norm*(np.absolute(four_trans))**2
        # Add the normalisation of the squared power spectrum
        power_spectrum_squared += (norm*(np.absolute(four_trans))**2)**2

        # For calculating the total white noise
        if noise_subtraction:
            rate_tot.extend(segment)
            bkg_tot.extend(bkg_segment)

    # Calculate the mean power spectrum
    power_spectrum = power_spectrum/float(number_of_segments)

    # Calculate the mean power spectrum
    power_spectrum_squared = power_spectrum_squared/float(number_of_segments)

    # Calculating the error on the power spectrum
    power_spectrum_error = power_spectrum/np.sqrt(float(number_of_segments))

    # Calculate the noise & subtract from the power spectrum
    if noise_subtraction:
        white_noise = (2*(np.mean(rate_tot)+np.mean(bkg_tot))/np.mean(rate_tot)**2)
        dead_noise = deadt.calculate_deadtime(path_std1, frequency, npcu=npcu)
        power_spectrum -= (white_noise*(dead_noise/2.))

    # Note the range of the power spectrum - this is due to the output
    # of the FFT function, which adds the negative powers at the end of
    # the list
    ps = power_spectrum[1:n_seg/2]
    ps_error = power_spectrum_error[1:n_seg/2]
    ps_squared = power_spectrum_squared[1:n_seg/2]
    frequency = frequency[1:n_seg/2]
    
    return ps, ps_error, ps_squared, number_of_segments, frequency, frequency_error


def create_power_spectra():
    '''
    Function to generate power spectral density based on RXTE lightcurves.
    '''

    # Let the user know what's going to happen
    purpose = 'Creating Power Spectra'
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
    for path_lc, group in db.groupby('bkg_corrected_lc'):
    
        # Check whether x-ray flare was present
        path_bkg = group.rebinned_bkg.values[0]
        flare = False
        if 'lc_no_flare' in group:
            if pd.notnull(group.lc_no_flare.values[0]):
                flare = True
                former_lc = path_lc
                path_lc = group.lc_no_flare.values[0]
                path_bkg = group.bkg_no_flare.values[0]

        # Determine parameters
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        mode = group.modes.values[0]
        res = group.resolutions.values[0]

        # Find std1 path
        std1 = db[((db.obsids==obsid) & (db.modes=='std1'))].paths_data.iloc[0]
        path_std1 = std1 + '.gz'
        
        # Determine the maximum number of pcus on during the observation
        npcu = group.npcu.values[0]
        
        print obsid, mode, res

        # Calculate power spectrum
        output = power_spectrum(path_lc, path_bkg, path_std1, npcu)

        if output:
            ps, ps_er, ps_sq, num_seg, freq, freq_er = output
            path_ps = path_obsid + mode + '_' + res + '.ps'

            # Create file within obsid folder
            with open(path_ps, 'w') as f:
                # For each value in a power spectrum
                for i, value in enumerate(ps):
                    line = (repr(value) + ' ' +
                            repr(ps_er[i]) + ' ' +
                            repr(freq[i]) + ' ' +
                            repr(freq_er[i]) + ' ' +
                            repr(ps_sq[i]) + ' ' +
                            repr(num_seg) + '\n')
                    f.write(line)

            if not flare:
                d['bkg_corrected_lc'].append(path_lc)
                d['lc_no_flare'].append(float('NaN'))
                d['power_spectra'].append(path_ps)
            else:
                d['bkg_corrected_lc'].append(former_lc)
                d['lc_no_flare'].append(path_lc)
                d['power_spectra'].append(path_ps)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['power_spectra'])
    database.save(db)
    logs.stop_logging()
