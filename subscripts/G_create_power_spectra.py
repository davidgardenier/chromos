import os
import numpy as np
import numpy.fft as fft
import fitsio
import math
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# ----------------------- Create power spectra --------------------------------
# -----------------------------------------------------------------------------

def find_files():
    '''
    Function to obtain a list with paths to corrected light curves for both
    xray flares and background, if not existant, only the light curves which
    have been corrected for the background. Also import the rebinned background
    or if available the corrected for xray flares background files.

    Output:
     - list with paths to all background corrected data
     - list with paths to all background data
    '''

    light_curves = []
    backgrounds = []

    folders = [x[0] for x in os.walk('.')]
    upper_level = os.getcwd()

    for d in folders:
        os.chdir(d)
        xray_flare = False

        for f in os.listdir('.'):

            # If an xray flare was present, use the corrected file
            # minus xray flare
            if (f.startswith('corrected_rate_minus_xray_flares_') and
                f.endswith('.dat')):
                light_curves.append(os.path.join(os.getcwd(), f))
                xray_flare = True
            # If there was an xray flare, there should be a background
            # which had been corrected for the flare
            if (f.startswith('corrected_bkg_rate_minus_xray_flares_') and
                f.endswith('.dat')):
                backgrounds.append(os.path.join(os.getcwd(), f))
                xray_flare = True

            if not xray_flare:
                # If not, just use the corrected file
                if f.startswith('corrected_rate_') and f.endswith('.dat'):
                    light_curves.append(os.path.join(os.getcwd(), f))
                 # Else use the rebinned file
                if f.startswith('rebinned_background_') and f.endswith('.dat'):
                    backgrounds.append(os.path.join(os.getcwd(), f))
            else:
                continue

        os.chdir(upper_level)

    return light_curves, backgrounds


def generate_power_spectra(print_output=False):
    '''
    Function to generate power spectral density based on RXTE lightcurves.

    Output:
     - The PSD values for each lightcurve and a corresponding frequency grid,
    both with errors. If requested, saved figures of the PSDs.

    Structure of Output: 4 parts, callable with [0],[1],[2],[3]. First contains
    a list of the seperate psds. Second a list with the corresponding errors.
    Third the frequency grid and fourth the frequency errors. For the first
    two, one needs to specify which lightcurve data is wanted.
    '''

    # Determine paths to light curves
    paths_lc, paths_bkg = find_files()

    # Determine the expected number of spectra
    n_spectra = len(paths_lc)

    # Initialize the arrays in which power spectra will be saved
    power_spectra = []
    power_spectra_error = []
    bkg_power_spectra = []
    bkg_power_spectra_error = []

    # Calculate the normalised power spectra with errors
    for i in xrange(n_spectra):

        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = np.loadtxt(paths_lc[i],
                                                dtype=float,
                                                unpack=True)

        # Read in the background files
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = np.loadtxt(
                                                                  paths_bkg[i],
                                                                  dtype=float,
                                                                  unpack=True)
        # Determine the number of bins
        n_bins = int(n_bins[0])

        # Determine the (time) width of each bin
        dt = dt[0]

        # Express the length of each segment size in units of dt
        n = 512/dt
        # n should already be a power of 2 - but in case if isn't
        # this line will round it off to the nearest power of 2
        n_seg = pow(2, int(math.log(n, 2) + 0.5))

        # Check the data time resolution corresponds to the
        # background time resolution
        if bkg_dt[0] != dt:
            print ' Warning: data & background have different time resolutions'

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
                print '-----------------------'
                print 'Working on:', paths_lc[i].split('/')[-2]
                if paths_lc[i].split('/')[-1].split('_')[2] == 'minus':
                    print 'X-ray flare: Present'
                print 'Number of segments:', number_of_segments
                print 'Ceasing with calculations - no segments'

                # Still append an item to the list of power spectrum to
                # ensure the length of the arrays remain the same
                power_spectra.append('nan')
                power_spectra_error.append('nan')

            continue

        # Initialise the power spectrum array
        power_spectrum = np.zeros((n_seg))

        ## Initialise the white noise array
        #if white_noise_subtraction:
        #    white_noise_per_segment = np.zeros((n_seg))

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
            

            # Calculate the white noise per segment & subtract from the power
            # spectrum
            if white_noise_subtraction:
                white_noise = (2*(np.mean(segment)+np.mean(bkg_segment))/np.mean(segment)**2)
                power_spectrum -= white_noise
                
        # Calculate the mean power spectrum
        power_spectrum = power_spectrum/float(number_of_segments)

        # Calculating the error on the power spectrum
        power_spectrum_error = power_spectrum/np.sqrt(float(number_of_segments))

        # Adding to the list of power spectra of all paths
        # Note the range of the power spectrum - this is due to the output
        # of the FFT function, which adds the negative powers at the end of
        # the list
        power_spectra.append(power_spectrum[1:n_seg/2])
        power_spectra_error.append(power_spectrum_error[1:n_seg/2])

        # Give the user information on what's happening
        if print_output:
            print '-----------------------'
            print 'Working on:', paths_lc[i].split('/')[-2]
            if paths_lc[i].split('/')[-1].split('_')[2] == 'minus':
                print 'X-ray flare: Present'
            print 'Number of segments:', number_of_segments
            print 'Succeeded in taking the Discrete FFT'
            print 'White noise subtraction:', white_noise_subtraction

    # Calculate the corresponding frequency grid
    # (assuming that dt is the same for all)
    frequency = fft.fftfreq(n_seg, dt)[1:n_seg/2]
    
    # Calculate the error on the frequencies
    frequency_error = (1.0/(2*dt*float(n_seg)))*np.ones(n_seg/2 - 1)

    # Save the power spectra
    for i, spectrum in enumerate(power_spectra):
    
        # Unless the number of segments was zero
        # Then, skip that obsid
        if isinstance(spectrum, basestring):
            continue
            
        # Presuming everything went well
        else:

            # Create file within obsid folder
            f = open((paths_lc[i].split('correct')[0] +
                      'power_spectrum_' +
                      paths_lc[i].split('correct')[1].split('_')[-1]), 'w')

            # For each value in a power spectrum
            for item, value in enumerate(spectrum):
                # power_spectra value, error, frequency, freq_error
                line = (repr(value) + ' ' + 
                        repr(power_spectra_error[i][item]) + ' ' + 
                        repr(frequency[item]) + ' ' +
                        repr(frequency_error[item]) + '\n')

                f.write(line)

            f.close()

            #plt.plot(frequency, spectrum, label=paths_lc[i].split('/')[-2])
            #plt.legend()
            #plt.show()

    print '----------- \n Created power spectra'

    # Return all power spectram, frequency grids and errors on both
    return power_spectra, power_spectra_error, frequency, frequency_error

if __name__ == '__main__':
    generate_power_spectra(print_output=False)
