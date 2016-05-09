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
    import numpy as np
    import itertools

    atolls=[('4u_1705_m44', '4U 1705-44'),
            ('4U_0614p09', '4U 0614+09'),
            ('4U_1636_m53', '4U 1636-53'),
            ('4U_1702m43', '4U 1702-43'),
            ('4U_1728_34', '4U 1728-34'),
            ('aquila_X1', 'Aql X-1'),
            ('HJ1900d1_2455', 'HETE J1900.1-2455'),
            ('sgr_x1', 'Sgr X-1'),
            ('sgr_x2', 'Sgr X-2') #Common Patterns in the Evolution between the Luminous Neutron Star Low-Mass X-ray Binary Subclasses
            ]

    zs = [('cyg_x2', 'Cyg X-2'),
          ('gx_5m1', 'GX 5-1'), #Only 5 points
          ('gx_17p2', 'GX 17+2'), #Only has 4 points,
          ('gx_340p0', 'GX 340+0'), #Only 5 points
          ('gx_349p2', 'GX 349+2'), #Only 3 points
          #('J1701_462', 'XTE J1701-462'), #Transitions between states
          ('sco_x1', 'Sco X-1')]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.2))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.1, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow])]

    x_atolls = []
    y_atolls = []
    xerror_atolls = []
    yerror_atolls = []

    for i, o in enumerate(atolls):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_atolls.extend(db.pc1.values)
        y_atolls.extend(db.pc2.values)
        xerror_atolls.extend(db.pc1_err.values)
        yerror_atolls.extend(db.pc2_err.values)

    # Plot Atolls
    g.plot(graph.data.values(x=x_atolls, y=y_atolls, title='Atoll sources'), scatterstyle)

    #plot Black Holes
    x_z = []
    y_z = []
    xerror_z = []
    yerror_z = []

    for i, o in enumerate(zs):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_z.extend(db.pc1.values)
        y_z.extend(db.pc2.values)
        xerror_z.extend(db.pc1_err.values)
        yerror_z.extend(db.pc2_err.values)

    # Plot Z
    g.plot(graph.data.values(x=x_z, y=y_z, title='Z sources'), scatterstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/atoll_z')

if __name__=='__main__':
    plot_allpcs()