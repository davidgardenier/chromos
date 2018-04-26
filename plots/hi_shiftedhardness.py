# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from pyx import *


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'

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
    # ('gx_5m1', 'GX 5-1'), Only 4 points
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
x_shifted = []
y_shifted = []

for i, o in enumerate(ns):
    name = o[-1]
    o = o[0]
    p = path(o)
    db = pd.read_csv(p)
    db = db[np.isfinite(db['flux_i3t16_s6p4t9p7_h9p7t16'])]
    x = db.flux_i3t16_s6p4t9p7_h9p7t16.values
    y = db.hardness_i3t16_s6p4t9p7_h9p7t16.values
    x_ns.extend(x)
    y_ns.extend(y)

    db = pd.read_csv(p)
    db = db[np.isfinite(db['flux_i2t20_s2t6_h9t20'])]
    x = db.flux_i2t20_s2t6_h9t20.values
    y = db.hardness_i2t20_s2t6_h9t20.values
    x_shifted.extend(x)
    y_shifted.extend(y)

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

    for i in range(len(xposition)):

        myticks = [graph.axis.tick.tick(1e-12, label=" ", labelattrs=[text.mathmode]),
                   graph.axis.tick.tick(1e-10, label=" ", labelattrs=[text.mathmode]),
                   graph.axis.tick.tick(1e-8, label=" ", labelattrs=[text.mathmode]),
                   graph.axis.tick.tick(1e-6, label=" ", labelattrs=[text.mathmode])]

    	if yposition[i]!=0.0:
            xtitle = ""
            xtexter=empty()
    	else:
            xtitle = "Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"
            xtexter=graph.axis.texter.mixed()
    	if xposition[i]!=0.0:
            ytitle = ""
            ytexter=empty()
    	else:
            ytitle="Hardness"
            ytexter=graph.axis.texter.mixed()

        if yposition[i]==0 and xposition[i]==0:
            xtitle = r"\scriptsize{Intensity [3-16 keV] (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$})"
            xtexter=graph.axis.texter.mixed()
        if yposition[i]==0 and xposition[i]==6:
            xtitle = r"\scriptsize{Intensity [2-20 keV] (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$})"
            xtexter=graph.axis.texter.mixed()

    	g=c.insert(graph.graphxy(width=6.0,
                                 height=6.0,
                                 xpos=xposition[i],
                                 ypos=yposition[i],
	                             x=graph.axis.log(min=1e-12,max=1e-6,title=xtitle,texter=xtexter,manualticks=myticks),
	                             y=graph.axis.lin(min=0.0,max=2.75,title=ytitle,texter=ytexter)))

        # Plot Neutron Stars
        grey= color.cmyk(0,0,0,0.5)
        nsstyle = [graph.style.symbol(size=0.1, symbolattrs=[color.rgb.red])]
        if i==0:
            g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron Stars'), nsstyle)
            xtext, ytext = g.pos(6e-7, 2.6)
            g.text(xtext,ytext, '[9.7-16.0 keV]/[6.4-9.7 keV]', [text.halign.boxright, text.valign.top])
        nsstyle = [graph.style.symbol(size=0.1, symbolattrs=[color.rgb.blue])]
        if i==1:
            g.plot(graph.data.values(x=x_shifted, y=y_shifted, title='Neutron Stars'), nsstyle)
            xtext, ytext = g.pos(6e-7, 2.6)
            g.text(xtext,ytext, '[9.0-20.0 keV]/[2.0-9.0 keV]', [text.halign.boxright, text.valign.top])
    # title = huerange.replace('_', '$^{\circ}$-') + '$^{\circ}$'
    # c.text(6.0,yposition[-1]+6.5,title,
    #        [text.halign.center, text.valign.bottom, text.size.Large])

    outputfile = '/scratch/david/master_project/plots/publication/hi/shiftedhardness'
    c.writePDFfile(outputfile)
    # os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


if __name__=='__main__':
    plotpcpane()
