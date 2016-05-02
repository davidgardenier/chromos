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
    db = db[(db.pc1.notnull())]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db


def anypulsations(x):
    pulsations = ['91015-01-01-00',
                    '91015-01-03-00',
                    '91015-01-03-01',
                    '91015-01-03-02',
                    '91015-01-03-03',
                    '91015-01-03-04',
                    '91015-01-03-05',
                    '91015-01-03-06',
                    '91015-01-04-00',
                    '91015-01-04-01',
                    '91015-01-04-03',
                    '91015-01-04-04',
                    '91015-01-04-06',
                    '91015-01-04-07',
                    '91015-01-05-00',
                    '91015-01-05-01',
                    '91015-01-05-02',
                    '91015-01-06-00',
                    '91015-01-06-01',
                    '91015-01-06-02',
                    '91015-01-07-00',
                    '91015-01-07-01',
                    '91059-03-01-00',
                    '91059-03-01-01',
                    '91059-03-01-02',
                    '91059-03-01-03',
                    '91059-03-01-04',
                    '91059-03-02-00',
                    '91059-03-02-01',
                    '91059-03-02-02',
                    '91059-03-02-03',
                    '91059-03-02-04',
                    '91059-03-02-05',
                    '91059-03-03-00',
                    '91059-03-03-01']

    no_pulsations = ['91057-01-01-00',
                    '91057-01-01-01',
                    '91057-01-02-00',
                    '91057-01-05-00',
                    '91057-01-05-01',
                    '91057-01-05-02',
                    '91057-01-05-03',
                    '91057-01-05-04',
                    '91057-01-06-00',
                    '91057-01-06-01',
                    '91057-01-06-02',
                    '91057-01-06-03',
                    '91057-01-06-04',
                    '91057-01-07-00',
                    '91057-01-07-01',
                    '91057-01-07-02',
                    '91057-01-07-03',
                    '91059-03-03-02',
                    '91059-03-03-03',
                    '91059-03-04-00',
                    '91057-01-10-00',
                    '91057-01-10-01',
                    '91057-01-10-02',
                    '91057-01-10-03',
                    '91057-01-11-00',
                    '91057-01-12-00',
                    '91057-01-13-00',
                    '91057-01-14-00',
                    '91057-01-15-00',
                    '91057-01-15-00',
                    '91432-01-01-00']

    if x.obsids in pulsations:
        return True
    if x.obsids in no_pulsations:
        return False

def plot_allpcs():
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    # Set up plot details
    plt.figure(figsize=(10,10))
    o = 'HJ1900d1_2455'
    p = path(o)
    db = pd.read_csv(p)
    db = findbestdata(db)

    pulse = db.apply(anypulsations, axis=1)


    for i in range(len(pulse)):
        if pulse[i] is True:
            colour = 'r'
            z = 10
        if pulse[i] is False:
            colour = 'b'
            z = 1
        # else:
        #     colour = 'k'

        x = db.pc1.values[i]
        y = db.pc2.values[i]
        xerror = db.pc1_err.values[i]
        yerror = db.pc2_err.values[i]

        # One big plot
        plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', c=colour, linewidth=2, zorder=z)
    # Subplots
    #plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', linewidth=2)

    plt.axis([0.01, 1000, 0.01, 100])
    plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
    plt.xscale('log', nonposx='clip')
    plt.ylabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
    plt.yscale('log', nonposy='clip')
    plt.title('Red is pulse, blue if not')

    # In case you want to save each figure individually
    #plt.savefig('/scratch/david/master_project/plots/pc/transparent/' + o + '.png', transparent=True)
    #plt.gcf().clear()
        #plt.clf()

    plt.show()

if __name__=='__main__':
    plot_allpcs()
