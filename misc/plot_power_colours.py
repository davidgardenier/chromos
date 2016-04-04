# Quick script to overplot power colour values

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


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


def bestdata(df):
    '''Select the data with best mode and resolution'''
    ordering = ['goodxenon','event','binned','std2']
    for mode in ordering:
        if mode in df.modes.values:
            df = df[df.modes==mode]
            if df.shape[0] > 1:
                bestres = findbestres(df.resolutions.values)
                return df[df.resolutions==bestres].iloc[0]
            else:
                return df.iloc[0]


objects = ['4u_1705_m44',
           'xte_J1808_369',
           'cir_x1',
           'cyg_x2',
           'EXO_0748_676',
           'HJ1900d1_2455',
           'sco_x1',
           '4U_1728_34',
           'J1701_462',
           'aquila_X1',
           'xte_J1808_369']

plt.figure()

for o in objects:

    p = path(o)
    db = pd.read_csv(p)
    print o, db.shape
    print '=======================\n', db.apply(pd.Series.nunique)

    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.groupby('obsids').apply(bestdata)
    print '%d data points for %s' %(len(db),o)
    x = db.pc1.values
    y = db.pc2.values
    xerror = db.pc1_err.values
    yerror = db.pc2_err.values

    plt.errorbar(x, y, xerr=xerror, yerr=yerror, ls='none', label=o)

    plt.axis([0.01, 1000, 0.01, 1000])
    plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
    plt.xscale('log', nonposx='clip')
    plt.ylabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
    plt.yscale('log', nonposy='clip')
    plt.title('Power Colours')
    plt.legend()
    #plt.show()
    plt.savefig('/scratch/david/master_project/plots/pc_' + o + '.png')
    plt.clf()

# plt.show()
