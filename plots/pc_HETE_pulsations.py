# Quick script to overplot power colour values
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
from pyx import *

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
    unitorder = ['us','ms','s']
    for u in unitorder:
        if u in tails:
            indices = [i for i, x in enumerate(tails) if x==u]
            sameunits = [heads[i] for i in indices]
            sortvalues = sorted(sameunits)
            return sortvalues[0]+u


def findbestdataperobsid(df):
    '''Select the data with best mode and resolution'''
    ordering = ['gx1','gx2','event','binned','std2']
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
    import numpy as np
    import itertools

    scos=[('gx_17p2', 'GX 17+2'), #Only has 4 points,
          ('sco_x1', 'Sco X-1'),
          ('gx_349p2', 'GX 349+2')] #Only 3 points

    cygs = [('cyg_x2', 'Cyg X-2'),
          ('gx_5m1', 'GX 5-1'), #Only 5 points
          ('gx_340p0', 'GX 340+0')] #Only 5 points]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=5, max=100, title=r"PC1"),
                      y=graph.axis.log(min=0.1, max=1, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.2))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.15, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(size=0.15, symbolattrs=[color.gradient.Rainbow])]

    x_pulse = []
    y_pulse = []
    xerror_pulse = []
    yerror_pulse = []

    x_nopulse = []
    y_nopulse = []
    xerror_nopulse = []
    yerror_nopulse = []

    p = path('HJ1900d1_2455')
    db = pd.read_csv(p)
    db = findbestdata(db)
    pulse = db.apply(anypulsations, axis=1)

    for i in range(len(pulse)):
        if pulse[i] is True:
            x_pulse.append(db.pc1.values[i])
            y_pulse.append(db.pc2.values[i])
            xerror_pulse.append(db.pc1_err.values[i])
            yerror_pulse.append(db.pc2_err.values[i])
        if pulse[i] is False:
            x_nopulse.append(db.pc1.values[i])
            y_nopulse.append(db.pc2.values[i])
            xerror_nopulse.append(db.pc1_err.values[i])
            yerror_nopulse.append(db.pc2_err.values[i])

    #g.plot(graph.data.values(x=x_pulse, y=y_pulse, title='Pulsation'), scatterstyle)
    g.plot(graph.data.values(x=x_pulse, y=y_pulse, dx=xerror_pulse, dy=yerror_pulse, title='Pulsation'), errstyle)
    #g.plot(graph.data.values(x=x_nopulse, y=y_nopulse, title='Standard'), scatterstyle)
    g.plot(graph.data.values(x=x_nopulse, y=y_nopulse, dx=xerror_nopulse, dy=yerror_nopulse, title='Standard'), errstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/hete_pulsations')

if __name__=='__main__':
    plot_allpcs()
