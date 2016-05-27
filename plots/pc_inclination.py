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

    objects = [('4u_1705_m44', 'e'),
              ('xte_J1808_369', 'e'),
              ('cir_x1', 'f'),
              ('cyg_x2', 'e'),
              ('EXO_0748_676', 'e'),
              ('HJ1900d1_2455', 'f'),
              ('sco_x1', 'f'),
              ('4U_1728_34', 'f'),
              ('4U_0614p09', 'e'),
              ('J1701_462', 'e'),
              ('aquila_X1', 'e'),
              ('4U_1636_m53', 'e')]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.2))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.08, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow])]

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

    g.plot(graph.data.values(x=x_face, y=y_face, title='Low Incl.'), scatterstyle)
    g.plot(graph.data.values(x=x_edge, y=y_edge, title='High Incl.'), scatterstyle)
    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/inclination')

if __name__=='__main__':
    plot_allpcs()
