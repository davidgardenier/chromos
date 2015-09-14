import os
import numpy as np
import matplotlib.pyplot as plt

def find_files():
    '''
    Function to obtain a list with paths to all corrected rates & backgrounds
    
    Output:
     - list with paths to all corrected rates  & backgrounds
    '''
    
    corrected_rates = []
    backgrounds = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.startswith('corrected_rate_') and f.endswith('.dat') and len(f)==24:
                corrected_rates.append(os.path.join(root, f))
            if f.startswith('rebinned_background_') and f.endswith('.dat'):
                backgrounds.append(os.path.join(root, f))
                
    return corrected_rates, backgrounds
    
    
def cut_xray_flares(print_output=False):
    '''
    Function to find X-ray flares in a light curve by finding when the rate 
    exceeds more than 5sigma, and then search to the left and right of it when
    the rate diminishes to 1sigma (and right hand side when the average of 10
    points is less than 1sigma). Write output to a file in an obsid-folder with
    the name corrected_rate_minus_xray_flare_<timingresolution>.dat if an X-ray
    flare was detected
    '''
    # Find path to files
    paths_cr, paths_bkg = find_files()
    
    # For each path
    for i, p in enumerate(paths_bkg):

        if print_output:
            print '------------ \n Trying to find X-ray flares in', paths_cr[i]
            
        rate, t, dt, n_bins, error = np.loadtxt(paths_cr[i], dtype=float, unpack=True)
        
        # Calculate the mean rate
        mean_rate = np.mean(rate)
        std = np.std(rate, ddof=1)
        
        # Compute the limit above which a X-ray flare must exist
        limit = mean_rate + 7*std
        
        indexes_to_remove = []
        
        n_bins = int(n_bins[0])
        
        j = 0
        upper_limit = 80000
        
        while j < n_bins:
                   
            if rate[j] > limit and rate[j+1] > limit:
                indexes_to_remove.extend([l for l in range(j,max(j-300,0),-1)])
                indexes_to_remove.extend([l for l in range(j,min(j+upper_limit,n_bins))])
                j += upper_limit
            else:
                j += 1
            
        '''
        # Loop through the rate values
        for j in range(int(n_bins-1)):
            if j not in indexes_to_remove:
                # Find X-ray flares
                if rate[j] > limit and rate[j+1] > limit:
                
                    # If found search backwards till the values reach the mean
                    # again
                    for l in range(j,0,-1):
                        if rate[l] > mean_rate:
                            indexes_to_remove.append(l)
                        else:
                            break
                    
                    for l in range(j,min(j+1500,n_bins)):
                        indexes_to_remove.append(l)
                    # And search forwards until the average of 20 points is
                    # smaller than the mean
                    #for l in range(j,n_bins):
                        
                    #    if np.mean(rate[l-10:l+10]) > mean_rate:
                    #        indexes_to_remove.append(l)
                    #    else:
                    #        break
                    #continue
            else:
                continue
        '''
        # If X-ray flares were detected
        if len(indexes_to_remove) > 0:
            
            # Read in the rebinned_background and the rates of the corrected 
            # rates
            bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = np.loadtxt(p,
                                                                   dtype=float,
                                                                   unpack=True)
            #plt.scatter(t, rate,c='r',lw=0)
            
            # Remove the X-ray events
            rate = np.delete(rate, indexes_to_remove)
            bkg_rate = np.delete(bkg_rate, indexes_to_remove)
            t = np.delete(t, indexes_to_remove)
            bkg_t = np.delete(bkg_t, indexes_to_remove)
            error = np.delete(error, indexes_to_remove)
            bkg_error = np.delete(bkg_error, indexes_to_remove)
            
            n_bins = len(rate)
            bkg_n_bins = len(bkg_rate)
            
            # Path to which the data will be saved
            new_file = p.split('rebinned_background_')[0] + 'corrected_rate_minus_xray_flares_' + p.split('rebinned_background_')[1][:5] + '.dat'
            
            if print_output:
                print ' Wait...'
                
            # Write the X-ray flare corrected rates to a file
            with open(new_file, 'w') as out_file:
                for i in range(n_bins):
                    out_file.write(repr(rate[i]) + ' ' + repr(t[i]) + ' ' + str(dt[0]) + ' ' + str(n_bins) + ' ' + repr(error[i]) + '\n')
                    
            # Path to which the background data will be saved
            bkg_file = p.split('rebinned_background_')[0] + 'corrected_bkg_rate_minus_xray_flares_' + p.split('rebinned_background_')[1][:5] + '.dat'
            
            # Write the background X-ray flare corrected rates to a file
            with open(bkg_file, 'w') as out_file:
                for i in range(n_bins):
                    out_file.write(repr(bkg_rate[i]) + ' ' + repr(bkg_t[i]) + ' ' + str(bkg_dt[0]) + ' ' + str(bkg_n_bins) + ' ' + repr(bkg_error[i]) + '\n')
                    
            if print_output:
                print ' Written output'

            #plt.scatter(t,rate,c='b',lw=0)
            #plt.show()
