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


def findbestdata(db, o):
    # Apply constraint to the data
    if o != 'IGR_J17480m2446':
        db = db[(db.pc1.notnull() & db.lt3sigma==True)]
        db = db.groupby('obsids').apply(findbestdataperobsid)
    else:
        db = db[(db.pc1.notnull() & db.lt3sigma==True) & ((db['times'].str.contains("2010-10")) | (db['times'].str.contains("2010-11")))]
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

    #Name, inclination ('e'dge if <45, 'f'ace if >45)
    objects = [#('4u_1705_m44', 'a'),
              ('xte_J1808_369', '401'),
             # ('cir_x1', 'z'),
              ('EXO_0748_676', '552.5'),
              ('HJ1900d1_2455', '377.3'),
              #('v4634_sgr', 'a'),
              ('4U_1728_34', '364'),
              ('4U_0614p09', '414.7'),
             # ('4U_1702m43', 'a'),
              #('J1701_462', 'z'),
              ('aquila_X1', '550'),
              ('4U_1636_m53', '581.9'),
              ('IGR_J17480m2446', '11')]

    objects = sorted(objects, key=lambda x: x[1])
    # Set up plot details
    plt.figure(figsize=(10,10))
    colormap = plt.cm.jet
    colours = [colormap(i) for i in np.linspace(0.1, 0.9, len(objects))]
    marker = itertools.cycle(('^', '+', '.', 'o', '*'))

    for w, details in enumerate(objects):
        o = details[0]
        incl = details[1]
        print o
        p = path(o)
        db = pd.read_csv(p)

        # Determine pc values
        bestdata = findbestdata(db, o)

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
        # if incl == 'e':
        #    colour = 'b'
        # elif incl=='f':
        #    colour = 'r'
        # else:
        #     colour='k'

        plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', c=colours[w],marker=marker.next(), label=o + ' ' +incl, linewidth=2)
        # If plotting per inclination
        # plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', c=colour,marker=marker.next(), label=o, linewidth=2)

        plt.axis([0, 360, 0, 2.0])
        plt.xlabel('Hue')
        #plt.xscale('log', nonposx='clip')
        plt.ylabel('Hardness (9.7-16 keV)/(6.4-9.7 keV)')
        #plt.yscale('log', nonposy='clip')
        #plt.title('Blue is edge, red is face-on')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        #plt.savefig('/scratch/david/master_project/plots/hue_hardness/i3t16_s6p4t9p7_h9p7t16/hue_' + o + '.png', transparent=True)
        #plt.gcf().clear()
        #plt.clf()

    plt.show()

if __name__=='__main__':
    plot_allhues()
