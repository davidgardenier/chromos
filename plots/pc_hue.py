# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
from math import atan2, degrees, pi, log10, sqrt, radians
import matplotlib.pyplot as plt
from collections import defaultdict
from pyx import *

from filter_bursts import filter_bursts

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

    objects=[
            ('4U_0614p09', '4U 0614+09'),
            ('4U_1636_m53', '4U 1636-53'),
            ('4U_1702m43', '4U 1702-43'),
            ('4u_1705_m44', '4U 1705-44'),
            ('4U_1728_34', '4U 1728-34'),
            ('aquila_X1', 'Aql X-1'),
            ('cyg_x2', 'Cyg X-2'),
            ('gx_17p2', 'GX 17+2'),
            ('gx_340p0', 'GX 340+0'),
            #('gx_349p2', 'GX 349+2'), #Only 3 points
            # ('gx_5m1', 'GX 5-1'),  # Only 4 points
            ('HJ1900d1_2455', 'HETE J1900.1-2455'),
            ('IGR_J00291p5934', 'IGR J00291+5934'),
            ('IGR_J17480m2446', 'IGR J17480-2446'),
            #('IGR_J17498m2921', 'IGR J17498-2921'), #Only 1 point
            ('KS_1731m260', 'KS 1731-260'),
            ('xte_J1808_369', 'SAX J1808.4-3648'),
            ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
            ('sco_x1', 'Sco X-1'),
            ('sgr_x1', 'Sgr X-1'),
            ('sgr_x2', 'Sgr X-2'),
            ('v4634_sgr', 'V4634 Sgr'),
            #('XB_1254_m690', 'XB 1254-690'), #Only 1 point
            ('xte_J0929m314', 'XTE J0929-314'),
            ('J1701_462', 'XTE J1701-462'),
            ('xte_J1751m305', 'XTE J1751-305'),
            #('xte_J1807m294', 'XTE J1807-294'), # Only 2 points
            #('xte_J1814m338', 'XTE J1814-338'),  # Only 3 points
            #('gx_339_d4', 'GX 339-4'), # BH system
            #('H1743m322', 'H1743-322'),  # BH system
            #('xte_J1550m564', 'XTE J1550-564'), #BH system
            ]


    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                      y=graph.axis.log(min=0.01, max=100, title=r"PC2"))
    errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.08, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(graph.style.symbol.cross, size=0.1, symbolattrs=[color.gradient.Rainbow])]

    allhues = []
    for i, o in enumerate(objects):
        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        # Determine pc values
        bestdata = findbestdata(db)
        bestdata = filter_bursts(bestdata)

        # Calculate hues
        for i in range(len(bestdata.pc1.values)):
            # Determine input parameters
            obsid = bestdata.obsids.values[i]
            mode = bestdata.modes.values[i]
            pc1 = bestdata.pc1.values[i]
            pc2 = bestdata.pc2.values[i]
            pc1err = bestdata.pc1_err.values[i]
            pc2err = bestdata.pc2_err.values[i]
            hue, hue_err = cal_hue(pc1,pc2,pc1err,pc2err)
            allhues.append((o, obsid, pc1, pc2, pc1err, pc2err, mode, hue, hue_err))

    # Split into bins
    bins = [i for i in range(0,380,20)]
    binnedhues = defaultdict(list)
    for i, e in enumerate(allhues):

        for j, b in enumerate(bins):
            if e[-2] < b:
                binnedhues[str(bins[j-1]) + '_' + str(b)].append(e)
                break

    #Order the bins
    startofbins = []
    for k in binnedhues.keys():
        startofbins.append(int(k.split('_')[0]))
    sortedkeys = [x for (y,x) in sorted(zip(startofbins,binnedhues.keys()))]

    # Plot the bins
    for k in sortedkeys:
        pertype = zip(*binnedhues[k])
        g.plot(graph.data.values(x=pertype[2], y=pertype[3]), scatterstyle)

        #If wanting to print a list of objects & obsids per angle
#        print k
#        print '--------------'
#        for e in binnedhues[k]:
#            print "('%s','%s','%s')" %(e[0], e[1], e[-3])
#        print '=============='
        print "hues['%s'] = [" %k
        for e in binnedhues[k]:
            print "('%s','%s','%s')," %(e[0], e[1], e[-3])
        print ']'

    # Overplot bin details
    for b in [0,20,40,60,80,100,120,140,160]:
        # Add 135 degrees as the hue angle is defined
        # from the line extending in north-west direction
        degs = b + 135
        # Fixing things with minus degrees
        if degs < 0:
            degs = (180 - abs(degs)) + 180
        degs = radians(degs)
        func = 'y(x)=exp(tan('+str(degs)+')*(log(x)-log(4.51920))+log(0.453724))'
        linesty = graph.style.line(lineattrs=[attr.changelist([style.linestyle.dashed])])
        g.plot(graph.data.function(func), styles=[linesty])


        xtext, ytext = g.pos(345, 17)
        g.text(g.width-0.1,ytext, '100$^{\circ}$', [text.halign.boxright])
        xtext, ytext = g.pos(345, 1.8)
        g.text(g.width-0.1,ytext, '120$^{\circ}$', [text.halign.boxright])
        xtext, ytext = g.pos(345, 0.35)
        g.text(g.width-0.1,ytext, '140$^{\circ}$', [text.halign.boxright])
        xtext, ytext = g.pos(345, 0.07)
        g.text(g.width-0.1,ytext, '160$^{\circ}$', [text.halign.boxright])

        xtext, ytext = g.pos(190, 20)
        g.text(xtext,0.1, '180$^{\circ}$', [text.halign.boxleft])
        xtext, ytext = g.pos(28, 1.9)
        g.text(xtext,0.1, '$200^{\circ}$', [text.halign.boxleft])
        xtext, ytext = g.pos(6.5, 0.35)
        g.text(xtext,0.1, '220$^{\circ}$', [text.halign.boxleft])
        xtext, ytext = g.pos(1.9, 0.06)
        g.text(xtext,0.1, '240$^{\circ}$', [text.halign.boxleft])
        xtext, ytext = g.pos(0.45, 0.08)
        g.text(xtext,0.1, '260$^{\circ}$', [text.halign.boxleft])
        xtext, ytext = g.pos(0.04, 0.08)
        g.text(xtext,0.1, '280$^{\circ}$', [text.halign.boxleft])

        xtext, ytext = g.pos(345, 0.09)
        g.text(0.1,ytext, '300$^{\circ}$', [text.halign.boxleft, text.valign.top])
        xtext, ytext = g.pos(345, 0.65)
        g.text(0.1,ytext, '320$^{\circ}$', [text.halign.boxleft, text.valign.top])
        xtext, ytext = g.pos(345, 4)
        g.text(0.1,ytext, '340$^{\circ}$', [text.halign.boxleft, text.valign.top])

        xtext, ytext = g.pos(0.022, 20)
        g.text(xtext,g.height-0.1, '0$^{\circ}$', [text.halign.boxright, text.valign.top])
        xtext, ytext = g.pos(0.37, 1.9)
        g.text(xtext,g.height-0.1, '$20^{\circ}$', [text.halign.boxright, text.valign.top])
        xtext, ytext = g.pos(2.6, 0.35)
        g.text(xtext,g.height-0.1, '40$^{\circ}$', [text.halign.boxright, text.valign.top])
        xtext, ytext = g.pos(18, 0.06)
        g.text(xtext,g.height-0.1, '60$^{\circ}$', [text.halign.boxright, text.valign.top])
        xtext, ytext = g.pos(150, 0.08)
        g.text(xtext,g.height-0.1, '80$^{\circ}$', [text.halign.boxright, text.valign.top])

    g.writePDFfile('/scratch/david/master_project/plots/publication/pc/hue_bins')


if __name__=='__main__':
    plot_allpcs()
