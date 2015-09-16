import os
import numpy as np
import fitsio
import glob

def find_light_curves():
    '''
    Function to obtain a list with paths to all light curves & backgrounds
    
    Output:
     - list with paths to all lightcurves & backgrounds
    '''
    
    light_curves = []
    backgrounds = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.startswith('firstlight') and f.endswith('.lc'):
                if len(glob.glob(root + '/rebinned_background_*')) == 0:
                    print 'No background found in', root
                    continue
                else:
                    lc = os.path.join(root, f)
                    light_curves.append(lc)
                    bkg = lc.split('firstlight')[0] + 'rebinned_background' + lc.split('firstlight')[1][:-2] + 'dat'
                    backgrounds.append(bkg)

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
    

def account_for_background(print_output=False):
    '''
    Function to correct for background - basically subtracts the rebinned
    background rates from the rates and saves them as corrected rates.
    '''
    
    # Find path to files
    paths_lc, paths_bkg = find_light_curves()
    
    # For each path
    for i, p in enumerate(paths_bkg):
        # Read in the rebinned_background and the rates of the lightcurves
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error  = np.loadtxt(p,dtype=float,unpack=True)
        rate, t, dt, n_bins, error = read_light_curve(paths_lc[i])
        
        corrected_rate = rate - bkg_rate

        # Path to which the data will be saved
        new_file = p.split('rebinned_background_')[0] + 'corrected_rate_' + p.split('rebinned_background_')[1][:5] + '.dat'
        
        # Write the corrected rates to a file
        with open(new_file, 'w') as out_file:
            for i in range(n_bins):
                out_file.write(repr(corrected_rate[i]) + ' ' + repr(t[i]) + ' ' + repr(dt) + ' ' + repr(n_bins) + ' ' + repr(error[i]) + '\n')
                
        if print_output:
            print '------------------ \n Have corrected for path', p
