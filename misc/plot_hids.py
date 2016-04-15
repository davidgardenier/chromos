# Quick script to overplot power colour values
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

    objects = ['4u_1705_m44',
               'xte_J1808_369',
               'cir_x1',
               'cyg_x2',
               'EXO_0748_676',
               'HJ1900d1_2455',
               'sco_x1',
               'v4634_sgr',
               '4U_1728_34',
               '4U_0614p09',
               '4U_1702m43',
               'J1701_462',
               'aquila_X1',
               '4U_1636_m53',
               'gx_339_d4']

    # Set up plot details
    plt.figure(figsize=(10,10))
    colormap = plt.cm.Paired
    colours = [colormap(i) for i in np.linspace(0.1, 0.9, len(objects))]
    marker = itertools.cycle(('^', 'D', '.', 'o', '*'))

    for i, o in enumerate(objects):

        p = path(o)
        db = pd.read_csv(p)

        x = db.flux.values
        y = db.hardness.values

        # One big plot
        plt.scatter(x, y, color=colours[i], marker=marker.next(), label=o, linewidth=0)

        plt.axis([0, 2e-8, 0, 2.5])
        plt.xlabel('Intensity (Photons*ergs/cm^2/s)')
        plt.ylabel('Hardness (6-13 keV)/(2-6 keV)')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        plt.savefig('/scratch/david/master_project/plots/hid_' + o + '.png', transparent=True)
        plt.gcf().clear()
        #plt.clf()

    #plt.show()

if __name__=='__main__':
    plot_allhids()
