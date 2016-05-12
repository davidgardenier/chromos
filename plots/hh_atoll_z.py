# Quick script to overplot power colour values
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from math import atan2, degrees, pi, log10, sqrt
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

def cal_hue(x,y,xerr,yerr):
    '''
    Function to calculate the hue on basis of power colour-ratio values.

    Assuming:
     - errors symmetric along either axis
     - errors uncorrelated with each other
     - errors given relative to a value

    Returns:
     - [tuple] hue, hue_error
    '''
    # Central point
    x0 = 4.51920
    y0 = 0.453724

    x = float(x)
    y = float(y)

    # Angles are defined in log-space
    dx = log10(x) - log10(x0)
    dy = log10(y) - log10(y0)

    # Calculate angle
    rads = atan2(dy,dx)
    rads %= 2*pi
    # Add 135 degrees as the hue angle is defined
    # from the line extending in north-west direction
    degs = -(rads*(180/pi)) + 135
    # Fixing things with minus degrees
    if degs < 0:
        degs = (180 - abs(degs)) + 180

    # Calculate errors with error propagation
    above = (yerr*x*log10(x/x0))**2+(xerr*y*log10(y/y0))**2
    below = (x*y*(log10(x/x0)**2 + log10(y/y0)**2))**2
    radserr = sqrt(above/float(below))
    radserr %= 2*pi
    degserr = radserr*180/pi

    return degs, degserr

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

    x_atolls = []
    y_atolls = []
    xerror_atolls = []
    yerror_atolls = []

    for i, o in enumerate(atolls):
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        # Determine pc values
        bestdata = findbestdata(db)
        # Calculate hues
        hues = []
        hues_err = []
        for i in range(len(bestdata.pc1.values)):
            # Determine input parameters
            pc1 = bestdata.pc1.values[i]
            pc2 = bestdata.pc2.values[i]
            pc1err = bestdata.pc1_err.values[i]
            pc2err = bestdata.pc2_err.values[i]
            hue, hue_err = cal_hue(pc1,pc2,pc1err,pc2err)
            hues.append(hue)
            hues_err.append(hue_err)

        # Determine hardness values
        hardness = []
        hardness_err = []
        for obsid, group in bestdata.groupby('obsids'):
            df = db[db.obsids==obsid].dropna(subset=['flux_i3t16_s6p4t9p7_h9p7t16'])
            hardness.append(df.hardness_i3t16_s6p4t9p7_h9p7t16.values[0])
            hardness_err.append(df.hardness_err_i3t16_s6p4t9p7_h9p7t16.values[0])

        x_atolls.extend(hues)
        y_atolls.extend(hardness)
        xerror_atolls.extend(hues_err)
        yerror_atolls.extend(hardness_err)

    x_zs = []
    y_zs = []
    xerror_zs = []
    yerror_zs = []

    for i, o in enumerate(zs):
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        # Determine pc values
        bestdata = findbestdata(db)
        # Calculate hues
        hues = []
        hues_err = []
        for i in range(len(bestdata.pc1.values)):
            # Determine input parameters
            pc1 = bestdata.pc1.values[i]
            pc2 = bestdata.pc2.values[i]
            pc1err = bestdata.pc1_err.values[i]
            pc2err = bestdata.pc2_err.values[i]
            hue, hue_err = cal_hue(pc1,pc2,pc1err,pc2err)
            hues.append(hue)
            hues_err.append(hue_err)

        # Determine hardness values
        hardness = []
        hardness_err = []
        for obsid, group in bestdata.groupby('obsids'):
            df = db[db.obsids==obsid].dropna(subset=['flux_i3t16_s6p4t9p7_h9p7t16'])
            hardness.append(df.hardness_i3t16_s6p4t9p7_h9p7t16.values[0])
            hardness_err.append(df.hardness_err_i3t16_s6p4t9p7_h9p7t16.values[0])

        x_zs.extend(hues)
        y_zs.extend(hardness)
        xerror_zs.extend(hues_err)
        yerror_zs.extend(hardness_err)

    # Set up plot details
    g = graph.graphxy(height=9,
                      width=9,
                      x=graph.axis.lin(min=0, max=360, title=r"Hue ($^{\circ}$)"),
                      y=graph.axis.lin(min=0.5, max=1.75, title=r"Hardness (9.7-16 keV)/(6.4-9.7 keV)"),
                      key=graph.key.key(pos='tr', dist=0.1, hdist=0.1, vdist=0.1, keyattrs=[deco.filled([color.rgb.white])]))
    errstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow])]

    g.plot(graph.data.values(x=x_atolls, y=y_atolls, dx=xerror_atolls, dy=yerror_atolls, title='Atoll sources'), errstyle)
    g.plot(graph.data.values(x=x_zs, y=y_zs, dx=xerror_zs, dy=yerror_zs, title='Z sources'), errstyle)
    g.writePDFfile('/scratch/david/master_project/plots/publication/hh/atoll_z')

if __name__=='__main__':
    plot_allpcs()
