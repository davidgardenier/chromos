import os
import fitsio
import numpy as np
import matplotlib.pyplot as plt
import glob
# -----------------------------------------------------------------------------
# ----------------------- Rebin the background --------------------------------
# -----------------------------------------------------------------------------

def find_light_curves():
    '''
    Function to obtain a list with paths to all light curves
    
    Output:
     - list with paths to all lightcurves
    '''
    
    light_curves = []
    backgrounds = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.startswith('firstlight') and f.endswith('.lc'):
                if len(glob.glob(root + '/background_*')) == 0:
                    print 'No background found in', root
                    continue
                else:
                    lc = os.path.join(root, f)
                    light_curves.append(lc)
                    backgrounds.append(lc.split('firstlight')[0] + 'background' + lc.split('firstlight')[1])
                    
                    
    return light_curves, backgrounds
             

def read_light_curve(path):
    '''
    Function to read the data from the lightcurve fits files. Adapted with 
    permission from Jakob van den Eijnden.
    
    Input parameters:
     - path: path of the lightcurve
    
    Output parameters:
     - rate: rate of photons per second
     - t: time grid of the observation
     - dt: time resolution; usually 1/128. for RXTE data
     - n_bins: number of time bins in the total observation. 
     - error: error on the rate of photons per second
    '''    

    lc = path
    lc_fits = fitsio.FITS(lc)
    lc_header = lc_fits['RATE'].read_header()
        
    n_bins = lc_header['NAXIS2']
    dt = lc_header['TIMEDEL']
    t_0 = lc_header['TSTARTI'] + lc_header['TSTARTf']
    
    t = lc_fits['RATE']['TIME'][:]
    rate = lc_fits['RATE']['RATE'][:]
    error = lc_fits['RATE']['ERROR'][:]    
    
    lc_fits.close()
    
    return rate, t, dt, n_bins, error


def rebin_background(print_output=False):
    '''
    Function to rebin the background data to the same binning as the actual 
    light curve. The basic idea is the draw a line between each point of the 
    background rates and once you know the function to describe this line, you
    can take the x-value (in this case time) of each point of a light curve and
    then calculate which corresponding y-value (or rate) it should have. 
    
    Note an error of 0 has been applied to the rebinned background rates for 
    now, but this will have to be solved at some stage.
    
    The function writes a file in each obsid folder with the name
    'rebinned_background_<bintime>.dat' in the same format as the light curves.
    '''

    # Determine paths to light curves
    paths_lc, paths_bkg = find_light_curves()
    print len(paths_lc), len(paths_bkg)
    # Determine number of light curves we'll have to loop though
    n_spectra = len(paths_lc)
    
    # For each light curve
    for i in xrange(n_spectra):
        
        if print_output:
            print '------------------ \n Working on path', paths_lc[i]
        
        # Define how to find the background files    
        bkg = paths_bkg[i]

        # Reading in the lightcurve data for each path/file
        rate, t, dt, n_bins, error = read_light_curve(paths_lc[i])
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = read_light_curve(bkg)
        
        # Set up an array for the rebinned background data
        rebinned_bkg_rate = []
        upper_index = 0

        # For each datapoint of the actual light curve 
        for k in range(n_bins):
            # If it's time value is smaller than the background time
            if t[k] <= bkg_t[0]:
                # Then always take the rate value of the smallest background time
                rebinned_bkg_rate.append(bkg_rate[0])
            # If it's time value is larger than the background time
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
                    
                    # Fit the two points with a line
                    fit = np.polyfit(x, y, 1)
                    # Turn it into a function so you can give a x-value and 
                    # it will tell you the y-value (in this case the rate)
                    fit_fn = np.poly1d(fit)
                    
                # Add the necessary rate value
                rebinned_bkg_rate.append(fit_fn(t[k]))
               
        # Errors still need to be calculated
        rebinned_bkg_error = [0]*n_bins
        
        # Path to which the data will be saved
        new_file = paths_lc[i].split('firstlight_')[0] + 'rebinned_background_' + paths_lc[i].split('firstlight_')[1][:5] + '.dat'
        
        # Write the rebinned background data to a file
        with open(new_file, 'w') as out_file:
            for m in range(n_bins):
                # In the same format as the light curves
                out_file.write(repr(rebinned_bkg_rate[m]) + ' ' + repr(t[m]) + ' ' + repr(dt) + ' ' + repr(n_bins) + ' ' + repr(rebinned_bkg_error[m]) + '\n')
        
        if print_output:
            print ' Written rebinned background to file'
