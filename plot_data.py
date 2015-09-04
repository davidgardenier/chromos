import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic
from matplotlib import gridspec
import os
import fitsio

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
    
    return rate, t, dt, n_bins, error, t_0
    

def obtain_paths():
    '''
    Function to find the paths to all obsids
    '''
    paths_obsids = []

    for root, dirs, files in os.walk('./'):
        for d in dirs:
            path = os.path.join(root, d)
            if len(path.split('/'))==3 and len(d.split('-'))==4:
                if not (d.endswith('A') or d.endswith('Z')):
                    paths_obsids.append(path)
                    
    return paths_obsids


def plot_obsid(show=False):
    '''
    Function to plot the light curve, power spectrum, freq*power spectrum
    and the placing on the power colour-colour diagram per obsid
    
    Arguments:
     - show: if True, shows the graphs and doesn't save them.
             if False, does not show the graphs, but does save them.         
    '''
    
    # Find the paths
    paths=obtain_paths()

    for e in paths:
    
        # Set up grid
        fig = plt.figure(figsize=(15, 10))
        gs = gridspec.GridSpec(2, 3)
        t_0 = 0

        # Find all the files
        files = []
        for (dirpath, dirnames, filenames) in os.walk(e):
            files.extend(filenames)
            break
        
        for f in files:
            path = os.path.join(e, f)
            
            # UPPER GRAPH
            # -------------------------------------------
            # Plot the upper graph showing the lightcurve
            if f.startswith('firstlight_') and f.endswith('.lc'):
            
                # Get the data
                rate, t, dt, n_bins, error, t_0 = read_light_curve(path)
                
                ax1 = fig.add_subplot(gs[0,-2:])
                
                # Plot with a time offset
                ax1.plot(t-t_0, rate, 'r-')
                
                # Graph details
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Rate (s^-1)')
                
                # Text on right hand side of image
                
                # Give the obsid number
                plt.figtext(0.17, 0.9, 'OBSID: ' + e.split('/')[-1], 
                            fontsize=14, fontweight='bold', 
                            horizontalalignment='center')
                            
                # Give the time offset
                plt.figtext(0.17, 0.85, 'Starting Time: ' + str(t_0), 
                            fontsize=14, horizontalalignment='center')
        
            # If a rebinned background file has been found, plot it in the
            # same graph
            elif f.startswith('rebinned_background_') and f.endswith('.dat'):
            
                # Set a normalisation factor so it is visible
                norm_bkg = 10
                
                # Import the data
                bkg_rate, bkg_t, bkg_dt, bkg_n_bins, bkg_error = np.loadtxt(path,dtype=float,unpack=True)
                
                # Plot the data
                ax1.plot(bkg_t-t_0, bkg_rate*norm_bkg, 'b-')
                
                # Add text, giving the normalisation factor
                plt.figtext(0.17, 0.8, 'Normalisation bkg: ' + str(norm_bkg), 
                            fontsize=14, horizontalalignment='center')
                
                
            elif f.startswith('corrected_rate_minus_xray_flare_') and f.endswith('.dat'):
                print f


            elif f.startswith('power_spectrum_') and f.endswith('.dat'):
                
                # POWER SPECTRUM
                # --------------
                # Import power spectrum
                ps, ps_error, freq, freq_error = np.loadtxt(path,dtype=float,
                                                            unpack=True)
                # Plot details
                ax2 = fig.add_subplot(gs[1,:-2])
                ax2.plot(freq, ps, 'r-')
                ax2.set_ylabel('Power')
                ax2.set_xlabel('Frequency (Hz)')
                ax2.set_xscale("log", nonposx='clip')

                # FREQUENCY POWER SPECTRUM
                # ------------------------
                ax3 = fig.add_subplot(gs[1,-2:-1])
                
                bin_means, bin_edges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=25))
                #print len(bin_means), len(bin_edges)
                ax3.step(bin_edges[:-1], bin_means, where='pre', lw=2, label='binned statistic of data')
                
                #ax3.hlines(bin_means, bin_edges[:-1], bin_edges[1:], 
                #           colors='g', lw=5, label='binned statistic of data')
                # If plotting with errorbar
                #ax3.errorbar(freq, ps*freq, xerr=freq_error, 
                #             yerr=(ps*freq_error + freq*ps_error), 
                #             fmt='o', color='r')
                ax3.set_xscale("log", nonposx='clip')
                ax3.set_yscale("log", nonposy='clip')
                ax3.set_ylabel('Frequency*Power')
                ax3.set_xlabel('Frequency (Hz)')
                
                # POWER COLOUR COLOUR
                # -------------------
                pc1, pc2, obsid = np.genfromtxt('./pwr_colours.dat',delimiter=' ',dtype=np.str,unpack=True)
                
                pc1 = [float(i) for i in pc1]
                pc2 = [float(i) for i in pc2]
                
                # Plot details
                ax4 = fig.add_subplot(gs[1,-1:])
                ax4.loglog(pc1, pc2, 'o', c='k', zorder=1)
                ax4.set_xlim([0.03, 101])
                ax4.set_ylim([0.03, 101])
                ax4.set_xlabel('PC1 ([0.25-2.0]/[0.0039-0.031])')
                ax4.set_ylabel('PC2 ([0.031-0.25]/[2.0-16.0])')
                
                # Find the right power colour colour value
                h = np.where(obsid == e.split('/')[-1])[0][0]
                # Add a red dot showing the power colour colour value
                ax4.scatter([pc1[h]],[pc2[h]], c='r', lw=0, s=50, zorder=2)

        print '-----------\n Plotting:', e
        
        fig.tight_layout()
        
        if show:
            plt.show()
        else:
            plt.savefig('./plots/full_' + e.split('/')[-1])
            
        plt.clf()
        
plot_obsid(show=False)
