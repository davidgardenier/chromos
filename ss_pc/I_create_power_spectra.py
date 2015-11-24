import json
import numpy as np
import math
import numpy.fft as fft
from progress_bar import *
from sys import stdout

def power_spectrum(path_lc, path_bkg, print_output):

    try:
        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = np.loadtxt(path_lc,
                                                dtype=float,
                                                unpack=True)

        # Read in the background files
        bkg_rate = np.loadtxt(path_bkg, dtype=float, unpack=True)

    except IOError:
        return

    # Determine the number of bins
    try:
        n_bins = int(n_bins[0])
    except IndexError:
        return

    # Determine the (time) width of each bin
    dt = dt[0]

    # Express the length of each segment size in units of dt
    n = 512/dt
    # n should already be a power of 2 - but in case if isn't
    # this line will round it off to the nearest power of 2
    n_seg = pow(2, int(math.log(n, 2) + 0.5))

    # Whether you wish subtract white noise
    white_noise_subtraction = True

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

        # Let the user know what's happened
        if print_output:
            return 'No segments'

    # Initialise the power spectrum array
    power_spectrum = np.zeros((n_seg))
    # Necessary for errors on power colour values
    power_spectrum_squared = np.zeros((n_seg))

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
        if white_noise_subtraction:
            rate_tot.extend(segment)
            bkg_tot.extend(bkg_segment)

    # Calculate the mean power spectrum
    power_spectrum = power_spectrum/float(number_of_segments)

    # Calculate the mean power spectrum
    power_spectrum_squared = power_spectrum_squared/float(number_of_segments)

    # Calculating the error on the power spectrum
    power_spectrum_error = power_spectrum/np.sqrt(float(number_of_segments))

    # Calculate the white noise & subtract from the power spectrum
    if white_noise_subtraction:
        white_noise = (2*(np.mean(rate_tot)+np.mean(bkg_tot))/np.mean(rate_tot)**2)
        power_spectrum -= white_noise

    # Note the range of the power spectrum - this is due to the output
    # of the FFT function, which adds the negative powers at the end of
    # the list
    ps = power_spectrum[1:n_seg/2]
    ps_error = power_spectrum_error[1:n_seg/2]
    ps_squared = power_spectrum_squared[1:n_seg/2]

    # Calculate the corresponding frequency grid
    # (assuming that dt is the same for all)
    frequency = fft.fftfreq(n_seg, dt)[1:n_seg/2]

    # Calculate the error on the frequencies
    frequency_error = (1.0/(2*dt*float(n_seg)))*np.ones(n_seg/2 - 1)

    return ps, ps_error, ps_squared, number_of_segments, frequency, frequency_error


def create_power_spectra(print_output=False):
    '''
    Function to generate power spectral density based on RXTE lightcurves.
    '''

    # Let the user know what's going to happen
    purpose = 'Creating power spectra'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # For progress bar
    num_obsid = float(len(d))
    o = 0
    t0 = datetime.now()

    # For print statements
    template = "{0:14} {1:8} {2:1} {3:20}"

    # For each path to a light curve
    for obsid in d:
        o += 1
        t = datetime.now()
        update_progress(o/num_obsid, t0, t)

        for mode in d[obsid]:
            if 'path_xray_corrected_lc' in d[obsid][mode].keys():

                for i, path in enumerate(d[obsid][mode]['path_xray_corrected_lc']):

                    # If path is empty, use the standard bkg_corrected lightcurve
                    if path == '':
                        if d[obsid][mode]['path_rebinned_bkg'][i] != '':
                            path = d[obsid][mode]['path_bkg_corrected_lc'][i]
                            path_bkg = d[obsid][mode]['path_rebinned_bkg'][i]
                        else:
                            continue
                    else:
                        # Otherwise use the x-ray corrected one
                        path_bkg = d[obsid][mode]['path_xray_corrected_bkg_lc'][i]

                    # Now that it has been determined which paths need to be used
                    output = power_spectrum(path, path_bkg, print_output)
                    # Create list for paths to power spectra
                    d[obsid][mode]['path_ps'] = []

                    # Deal with the various outputs
                    success = False
                    if output is None:
                        d[obsid][mode]['path_ps'].append('')
                        message = 'File doesn\'t exsist'
                    elif output == 'No segments':
                        d[obsid][mode]['path_ps'].append('')
                        message = 'No segments'
                    else:
                        message = 'Writing spectrum to file'
                        success = True

                    # Define the resolution
                    if mode != 'std2':
                        res = path.split('_')[-1]
                    else:
                        res = ''

                    if print_output:
                        statement = ['\r   ', obsid, mode, res,
                                     '--> ', message, '\n']
                        stdout.write(template.format(*statement))
                        update_progress(o/num_obsid, t0, t)

                    if success:
                        ps, ps_er, ps_sq, num_seg, freq, freq_er = output
                        file_path = ('/').join(path.split('/')[:3]) + '/'
                        file_name = 'power_spectrum_'
                        file_type = ('_').join(path.split('_')[-2:])
                        output_file = file_path + file_name + file_type

                        #d[obsid][mode]['path_power_spectrum']

                        # Create file within obsid folder
                        f = open(output_file, 'w')

                        # For each value in a power spectrum
                        for i, value in enumerate(ps):
                            # power_spectra value, error, frequency, freq_error
                            line = (repr(value) + ' ' +
                                    repr(ps_er[i]) + ' ' +
                                    repr(freq[i]) + ' ' +
                                    repr(freq_er[i]) + ' ' +
                                    repr(ps_sq[i]) + ' ' +
                                    repr(num_seg) + '\n')

                            f.write(line)

                        f.close()

                        d[obsid][mode]['path_ps'].append(output_file)

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Created power spectra'
