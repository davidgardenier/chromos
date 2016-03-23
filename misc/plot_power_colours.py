# Quick script to overplot power colour values

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database.csv'


objects = ['aquila_X1', '4u_1705_m44']

plt.figure()

for o in objects:

    p = path(o)
    db = pd.read_csv(p)
    db = db[(db.modes!='std2')]
    print o, db.shape
    print '=======================\n', db.apply(pd.Series.nunique)
    print db.rsp
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
plt.show()
