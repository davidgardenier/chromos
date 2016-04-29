# Quick script to plot hardness intensity diagrams
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import os
import glob
import pandas as pd


def path(o):
    return '/scratch/david/master_project/' + o + '/info/hi.csv'


def plot_allhids():
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    objects = [('4u_1705_m44', 'e'),
              ('xte_J1808_369', 'e'),
              ('cir_x1', 'f'),
              #('cyg_x2', 'e'),
              ('EXO_0748_676', 'e'),
              ('HJ1900d1_2455', 'f'),
              ('sco_x1', 'f'),
              ('v4634_sgr', 'x'),
              ('4U_1728_34', 'f'),
              ('4U_0614p09', 'e'),
              ('4U_1702m43', 'x'),
              ('J1701_462', 'e'),
              ('aquila_X1', 'e'),
              ('4U_1636_m53', 'e'),
              ('gx_339_d4', 'x'),
              ('gx_5m1', 'x'),
              ('gx_340p0', 'x'),
              ('gx_17p2', 'x'),
              ('gx_349p2', 'x')]

    # Set up plot details
    plt.figure(figsize=(10,10))
    colormap = plt.cm.Paired
    colours = [colormap(i) for i in np.linspace(0.1, 0.9, len(objects))]
    marker = itertools.cycle(('^', 'D', '.', 'o', '*'))

    for i, o in enumerate(objects):
        o = o[0]
        print o

        p = path(o)
        db = pd.read_csv(p)

        x = db.flux_i3t16_s6p4t9p7_h9p7t16.values
        y = db.hardness_i3t16_s6p4t9p7_h9p7t16.values

        # One big plot
        plt.scatter(x, y, color=colours[i], marker=marker.next(), label=o, linewidth=0)

        plt.axis([1e-13, 1e-7, 0, 2.5])
        plt.ylabel('Hardness (9.7-16 keV)/(6.4-9.7 keV)')
        plt.xlabel('Intensity (Photons*ergs/cm^2/s)')
        plt.xscale('log', nonposx='clip')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        plt.savefig('/scratch/david/master_project/plots/hardness_intensity/' + o + '.png', transparent=True)
        plt.gcf().clear()
        #plt.clf()

    #plt.show()

if __name__=='__main__':
    plot_allhids()
