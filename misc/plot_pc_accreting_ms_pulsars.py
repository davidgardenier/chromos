# Quick script to overplot power colour values
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import os
import glob
import pandas as pd


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'


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
    for details in objects:
        o = details[0]
        type_obj = details[1]

        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x = db.pc1.values
        y = db.pc2.values
        xerror = db.pc1_err.values
        yerror = db.pc2_err.values

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
