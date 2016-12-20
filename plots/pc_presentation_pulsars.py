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

def findbestdatashifted(db):
    # Apply constraint to the data
    db = db[(db.pc1_shiftedby5.notnull() & db.lt3sigma_shiftedby5==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db

ns=[('4u_1705_m44', '4U 1705-44'),
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
    #('gx_349p2', 'GX 349+2'), #Only 3 points
    ('HJ1900d1_2455', 'HETE J1900.1-2455'),
    ('IGR_J00291p5934', 'IGR J00291+5934'),
    ('IGR_J17480m2446', 'IGR J17480-2446'),
    #('IGR_J17498m2921', 'IGR J17498-2921'), #Only 1 point
    #('IGR_J17511m3057', 'IGR J17511-3057'), #Same as XTE J1751
    ('J1701_462', 'XTE J1701-462'),
    ('KS_1731m260', 'KS 1731-260'),
    ('sco_x1', 'Sco X-1'),
    ('sgr_x1', 'Sgr X-1'),
    ('sgr_x2', 'Sgr X-2'),
    ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
    ('v4634_sgr', 'V4634 Sgr'),
    #('XB_1254_m690', 'XB 1254-690'),
    ('xte_J0929m314', 'XTE J0929-314'),
    #('xte_J1550m564', 'XTE J1550-564'), #BH system
    ('xte_J1751m305', 'XTE J1751-305'),
    #('xte_J1807m294', 'XTE J1807-294'), #Only 4 points
    ('xte_J1808_369', 'SAX J1808.4-3648'),
    ('xte_J1814m338', 'XTE J1814-338')]

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

    x_ns.extend(db.pc1.values)
    y_ns.extend(db.pc2.values)
    xerror_ns.extend(db.pc1_err.values)
    yerror_ns.extend(db.pc2_err.values)

bursters = [('4U_0614p09',414.7),
            ('4U_1636_m53',581.9),
            ('4U_1702m43',330),
            ('4U_1728_34',364),
            ('aquila_X1',550.3),
            ('EXO_0748_676',552.5),
            ('KS_1731m260',524)]

pulsars = [('HJ1900d1_2455',377.3),
            ('IGR_J17480m2446',11),
            ('xte_J1751m305',244.8),
            ('xte_J1807m294',190.6),
            ('xte_J1808_369',401)]

names = {'4u_1705_m44':'4U 1705-44',
        '4U_0614p09':'4U 0614+09',
        '4U_1636_m53':'4U 1636-53',
        '4U_1702m43':'4U 1702-43',
        '4U_1728_34':'4U 1728-34',
        'aquila_X1':'Aql X-1',
        'cir_x1':'Cir X-1', #strange behaviour
        'cyg_x2':'Cyg X-2',
        'EXO_0748_676':'EXO 0748-676', #Strange behaviour
        'gx_5m1':'GX 5-1', #Only 5 points
        'gx_17p2':'GX 17+2', #Only has 4 points
        'gx_339_d4':'GX 339-4', #BH system
        'gx_340p0':'GX 340+0', #Only 5 points
        'gx_349p2':'GX 349+2', #Only 3 points
        'HJ1900d1_2455':'HETE J1900.1-2455',
        'H1743m322':'H1743-322',
        'IGR_J00291p5934':'IGR J00291+5934',
        'IGR_J17480m2446':'IGR J17480-2446',
        'IGR_J17498m2921':'IGR J17498-2921', #Only 1 point
        'IGR_J17511m3057':'IGR J17511-3057', #Same as XTE J1751
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
        'xte_J1807m294':'XTE J1807-294', #Only 4 points
        'xte_J1808_369':'SAX J1808.4-3648',
        'xte_J1814m338':'XTE J1814-338',
        'xte_J2123_m058':'XTE J2123-058'} # No pc points


class empty:

	def __init__(self):
		pass
	def labels(self, ticks):
		for tick in ticks:
			tick.label=""

def plotpcpane():

    # Set up plot details
    c=canvas.canvas()

    xposition=[0.0]
    yposition=[0.0]

    for i in range(len(xposition)):

        if i == 0:
            objs = pulsars
        objs = sorted(objs, reverse=True, key=lambda x: x[1])

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
	                             x=graph.axis.log(min=0.01,max=600,title=xtitle,texter=xtexter,manualticks=myticks),
	                             y=graph.axis.log(min=0.01,max=60,title=ytitle,texter=ytexter),
                                 key=graph.key.key(pos=None,hpos=1.0,vpos=0.5,hinside=0,dist=0.2, textattrs=[text.size.small])))
        scatterstyle= [graph.style.symbol(symbol=graph.style._circlesymbol, size=0.08, symbolattrs=[deco.filled, color.gradient.Rainbow])]

        # Plot Neutron Stars
        grey= color.cmyk(0,0,0,0.5)
        nsstyle = [graph.style.symbol(size=0.05, symbolattrs=[grey])]
        g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron Stars'), nsstyle)

        for o in objs:

            xs = []
            ys = []
            xerrors = []
            yerrors = []

            print o[0]
            name = str(o[-1])
            o = o[0]
            p = path(o)
            db = pd.read_csv(p)
            db = findbestdata(db)

            xs.extend(db.pc1.values)
            ys.extend(db.pc2.values)
            xerrors.extend(db.pc1_err.values)
            yerrors.extend(db.pc2_err.values)

            g.plot(graph.data.values(x=xs, y=ys, dx=xerrors, dy=yerrors, title=name + ' Hz'), scatterstyle)
    # title = huerange.replace('_', '$^[\circ]$-') + '$^[\circ]$'
    # c.text(6.0,yposition[-1]+6.5,title,
    #        [text.halign.center, text.valign.bottom, text.size.Large])

    outputfile = '/scratch/david/master_project/plots/publication/presentation/pc_pulsars'
    c.writePDFfile(outputfile)
    # os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


if __name__=='__main__':
    plotpcpane()
