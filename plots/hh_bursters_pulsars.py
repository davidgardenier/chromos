# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016
# Add filter bursts & update object lists
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

def findbestdatashifted(db):
    # Apply constraint to the data
    db = db[(db.pc1_shiftedby5.notnull() & db.lt3sigma_shiftedby5==True)]
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

ns=[
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
    #('H1743m322':'H1743-322'),  # BH system
    #('xte_J1550m564', 'XTE J1550-564'), #BH system
    ]

x_ns = []
y_ns = []
xerror_ns = []
yerror_ns = []

for i, o in enumerate(ns):
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

    # Plot details
    index_to_del = []
    for ih, h in enumerate(hues_err):
        if h > 30:
            index_to_del.append(ih)
    hues = [i for j, i in enumerate(hues) if j not in index_to_del]
    hues_err = [i for j, i in enumerate(hues_err) if j not in index_to_del]
    hardness = [i for j, i in enumerate(hardness) if j not in index_to_del]
    hardness_err = [i for j, i in enumerate(hardness_err) if j not in index_to_del]

    x_ns.extend(hues)
    y_ns.extend(hardness)
    xerror_ns.extend(hues_err)
    yerror_ns.extend(hardness_err)

bursters = [('4U_0614p09',414.7),
            ('4U_1636_m53',581.9),
            ('4U_1702m43',330),
            ('4U_1728_34',364),
            ('aquila_X1',550.3),
            ('KS_1731m260',524),
            ('S_J1756d9m2508', 182),
            ('xte_J0929m314', 185),
            ('xte_J1751m305', 435)]

pulsars = [('HJ1900d1_2455',377.3),
            ('IGR_J17480m2446',11),
            #('IGR_J17498m2921', 401),
            ('xte_J1751m305',244.8),
            ('xte_J1807m294',190.6),
            ('xte_J1814m338', 314),
            ('xte_J1808_369',401)]

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


class empty:

	def __init__(self):
		pass
	def labels(self, ticks):
		for tick in ticks:
			tick.label=""

def plotpcpane():

    # Set up plot details
    c=canvas.canvas()

    xposition=[0.0,6.0]
    yposition=[0.0,0.0]

    for z in range(len(xposition)):

        if z == 0:
            objs = bursters
        if z == 1:
            objs = pulsars
        objs = sorted(objs, key=lambda x: x[1])

        myticks = []
        if yposition[z]!=0.0:
            xtitle = ""
            xtexter=empty()
        else:
            xtitle = "Hue ($^{\circ}$)"
            xtexter=graph.axis.texter.mixed()
        if xposition[z]!=0.0:
            ytitle = ""
            ytexter=empty()
        else:
            ytitle="Hardness"
            ytexter=graph.axis.texter.mixed()

        g=c.insert(graph.graphxy(width=6.0,
                                 height=6.0,
                                 xpos=xposition[z],
                                 ypos=yposition[z],
                                 x=graph.axis.lin(min=0, max=360,title=xtitle,texter=xtexter,manualticks=myticks),
                                 y=graph.axis.lin(min=0.5, max=1.75,title=ytitle,texter=ytexter),
                                 key=graph.key.key(pos='bl', dist=0.1, hdist=0.1, vdist=0.1, keyattrs=[deco.filled([color.rgb.white])], textattrs=[text.size.tiny])))

        scatterstyle= [graph.style.symbol( size=0.1, symbolattrs=[color.gradient.Rainbow])]

        # Plot Neutron Stars
        grey= color.cmyk(0,0,0,0.5)
        nsstyle = [graph.style.symbol(size=0.1, symbolattrs=[grey])]
        g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron stars'), nsstyle)

        for o in objs:
            name = str(o[-1])
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

            # Plot details
            index_to_del = []
            for ih, h in enumerate(hues_err):
                if h > 30:
                    index_to_del.append(ih)
            hues = [i for j, i in enumerate(hues) if j not in index_to_del]
            hues_err = [i for j, i in enumerate(hues_err) if j not in index_to_del]
            hardness = [i for j, i in enumerate(hardness) if j not in index_to_del]
            hardness_err = [i for j, i in enumerate(hardness_err) if j not in index_to_del]

            g.plot(graph.data.values(x=hues, dx=hues_err, y=hardness, dy=hardness_err, title=name + ' Hz'), scatterstyle)
    # title = huerange.replace('_', '$^[\circ]$-') + '$^[\circ]$'
    # c.text(6.0,yposition[-1]+6.5,title,
    #        [text.halign.center, text.valign.bottom, text.size.Large])

    outputfile = '/scratch/david/master_project/plots/publication/hh/bursters_pulsars'
    c.writePDFfile(outputfile)
    # os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


if __name__=='__main__':
    plotpcpane()
