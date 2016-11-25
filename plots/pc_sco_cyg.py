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


def plot_allpcs():
    import numpy as np
    import itertools

    scos=[('sco_x1', 'Sco X-1'),
          ('gx_17p2', 'GX 17+2'), #Only has 4 points
          ('gx_349p2', 'GX 349+2')] #Only 3 points

    cygs = [('cyg_x2', 'Cyg X-2'),
          ('gx_5m1', 'GX 5-1'), #Only 5 points
          ('gx_340p0', 'GX 340+0')] #Only 5 points]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.1))

    #scos = sorted(scos, key=lambda x: x[1])
    #cygs = sorted(cygs, key=lambda x: x[1])

    scatterstyle= [graph.style.symbol(graph.style.symbol.changecross, size=0.15, symbolattrs=[color.rgb.red])]
    for i, o in enumerate(scos):

        x_scos = []
        y_scos = []
        xerror_scos = []
        yerror_scos = []

        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_scos.extend(db.pc1.values)
        y_scos.extend(db.pc2.values)
        xerror_scos.extend(db.pc1_err.values)
        yerror_scos.extend(db.pc2_err.values)

    # Plot Atolls
        g.plot(graph.data.values(x=x_scos, y=y_scos, title=name), scatterstyle)
    #g.plot(graph.data.values(x=x_scos, y=y_scos, dx=xerror_scos, dy=yerror_scos, title='Sco-like Z sources'), errstyle)
    #plot Black Holes


    scatterstyle= [graph.style.symbol(graph.style.symbol.changetriangle, size=0.15, symbolattrs=[color.rgb.blue])]

    for i, o in enumerate(cygs):
        x_cygs = []
        y_cygs = []
        xerror_cygs = []
        yerror_cygs = []

        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_cygs.extend(db.pc1.values)
        y_cygs.extend(db.pc2.values)
        xerror_cygs.extend(db.pc1_err.values)
        yerror_cygs.extend(db.pc2_err.values)

    # Plot Z
        g.plot(graph.data.values(x=x_cygs, y=y_cygs, title=name), scatterstyle)
    #g.plot(graph.data.values(x=x_cygs, y=y_cygs, dx=xerror_cygs, dy=yerror_cygs, title='Cyg-like Z sources'), errstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/sco_cyg')

if __name__=='__main__':
    plot_allpcs()
