# Quick script to overplot power colour values

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database.csv'


objects = ['aquila_X1', 'gx_339_d4']

colors = ['b', 'r']
q = 0
plt.figure()

for o in objects:

    p = path(o)
    db = pd.read_csv(p)

    constrs = [((db.pc1>3) & (db.pc1<10) & (db.pc2>0.4) & (db.pc2<1)), ((db.pc1>6) & (db.pc1<10) & (db.pc2>0.8) & (db.pc2<11))]

    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.drop_duplicates(['obsids','pc1'])

    x = db.pc1.values
    y = db.pc2.values
    xerror = db.pc1_err.values
    yerror = db.pc2_err.values

    plt.errorbar(x, y, xerr=xerror, yerr=yerror, ls='none', label=o, c=colors[q], marker='o', alpha=0.2)
    db = db[constrs[q]]

    x = db.pc1.values
    y = db.pc2.values
    xerror = db.pc1_err.values
    yerror = db.pc2_err.values
    plt.errorbar(x, y, xerr=xerror, yerr=yerror, ls='none', label='Constraint', c=colors[q], marker='v')

    plt.axis([0.01, 1000, 0.01, 1000])
    plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
    plt.xscale('log', nonposx='clip')
    plt.ylabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
    plt.yscale('log', nonposy='clip')
    plt.title('Power Colours')
    plt.legend()

    q += 1
    df = db.drop_duplicates('obsids')
    for obsid in df.obsids.values:
        print obsid
    print '+'*80

plt.show()
#plt.savefig('/scratch/david/master_project/plots/pc_' + o + '_bach_selection.png')
#plt.clf()
