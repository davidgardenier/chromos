# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
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

def findbestdatashifted(db):
    # Apply constraint to the data
    db = db[(db.pc1_s4.notnull() & db.lt3sigma_s4==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db

ns=[
    ('4U_0614p09', '4U 0614+09'),
    #('4U_1636_m53', '4U 1636-53'),  # Only 2 points
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


x_ns = []
y_ns = []
xerror_ns = []
yerror_ns = []

for i, o in enumerate(ns):
    name = o[-1]
    o = o[0]
    p = path(o)
    db = pd.read_csv(p)
    db = findbestdata(db)
    db = filter_bursts(db)

    x_ns.extend(db.pc1.values)
    y_ns.extend(db.pc2.values)
    xerror_ns.extend(db.pc1_err.values)
    yerror_ns.extend(db.pc2_err.values)

bhs = [('gx_339_d4', 'GX 339-4'), ('H1743m322','H1743-322'), ('xte_J1550m564', 'XTE J1550-564')]

x_bh = []
y_bh = []
xerror_bh = []
yerror_bh = []

for i, o in enumerate(bhs):
    name = o[-1]
    o = o[0]
    p = path(o)
    db = pd.read_csv(p)
    db = findbestdata(db)
    db = filter_bursts(db)

    x_bh.extend(db.pc1.values)
    y_bh.extend(db.pc2.values)
    xerror_bh.extend(db.pc1_err.values)
    yerror_bh.extend(db.pc2_err.values)

x_shiftedns = []
y_shiftedns = []
xerror_shiftedns = []
yerror_shiftedns = []

for i, o in enumerate(ns):
    o = o[0]
    p = path(o)
    db = pd.read_csv(p)
    try:
        db = findbestdatashifted(db)
        db = filter_bursts(db)
        if 'pc1_s4' not in db:
            print 'FAILED: %s' %o
            continue
    except:
        print 'FAILED: %s' %o
        continue
    x_shiftedns.extend(db.pc1_s4.values)
    y_shiftedns.extend(db.pc2_s4.values)
    xerror_shiftedns.extend(db.pc1_err_s4.values)
    yerror_shiftedns.extend(db.pc2_err_s4.values)

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

    for i in range(len(xposition)):

        # p = path(obj)
        # db = pd.read_csv(p)
        # db = findbestdata(db)
        #
        # x = db.pc1.values
        # y = db.pc2.values
        # xerror = db.pc1_err.values
        # yerror = db.pc2_err.values
        #
        # values = graph.data.values(x=x, y=y, dx=xerror, dy=yerror)

        myticks = []
    	if yposition[i]!=0.0:
            xtitle = ""
            xtexter=empty()
    	else:
            xtitle = "PC1"
            xtexter=graph.axis.texter.mixed()
    	if xposition[i]!=0.0:
            ytitle = ""
            ytexter=empty()
    	else:
            ytitle="PC2"
            ytexter=graph.axis.texter.mixed()

    	g=c.insert(graph.graphxy(width=6.0,
                                 height=6.0,
                                 xpos=xposition[i],
                                 ypos=yposition[i],
	                             x=graph.axis.log(min=0.01,max=400,title=xtitle,texter=xtexter,manualticks=myticks),
	                             y=graph.axis.log(min=0.01,max=30,title=ytitle,texter=ytexter)))

        # Plot Neutron Stars
        grey= color.cmyk(0,0,0,0.5)
        nsstyle = [graph.style.symbol(symbol=graph.style._circlesymbol, size=0.035, symbolattrs=[deco.filled, color.rgb.red])]
        bhstyle = [graph.style.symbol(size=0.08, symbolattrs=[grey])]
        if i==0:
            g.plot(graph.data.values(x=x_bh, y=y_bh, title='Black Holes'), bhstyle)
            g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron Stars'), nsstyle)
            xtext, ytext = g.pos(200, 16)
            g.text(xtext,ytext, 'Normal PCs', [text.halign.boxright, text.valign.top])
        nsstyle = [graph.style.symbol(symbol=graph.style._circlesymbol, size=0.035, symbolattrs=[deco.filled, color.rgb.blue])]
        if i==1:
            g.plot(graph.data.values(x=x_bh, y=y_bh, title='Black Holes'), bhstyle)
            g.plot(graph.data.values(x=x_shiftedns, y=y_shiftedns, title='Neutron Stars'), nsstyle)
            xtext, ytext = g.pos(200, 16)
            g.text(xtext,ytext, 'Shifted PCs', [text.halign.boxright, text.valign.top])
    # title = huerange.replace('_', '$^{\circ}$-') + '$^{\circ}$'
    # c.text(6.0,yposition[-1]+6.5,title,
    #        [text.halign.center, text.valign.bottom, text.size.Large])

    outputfile = '/scratch/david/master_project/plots/publication/pc/shiftedpc'
    c.writePDFfile(outputfile)
    # os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


if __name__=='__main__':
    plotpcpane()
