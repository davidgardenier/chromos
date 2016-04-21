# Quick script to overplot power colour values
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import os
import glob
import pandas as pd


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database.csv'


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


def plot_allpcs():
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    #Name, inclination ('e'dge if <45, 'f'ace if >45)
    objects = [#('4u_1705_m44', 'a'), #Must be rerun
              ('xte_J1808_369', 'a'),
              ('cir_x1', 'z'),
              ('cyg_x2', 'z'),
              #('EXO_0748_676', 'a'),
              ('HJ1900d1_2455', 'a'),
              ('sco_x1', 'z'),
              ('v4634_sgr', 'a'),
              ('4U_1728_34', 'a'),
              ('4U_0614p09', 'a'),
              ('4U_1702m43', 'a'),
              ('J1701_462', 'z'),
              ('aquila_X1', 'a'),
              ('4U_1636_m53', 'a'),
              ('cyg_x2', 'z'),
              ('gx_5m1', 'z'),
              ('gx_340p0', 'z'),
              ('sco_x1', 'z'),
              ('gx_17p2', 'z'),
              ('gx_349p2', 'z')]

    # Set up plot details
    plt.figure(figsize=(10,10))
    #colormap = plt.cm.Paired
    #plt.gca().set_color_cycle([colormap(i) for i in np.linspace(0, 0.9, len(objects))])
    marker = itertools.cycle(('^', '+', '.', 'o', '*'))

    for details in objects:
        o = details[0]
        incl = details[1]

        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x = db.pc1.values
        y = db.pc2.values
        xerror = db.pc1_err.values
        yerror = db.pc2_err.values

        # One big plot
        if incl == 'a':
            colour = 'b'
        elif incl == 'z':
            colour = 'r'
        else:
            colour = 'k'

        plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', c=colour, marker=marker.next(), label=o, linewidth=2)
        # Subplots
        #plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', linewidth=2)

        plt.axis([0.01, 1000, 0.01, 100])
        plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
        plt.xscale('log', nonposx='clip')
        plt.ylabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
        plt.yscale('log', nonposy='clip')
        plt.title('Blue is atoll, red is Z-source')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        #plt.savefig('/scratch/david/master_project/plots/pc_' + o + '.png')
        #plt.gcf().clear()
        #plt.clf()

    plt.show()

if __name__=='__main__':
    plot_allpcs()
