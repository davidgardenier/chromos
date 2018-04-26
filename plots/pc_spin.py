# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

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

    names = {'4u_1705_m44':'4U 1705-44',
            '4U_0614p09':'4U 0614+09',
            '4U_1636_m53':'4U 1636-53',
            '4U_1702m43':'4U 1702-43',
            '4U_1728_34':'4U 1728-34',
            'aquila_X1':'Aql X-1',
            'cyg_x2':'Cyg X-2',
            'gx_5m1':'GX 5-1',
            'gx_17p2':'GX 17+2',
            'gx_339_d4':'GX 339-4', #BH system
            'gx_340p0':'GX 340+0',
            'gx_349p2':'GX 349+2',
            'HJ1900d1_2455':'HETE J1900.1-2455',
            'H1743m322':'H1743-322',
            'IGR_J00291p5934':'IGR J00291+5934',
            'IGR_J17480m2446':'IGR J17480-2446',
            'IGR_J17498m2921':'IGR J17498-2921',
            'J1701_462':'XTE J1701-462',
            'KS_1731m260':'KS 1731-260',
            'sco_x1':'Sco X-1',
            'sgr_x1':'Sgr X-1',
            'sgr_x2':'Sgr X-2',
            'S_J1756d9m2508':'SWIFT J1756.9-2508',
            'v4634_sgr':'V4634 Sgr',
            'XB_1254_m690':'XB 1254-690',
            'xte_J0929m314':'XTE J0929-314',
            'xte_J1550m564':'XTE J1550-564', #BH system
            'xte_J1751m305':'XTE J1751-305',
            'xte_J1807m294':'XTE J1807-294',
            'xte_J1808_369':'SAX J1808.4-3648',
            'xte_J1814m338':'XTE J1814-338'}



    #From Marieke's thesis
    objects = [#('4u_1705_m44', 'a'),
              ('xte_J1808_369', '401'),
              ('HJ1900d1_2455', '377.3'),
              #('v4634_sgr', 'a'),
              ('4U_1728_34', '364'),
              ('4U_0614p09', '414.7'),
             # ('4U_1702m43', 'a'),
              #('J1701_462', 'z'),
              ('aquila_X1', '550'),
              ('4U_1636_m53', '581.9'),
              ('IGR_J17480m2446', '11')]

    objects = sorted(objects, key=lambda x: x[1])

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                      key=graph.key.key(pos='tr', dist=0.05, textattrs=[text.size.small]))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.08, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol( size=0.1, symbolattrs=[color.gradient.Rainbow])]

    for i, o in enumerate(objects):
        print o[0]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = findbestdata(db)

        x = db.pc1.values
        y = db.pc2.values
        xerror = db.pc1_err.values
        yerror = db.pc2_err.values

        g.plot(graph.data.values(x=x, y=y, dx=xerror, dy=yerror, title=name + ' Hz'), scatterstyle)
        #g.plot(graph.data.values(x=x, y=y, title=name), scatterstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/spin')

if __name__=='__main__':
    plot_allpcs()
