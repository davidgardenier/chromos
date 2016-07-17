# Script to plot multiple graphs per obsid
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import pandas as pd
import numpy as np
from matplotlib import use as mpluse
mpluse('agg') # Prevents errors when running in multiple screens
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.stats import binned_statistic
from plot_power_colours import findbestdataperobsid, findbestdata

class Plots:
    '''
    Class to determine setup for different plots
    '''

    def __init__(self, db, obj):

        # Set up grid
        self.fig = plt.figure(figsize=(15, 10))
        self.gs = gridspec.GridSpec(2, 3)

        self.db = db
        self.df = findbestdataperobsid(db)
        self.obj = obj
        self.lc = False
        self.ps = False
        self.sp = False


    def lightcurve(self):
        '''Plot a lightcurve'''

        # Import lightcurve
        import sys
        sys.path.insert(0, '/scratch/david/master_project/scripts/subscripts')
        from correct_for_background import read_light_curve as readlc
        try:
            rate, t, dt, n_bins, error = readlc(self.df.lightcurves)
        except IOError:
            print 'No lightcurve file found'
            return

        # Plot details
        ax1 = self.fig.add_subplot(self.gs[1,-3])
        ax1.plot(t, rate, 'b-', markevery=20)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Rate (s^-1)')
        ax1.set_xlim(t[0],t[-1])
        ax1.set_ylim(0,20000)

        # Plot a shaded area around detected xray flares
        if 'flare_times' in self.df:
            if pd.notnull(self.df.flare_times):
                nflares = self.df.flare_times.split(',')
                for nf in nflares:
                    flare = [float(f.strip("'")) for f in nf.split('-')]
                    ax1.axvspan(flare[0], flare[1], alpha=0.5, color='red')

        # Plot a shaded area whether pcu changes have been detected
        if pd.notnull(self.df.times_pcu):
            with open(self.df.times_pcu) as txt:
                lines = [l.strip() for l in txt.readlines()]

            times = [t[0]]
            for l in lines:
                times.extend(l.split(' '))

            for p in zip(times[0::2], times[1::2]):
                ax1.axvspan(p[0], p[1], alpha=0.5, color='green')

        self.lc = True


    def power_spectrum(self):
        '''Plot a power spectrum in v*vP(v)'''

        # Check whether it's worth running through plotting commands for ps's
        if (not self.lc or pd.isnull(self.df.power_spectra)):
            print 'No power spectrum'
            return

        # Import data
        try:
            all_data = np.loadtxt(self.df.power_spectra,dtype=float)
            inverted_data = np.transpose(all_data)
        except IOError:
            print 'No power spectrum'
            return

        # Give the columns their names
        ps = inverted_data[0]
        ps_error = inverted_data[1]
        freq = inverted_data[2]
        freq_error = inverted_data[3]
        ps_squared = inverted_data[4]
        num_seg = inverted_data[5][0]

        # Plot details
        ax2 = self.fig.add_subplot(self.gs[1,-2:-1])
        bin_means, bin_edges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=50))
        ax2.step(bin_edges[:-1], bin_means, where='pre', lw=2)

        # If plotting with errorbar
        # ax2.errorbar(freq, ps*freq, xerr=freq_error,
        #              yerr=(ps*freq_error + freq*ps_error),
        #              fmt='o', color='b')

        ax2.set_xscale('log', nonposx='clip')
        ax2.set_yscale('log', nonposy='clip')
        ax2.set_xlim([10e-3, 10e2])
        ax2.set_ylim([10e-7, 2])
        ax2.set_ylabel('Freq*Power (rms/mean)^2')
        ax2.set_xlabel('Frequency (Hz)')

        self.ps = True


    def power_colours(self):
        '''Plot power colour value against power colour object'''

        # Note this are only pc's with errors < 3sigma
        allpcs = pd.read_csv('/scratch/david/master_project/' + self.obj +'/info/power_colours.csv')

        # Plot details
        ax3 = self.fig.add_subplot(self.gs[1,-1:])
        ax3.set_xlim([0.01, 1000])
        ax3.set_ylim([0.01, 100])
        ax3.set_xscale('log', nonposx='clip')
        ax3.set_yscale('log', nonposy='clip')
        ax3.set_xlabel('PC1 (C/A [0.25-2.0]/[0.0039-0.031])')
        ax3.set_ylabel('PC2 (B/D [0.031-0.25]/[2.0-16.0])')

        ax3.scatter(allpcs.pc1, allpcs.pc2, marker='x')

        if not self.ps:
            return

        # Show whether constrainted to three sigma (red=yes, black=no)
        if self.df.lt3sigma is True:
            clr = 'r'
        else:
            clr = 'k'

        ax3.errorbar(self.df.pc1,
                    self.df.pc2,
                    xerr=self.df.pc1_err,
                    yerr=self.df.pc2_err,
                    c=clr,
                    marker='^',
                    lw=2,
                    zorder=2)


    def spectrum(self):
        '''Plot the spectrum of the object'''
        eufspec = self.df.paths_obsid + 'eufspec.dat'
        try:
            all_data = np.loadtxt(eufspec,dtype=float)
        except IOError:
            return
        energy, energy_err, energyflux, energyflux_err, model = np.transpose(all_data)

        ax4 = self.fig.add_subplot(self.gs[0,-2:-1])
        ax4.set_xlabel('Energy (keV)')
        ax4.set_xscale('log', nonposx='clip')
        ax4.set_ylabel('Energy*Flux (keV*Photons/cm^2/s)')
        ax4.set_xlim(3,19)
        #ax4.set_ylim(0,0.8)
        ax4.step(energy,energyflux,where='mid', lw=2)


    def hardness_intensity(self):
        '''Plot a hardness intensity diagram'''

        # Plot details
        ax5 = self.fig.add_subplot(self.gs[0,-1])
        ax5.set_ylabel('Hardness (9.7-16 keV)/(6.4-9.7 keV)')
        ax5.set_ylim(0,2.0)
        ax5.set_xlabel('Intensity (Photons*ergs/cm^2/s)')
        ax5.set_xscale('log', nonposx='clip')
        ax5.set_xlim(1e-12,1e-6)
        # Plot general scatter
        allhi = pd.read_csv('/scratch/david/master_project/' + self.obj +'/info/hi.csv')
        ax5.scatter(allhi.flux_i3t16_s6p4t9p7_h9p7t16,allhi.hardness_i3t16_s6p4t9p7_h9p7t16, marker='.', edgecolors='none')

        # Check if hardness intensity value available
        sdf = self.db.dropna(subset=['flux_i3t16_s6p4t9p7_h9p7t16'])
        if len(sdf) < 1:
            return
        # Plot position for this obsid on hid
        ax5.scatter(sdf.flux_i3t16_s6p4t9p7_h9p7t16,
                    sdf.hardness_i3t16_s6p4t9p7_h9p7t16,
                    c='r',
                    marker='^',
                    lw=0,
                    s=50,
                    zorder=2)


    def tidy(self):
        '''Set general plotting details regardless of which plot has been drawn'''

        self.fig.canvas.set_window_title(str(self.df.obsids))

        plt.figtext(0.17, 0.9, str(self.df.obsids),
                                fontsize=14, fontweight='bold',
                                horizontalalignment='center')

        plt.figtext(0.17, 0.8, str(self.df.modes) + ' ' + self.df.resolutions,
                    fontsize=14, horizontalalignment='center')

        plt.figtext(0.17, 0.85, str(self.df.times),
                    fontsize=14, horizontalalignment='center')

        self.fig.tight_layout()



def plot_per_obsid(db, obj):
    '''
    Function to plot several graphs for an obsid within a single figure
    '''

    # First get a file with the best contrained power colours
    df = findbestdata(db)
    c = ['pc1','pc1_err','pc2','pc2_err']
    df.to_csv('/scratch/david/master_project/' + obj + '/info/power_colours.csv', cols = c)
    # Then a file with all the fluxes
    df = db.dropna(subset=['flux_i3t16_s6p4t9p7_h9p7t16'])
    c = ['flux_i3t16_s6p4t9p7_h9p7t16','flux_err_i3t16_s6p4t9p7_h9p7t16','hardness_i3t16_s6p4t9p7_h9p7t16','hardness_err_i3t16_s6p4t9p7_h9p7t16']
    df.to_csv('/scratch/david/master_project/' + obj + '/info/hi.csv', cols = c)

    # Create folder to place plots
    if not os.path.exists('/scratch/david/master_project/' + obj + '/info/plots/'):
        os.makedirs('/scratch/david/master_project/' + obj + '/info/plots/')

    db = db.drop_duplicates('lightcurves')
    for obsid, group in db.groupby('obsids'):
            if len(group.pc1.dropna())==0:
                continue

            print obsid
            plot = Plots(group, obj)
            plot.lightcurve()
            plot.power_spectrum()
            plot.power_colours()
            plot.spectrum()
            plot.hardness_intensity()
            plot.tidy()
            #plt.show()
            plt.savefig('/scratch/david/master_project/' + obj + '/info/plots/' + obsid)


if __name__=='__main__':

    objects = ['sco_x1']
    #obj = raw_input('Object name: ')
   # objects = [obj]
    import pandas as pd
    import os

    for o in objects:
        print o, '\n======================'
        p = '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'
        db = pd.read_csv(p)

        plot_per_obsid(db, o)
