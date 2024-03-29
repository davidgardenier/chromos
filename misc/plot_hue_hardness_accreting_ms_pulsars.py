# Quick script to plot hue vs spectral hardness values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
from math import atan2, degrees, pi, log10, sqrt

def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o +'.csv'


def findbestres(res):
    '''Find the smallest resolution from a list of resolutions'''

    # Split resolutions into values and units
    heads = []
    tails = []
    for s in res:
        unit = s.strip('0123456789')
        num = s[:-len(unit)]
        heads.append(num)
        tails.append(unit)

    # Sort by unit, then by value
    unitorder = ['ms','us','s']
    for u in unitorder:
        if u in tails:
            indices = [i for i, x in enumerate(tails) if x==u]
            sameunits = [heads[i] for i in indices]
            sortvalues = sorted(sameunits)
            return sortvalues[0]+u


def findbestdataperobsid(df):
    '''Select the data with best mode and resolution'''
    ordering = ['gx1','event','binned','std2']
    for mode in ordering:
        if mode in df.modes.values:
            df = df[df.modes==mode]
            if df.shape[0] > 1:
                bestres = findbestres(df.resolutions.values)
                return df[df.resolutions==bestres].iloc[0]
            else:
                return df.iloc[0]


def findbestdata(db):
    # Apply constraint to the data
    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db


def cal_hue(x,y,xerr,yerr):
    '''
    Function to calculate the hue on basis of power colour-ratio values.

    Assuming:
     - errors symmetric along either axis
     - errors uncorrelated with each other
     - errors given relative to a value

    Returns:
     - [tuple] hue, hue_error
    '''
    # Central point
    x0 = 4.51920
    y0 = 0.453724

    x = float(x)
    y = float(y)

    # Angles are defined in log-space
    dx = log10(x) - log10(x0)
    dy = log10(y) - log10(y0)

    # Calculate angle
    rads = atan2(dy,dx)
    rads %= 2*pi
    # Add 135 degrees as the hue angle is defined
    # from the line extending in north-west direction
    degs = -(rads*(180/pi)) + 135
    # Fixing things with minus degrees
    if degs < 0:
        degs = (180 - abs(degs)) + 180

    # Calculate errors with error propagation
    above = (yerr*x*log10(x/x0))**2+(xerr*y*log10(y/y0))**2
    below = (x*y*(log10(x/x0)**2 + log10(y/y0)**2))**2
    radserr = sqrt(above/float(below))
    radserr %= 2*pi
    degserr = radserr*180/pi

    return degs, degserr


def plot_allhues():
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    #Name, type_objination ('e'dge if <45, 'f'ace if >45)
    objects = [('4u_1705_m44', 'x'),
                ('4U_0614p09', 'x'),
                ('4U_1636_m53', 'x'),
                ('4U_1702m43', 'x'),
                ('4U_1728_34', 'x'),
                ('aquila_X1', 'x'),
                ('cir_x1', 'x'),
                ('cyg_x2', 'x'),
                #('EXO_0748_676', 'x'),
                ('gx_3p1', 'x'),
                ('gx_5m1', 'x'),
                ('gx_17p2', 'x'),
                ('gx_339_d4', 'x'),
                ('gx_340p0', 'x'),
                ('gx_349p2', 'x'),
                ('HJ1900d1_2455', 'm'),
                ('IGR_J00291p5934', 'a'),
                ('IGR_J17498m2921', 'a'),
                ('IGR_J17511m3057', 'a'),
                ('J1701_462', 'x'),
                ('KS_1731m260', 'x'),
                ('sco_x1', 'x'),
                ('sgr_x1', 'x'),
                ('sgr_x2', 'x'),
                ('S_J1756d9m2508', 'a'),
                ('v4634_sgr', 'x'),
                ('XB_1254_m690', 'x'),
                ('xte_J0929m314', 'a'),
                ('xte_J1751m305', 'a'),
                ('xte_J1807m294', 'a'),
                ('xte_J1808_369', 'x'),
                ('xte_J1814m338', 'a')]
                #('xte_J2123_m058', 'x')]

    # Set up plot details
    plt.figure(figsize=(10,10))
    colormap = plt.cm.Paired
    colours = [colormap(i) for i in np.linspace(0.1, 0.9, 10)]
    marker = itertools.cycle(('^', '+', '.', 'o', '*'))

    ases = 0
    for w, details in enumerate(objects):
        o = details[0]
        type_obj = details[1]
        print o
        p = path(o)
        db = pd.read_csv(p)

        # Determine pc values
        bestdata = findbestdata(db)

        # Calculate hues
        hues = []
        hues_err = []

        for i in range(len(bestdata.pc1.values)):
            # Determine input parameters
            pc1 = bestdata.pc1.values[i]
            pc2 = bestdata.pc2.values[i]
            pc1err = bestdata.pc1_err.values[i]
            pc2err = bestdata.pc2_err.values[i]
            hue, hue_err = cal_hue(pc1,pc2,pc1err,pc2err)
            hues.append(hue)
            hues_err.append(hue_err)

        # Determine hardness values
        hardness = []
        hardness_err = []
        for obsid, group in bestdata.groupby('obsids'):
            df = db[db.obsids==obsid].dropna(subset=['flux_i3t16_s6p4t9p7_h9p7t16'])
            hardness.append(df.hardness_i3t16_s6p4t9p7_h9p7t16.values[0])
            hardness_err.append(df.hardness_err_i3t16_s6p4t9p7_h9p7t16.values[0])

        # Plot details
        x = hues
        y = hardness
        xerror = hues_err
        yerror = hardness_err

        # One big plot
        if type_obj == 'a':
            colour = colours[ases]
            lbl = o
            ases += 1
            zorders = 10
        else:
            colour = 'darkgrey'
            lbl = None
            zorders = 1

        plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', c=colour,marker=marker.next(), label=lbl, linewidth=2, zorder=zorders)

        plt.axis([0, 360, 0, 2])
        plt.xlabel('Hue')
        #plt.xscale('log', nonposx='clip')
        plt.ylabel('Hardness (9.7-16 keV)/(6.4-9.7 keV)')
        #plt.yscale('log', nonposy='clip')
        plt.title('Blue is atoll, red is Z-source')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        #plt.savefig('/scratch/david/master_project/plots/hue_' + o + '.png', transparent=True)
        #plt.gcf().clear()
        #plt.clf()

    plt.show()

if __name__=='__main__':
    plot_allhues()
