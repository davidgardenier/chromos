import json
import fitsio
import numpy as np

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



def rebin(path_lc, path_bkg, mode, resolution):

    # Import data
    try:
        rate, t, dt, n_bins, error = read_light_curve(path_lc)
        bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = read_light_curve(path_bkg)
    except IOError:
        return None

    # Output
    path_rebinned_bkg = path_bkg.split('back')[0] + 'rebinned_bkg_lc_' + mode + '_' + resolution
    path_bkg_corrected_lc = path_lc.split('light')[0] + 'bkg_corrected_lc_' + mode + '_' + resolution

    # Set up an array for the rebinned background data
    rebinned_bkg_rate = []
    upper_index = 0

    # For each datapoint of the actual light curve 
    for k in range(n_bins):
        # If its time value is smaller than the background time
        if t[k] <= bkg_t[0]:
            # Then always take the rate value of the smallest background time
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
        
    # Write the background corrected data to a file
    with open(path_bkg_corrected_lc, 'w') as out_file:
        for n in range(n_bins):
            out_file.write(repr(bkg_corrected_lc[n]) + ' ' + repr(t[n]) + ' ' + repr(dt) + ' ' + str(n_bins) + ' ' + repr(error[n]) + '\n')
       
    return path_rebinned_bkg, path_bkg_corrected_lc  


def rebin_background(print_output=False):
    '''
    Function to rebin all background files to the same resolution as the
    event/goodXenon files (which is 1/128s).
    '''
    
    # Let the user know what's going to happen
    purpose = 'Rebinning background'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)
    
    # For each path to a light curve
    for obsid in d:
        for mode in d[obsid]:
            if 'path_lc' in d[obsid][mode].keys():
            
                d[obsid][mode]['path_rebinned_bkg'] = []
                d[obsid][mode]['path_bkg_corrected_lc'] = []
                
                for i in range(len(d[obsid][mode]['path_lc'])):

                    # Determine the paths
                    path_lc = d[obsid][mode]['path_lc'][i]
                    path_bkg = d[obsid][mode]['path_bkg_lc'][i]
                    resolution = d[obsid][mode]['resolutions'][i]
                    
                    # Rebin, and create a corrected version
                    paths = rebin(path_lc, path_bkg, mode, resolution)
                    
                    if paths is None:
                        # Put in a place holder if no light curve was found
                        success = False
                        d[obsid][mode]['path_rebinned_bkg'].append('')
                        d[obsid][mode]['path_bkg_corrected_lc'].append('')
                    else:
                        # Append paths to dictionary
                        success = True
                        d[obsid][mode]['path_rebinned_bkg'].append(paths[0])
                        d[obsid][mode]['path_bkg_corrected_lc'].append(paths[1])
                    
                    if print_output:
                        print '    ', obsid, mode, resolution, '-->', success

                    
    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))
        
    print '---> Rebinned & corrected for background of all files' 
                    
