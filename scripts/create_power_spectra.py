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
            
            # If an xray flare was present, use the corrected file minus xray flare
            if f.startswith('corrected_rate_minus_xray_flares_') and f.endswith('.dat'):
                light_curves.append(os.path.join(os.getcwd(), f))
                xray_flare = True
            # If there was an xray flare, there should be a background
            # which had been corrected for the flare
            if f.startswith('corrected_bkg_rate_minus_xray_flares_') and f.endswith('.dat'):
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
    
    n_spectra = len(paths_lc)
    
    # Calculate the normalised power spectra with errors:
    power_spectra = []
    power_spectra_error = []
    bkg_power_spectra = []
    bkg_power_spectra_error = []
       
    for i in xrange(n_spectra):
        
        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = np.loadtxt(paths_lc[i],
                                                dtype=float,
                                                unpack=True)
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = np.loadtxt(
                                                                  paths_bkg[i],
                                                                  dtype=float,
                                                                  unpack=True)
        
        n_bins = int(n_bins[0])
        dt = dt[0]
        # Give length of each segment size in seconds
        n = 512/dt
        n_seg = pow(2, int(math.log(n, 2) + 0.5))

        # Give length of each segment size in seconds
        if bkg_dt[0] != dt:
            print ' Warning: data & background have different time resolutions'
        
        # Whether you wish subtract white noise
        white_noise_subtraction = True
        
        # Check if n_seg is an integer power of 2:
        if int(math.log(n_seg, 2)) != math.log(n_seg, 2):
            return 'Error: the size of the segments should be a power of 2'
            
        # Cutting the data into segments of the correct length:
        segment_endpoints = []  
                
        length = 0
        
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
        
        # Calculating the fourier transform for each segment and averaging
        number_of_segments = len(segment_endpoints)
        power_spectrum = np.zeros((n_seg))
        
        if white_noise_subtraction:
            white_noise_per_segment = np.zeros((n_seg))

        for j in xrange(number_of_segments):
            segment = rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]
            four_trans = fft.fft(segment, n_seg, 0)
            power_spectrum += (np.absolute(four_trans))**2

            bkg_segment = bkg_rate[segment_endpoints[j]-n_seg : segment_endpoints[j]]
                    
            if white_noise_subtraction:
                white_noise_per_segment += (2*(np.mean(segment)+np.mean(bkg_segment))/np.mean(segment)**2)
                  
        power_spectrum = power_spectrum/float(number_of_segments)
        
        if white_noise_subtraction:
            white_noise = white_noise_per_segment/float(number_of_segments)
        
        # Normalising the powerspectrum (fractional rms normalisation)
        norm = (2*dt)/(float(n_seg)*(np.mean(rate)**2))
        power_spectrum = power_spectrum*norm
        
        # Calculating the error on the power spectrum
        power_spectrum_error = power_spectrum/np.sqrt(float(number_of_segments))
        
        # Subtracting white noise
        if white_noise_subtraction:
            #white_noise = (2.0/np.mean(rate))*np.ones(n_seg) <- Adam's white noise function
            power_spectrum -= white_noise*norm

        # Adding to the list of power spectra of all paths
        power_spectra.append(power_spectrum[1:n_seg/2])
        power_spectra_error.append(power_spectrum_error[1:n_seg/2])
               
        if print_output:
            print '-----------------------' 
            print 'Working on:', paths_lc[i].split('/')[-2]
            if paths_lc[i].split('/')[-1].split('_')[2] == 'minus':
                print 'X-ray flare: Present'
            print 'Number of segments:', number_of_segments
            print 'Succeeded in taking the Discrete FFT'
            print 'White noise subtraction:', white_noise_subtraction 

    # Plotting the powerspectra (we assume that dt is the same for all)
    # frequency grid
    frequency = fft.fftfreq(n_seg, dt)[1:n_seg/2]
    frequency_error = (1.0/(2*dt*float(n_seg)))*np.ones(n_seg/2 - 1)
    
    # Save the power spectra
    for i, spectrum in enumerate(power_spectra):
        # Create file within obsid folder
        f = open(paths_lc[i].split('correct')[0] + 'power_spectrum_' + paths_lc[i].split('correct')[1].split('_')[-1], 'w')
        
        # For each value in a power spectrum
        for item, value in enumerate(spectrum):
            # power_spectra value, error, frequency, freq_error
            line = (repr(value) + ' ' + repr(power_spectra_error[i][item]) + ' '
                    + repr(frequency[item]) + ' ' + repr(frequency_error[item])
                    + '\n')
            
            f.write(line)
            
        f.close()
        
        #plt.plot(frequency, spectrum, label=paths_lc[i].split('/')[-2])
        #plt.legend()
        #plt.show()
        
    print '----------- \n Created power spectra'
    
    # Returning all power spectram, frequency grids and errors on both
    return power_spectra, power_spectra_error, frequency, frequency_error


if __name__ == '__main__':
    generate_power_spectra(print_output=False)
