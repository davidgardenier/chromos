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

    objects = [('4u_1705_m44', 'f'),
              ('xte_J1808_369', 'f'),
              ('cir_x1', 'e'),
              ('cyg_x2', 'e'),
              #('EXO_0748_676', 'e'),
              ('HJ1900d1_2455', 'f'),
              ('sco_x1', 'f'),
              ('4U_1728_34', 'f'),
              ('4U_0614p09', 'e'),
              ('J1701_462', 'e'),
              ('aquila_X1', 'e'),
              ('4U_1636_m53', 'e')]

    ns = [('4u_1705_m44', '4U 1705-44'),
        ('4U_0614p09', '4U 0614+09'),
        ('4U_1636_m53', '4U 1636-53'),
        ('4U_1702m43', '4U 1702-43'),
        ('4U_1728_34', '4U 1728-34'),
        ('aquila_X1', 'Aql X-1'),
        #('cir_x1', 'Cir X-1'), #strange behaviour
        ('cyg_x2', 'Cyg X-2'),
        #('EXO_0748_676', 'EXO 0748-676'), #Strange behaviour
        ('gx_5m1', 'GX 5-1'), #Only 5 points
        ('gx_17p2', 'GX 17+2'), #Only has 4 points
        #('gx_339_d4', 'GX 339-4'), #BH system
        ('gx_340p0', 'GX 340+0'), #Only 5 points
        ('gx_349p2', 'GX 349+2'), #Only 3 points
        ('HJ1900d1_2455', 'HETE J1900.1-2455'),
        ('IGR_J00291p5934', 'IGR J00291+5934'),
        ('IGR_J17480m2446', 'IGR J17480-2446'),
        ('IGR_J17498m2921', 'IGR J17498-2921'), #Only 1 point
        #('IGR_J17511m3057', 'IGR J17511-3057'), #Same as XTE J1751
        ('J1701_462', 'XTE J1701-462'),
        ('KS_1731m260', 'KS 1731-260'),
        ('sco_x1', 'Sco X-1'),
        ('sgr_x1', 'Sgr X-1'),
        ('sgr_x2', 'Sgr X-2'),
        ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
        ('v4634_sgr', 'V4634 Sgr'),
        ('XB_1254_m690', 'XB 1254-690'),
        ('xte_J0929m314', 'XTE J0929-314'),
        #('xte_J1550m564', 'XTE J1550-564'), #BH system
        ('xte_J1751m305', 'XTE J1751-305'),
        ('xte_J1807m294', 'XTE J1807-294'), #Only 4 points
        ('xte_J1808_369', 'SAX J1808.4-3648'),
        ('xte_J1814m338', 'XTE J1814-338')]

    unknown = [k[0] for k in ns if k[0] not in [o[0] for o in objects]]
    
    
    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.2))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.06, symbolattrs=[color.gradient.ReverseRainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.ReverseRainbow])]

    x_face = []
    y_face = []
    xerror_face = []
    yerror_face = []

    for details in objects:
        o = details[0]
        incl = details[1]
        if incl != 'f':
            continue

        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_face.extend(db.pc1.values)
        y_face.extend(db.pc2.values)
        xerror_face.extend(db.pc1_err.values)
        yerror_face.extend(db.pc2_err.values)

    x_edge = []
    y_edge = []
    xerror_edge = []
    yerror_edge = []

    for details in objects:
        o = details[0]
        incl = details[1]
        if incl != 'e':
            continue
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_edge.extend(db.pc1.values)
        y_edge.extend(db.pc2.values)
        xerror_edge.extend(db.pc1_err.values)
        yerror_edge.extend(db.pc2_err.values)

    x_unknown = []
    y_unknown = []
    xerror_unknown = []
    yerror_unknown = []

    for o in unknown:
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x_unknown.extend(db.pc1.values)
        y_unknown.extend(db.pc2.values)
        xerror_unknown.extend(db.pc1_err.values)
        yerror_unknown.extend(db.pc2_err.values)


    scatterstyle= [graph.style.symbol(graph.style.symbol.changecross, size=0.06, symbolattrs=[color.cmyk.Gray])]
    g.plot(graph.data.values(x=x_unknown, y=y_unknown, title='Unknown'), scatterstyle)
    scatterstyle= [graph.style.symbol(graph.style.symbol.changeplus, size=0.06, symbolattrs=[color.gradient.ReverseRainbow])]
    g.plot(graph.data.values(x=x_edge, y=y_edge, title='High Incl.'), scatterstyle)
    g.plot(graph.data.values(x=x_face, y=y_face, title='Low Incl.'), scatterstyle)
    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/inclination')

if __name__=='__main__':
    plot_allpcs()
