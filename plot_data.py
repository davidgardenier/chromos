import json
import os
import matplotlib.pyplot as plt
from scipy.stats import binned_statistic
from matplotlib import gridspec
import fitsio
import numpy as np

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True

os.chdir(PATH)

with open('./info_on_files.json', 'r') as info:
    d = json.load(info)

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


def plot_obsid(show=False):
    '''
    Function to plot the light curve, power spectrum, freq*power spectrum
    and the placing on the power colour-colour diagram per obsid

    Arguments:
     - show: if True, shows the graphs and doesn't save them.
             if False, does not show the graphs, but does save them.
    '''
    # Let the user know what's going to happen
    purpose = 'Plotting light curves, power spectra and power colour**2 diagram'
    print purpose + '\n' + '='*len(purpose)

    # Set up grid
    fig = plt.figure(figsize=(15, 10))
    gs = gridspec.GridSpec(2, 3)
    t_0 = 0

    for obsid in d:
        for mode in d[obsid].keys():
            plot = False
            if 'path_lc' in d[obsid][mode].keys():
                for path in d[obsid][mode]['path_lc']:

                    try:
                        # Get the data
                        rate, t, dt, n_bins, error, t_0 = read_light_curve(path)
                    except IOError:
                        print obsid, mode, 'File not present'
                        continue

                    ax1 = fig.add_subplot(gs[0,-2:])

                    # Plot with a time offset
                    ax1.plot(t-t_0, rate, 'r-')

                    # Graph details
                    ax1.set_xlabel('Time (s)')
                    ax1.set_ylabel('Rate (s^-1)')

                    # Text on right hand side of image

                    # Give the obsid number
                    plt.figtext(0.17, 0.9, 'Obsid: ' + str(obsid),
                                fontsize=14, fontweight='bold',
                                horizontalalignment='center')

                    # Give the mode
                    res = path.split('_')[-1].split('.')[0]
                    plt.figtext(0.17, 0.8, 'Mode/Resolution: '+ str(mode) + res,
                                fontsize=14, horizontalalignment='center')

                    # Give the time offset
                    plt.figtext(0.17, 0.85, 'Starting Time: ' + str(t_0),
                                fontsize=14, horizontalalignment='center')

                    plot = True

            if 'path_ps' in d[obsid][mode].keys():

                for path in d[obsid][mode]['path_ps']:
                    # POWER SPECTRUM
                    # --------------
                    # Import power spectrum
                    try:
                        ps, ps_error, freq, freq_error, _ , _ = np.loadtxt(path,dtype=float,
                                                                unpack=True)
                    except IOError:
                        print obsid, mode, 'PS file not present'
                        continue

                    res = path.split('_')[-1].split('.')[0]

                    # Plot details
                    ax2 = fig.add_subplot(gs[1,:-2])

                    bin_means, bin_edges, binnumber = binned_statistic(freq, ps, bins=np.logspace(-3,2, num=25))
                    ax2.step(bin_edges[:-1], bin_means, where='pre', lw=2)

                    # If plotting direct power spectrum
                    #ax2.plot(freq, ps, 'r-')

                    ax2.set_ylabel('Power')
                    ax2.set_xlabel('Frequency (Hz)')
                    ax2.set_xscale('log', nonposx='clip')

                    # FREQUENCY POWER SPECTRUM
                    # ------------------------
                    ax3 = fig.add_subplot(gs[1,-2:-1])

                    bin_means, bin_edges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=25))

                    ax3.step(bin_edges[:-1], bin_means, where='pre', lw=2)

                    # If plotting with errorbar
                    #ax3.errorbar(freq, ps*freq, xerr=freq_error,
                    #             yerr=(ps*freq_error + freq*ps_error),
                    #             fmt='o', color='r')

                    ax3.set_xscale('log', nonposx='clip')
                    ax3.set_yscale('log', nonposy='clip')
                    ax3.set_ylabel('Frequency*Power')
                    ax3.set_xlabel('Frequency (Hz)')

                    # POWER COLOUR COLOUR
                    # -------------------
                    pc1, pc2, obs, m, const = np.genfromtxt('./pwr_colours.dat',delimiter=' ',dtype=np.str,unpack=True)

                    pc1 = [float(i) for i in pc1]
                    pc2 = [float(i) for i in pc2]

                    # Plot details
                    ax4 = fig.add_subplot(gs[1,-1:])

                    for i in range(len(pc1)):
                        if const[i] == 'True':
                            colour = 'b'
                        else:
                            colour = 'k'
                        ax4.loglog(pc1[i], pc2[i], 'o', c=colour, zorder=1)

                    ax4.set_xlim([0.01, 1000])
                    ax4.set_ylim([0.01, 1000])
                    ax4.set_xlabel('PC1 ([0.25-2.0]/[0.0039-0.031])')
                    ax4.set_ylabel('PC2 ([0.031-0.25]/[2.0-16.0])')

                    # Find the right power colour colour value
                    h = np.where(obs == obsid)[0]
                    print '    ', obsid
                    if len(h) > 1:
                        for v in h:
                            if mode == m[v]:
                                h = v
                                break
                            else:
                                continue

                    # Add a red dot showing the power colour colour value
                    ax4.scatter([pc1[h]],[pc2[h]], c='r', lw=0, s=50, zorder=2)

                    plot = True

            if plot:
                if show:
                    plt.show()
                    plt.clf()
                else:
                    filename = str(obsid) + '_' + str(mode) + '_' + str(res)
                    plt.savefig('./../plots/full_' + filename)
                    plt.clf()

plot_obsid()
