# Quick script to overplot hardness-intensity values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
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


class empty:

	def __init__(self):
		pass
	def labels(self, ticks):
		for tick in ticks:
			tick.label=""

def plotpcpane(objects, nr):
    # Set up plot details
    c=canvas.canvas()
    if len(objects) == 12:
        xposition=[0.0,6.0,12.0, 0.0,6.0,12.0, 0.0,6.0,12.0,   0.0,6.0,12.0]
        yposition=[0.0,0.0,0.0,  6.0,6.0,6.0,  12.0,12.0,12.0, 18.0,18.0,18.0]
        order = [10,11,12,7,8,9,4,5,6,1,2,3]
    if len(objects) == 6:
        xposition=[0.0,6.0,12.0, 0.0,6.0,12.0]
        yposition=[0.0,0.0,0.0,  6.0,6.0,6.0]
        order = [4,5,6,1,2,3]
    if len(objects) == 3:
        xposition=[0.0,6.0,12.0]
        yposition=[0.0,0.0,0.0]
        order = [1,2,3]
    if len(objects) == 4:
        xposition=[0.0,6.0,12.0, 0.0]
        yposition=[6.0,6.0,6.0, 0.0]
        order = [1,2,3, 4]
    objcts = [objects[j-1] for j in order]

    print str(nr), '\n=========================='
    for i in range(len(objcts)):
        obj = objcts[i]
        print names[obj]

        p = path(obj)
        db = pd.read_csv(p)
        db = db[(np.isfinite(db['flux_i3t16_s6p4t9p7_h9p7t16'])) & (db.hardness_i3t16_s6p4t9p7_h9p7t16>=0.1)]
        x = db.flux_i3t16_s6p4t9p7_h9p7t16.values
        y = db.hardness_i3t16_s6p4t9p7_h9p7t16.values

        values = graph.data.values(x=x, y=y)

        myticks = []#[graph.axis.tick.tick(1e-6, label=" ", labelattrs=[text.mathmode])]
    	if yposition[i]!=0.0:
            xtitle = ""
            xtexter=empty()
    	else:
            xtitle = "Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"
            xtexter=graph.axis.texter.mixed()
            myticks = [graph.axis.tick.tick(1e-12, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-10, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-8, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-6, label=" ", labelattrs=[text.mathmode])]
    	if xposition[i]!=0.0:
            ytitle = ""
            ytexter=empty()
    	else:
            ytitle="Hardness"
            ytexter=graph.axis.texter.mixed()
        if len(objects) == 7 and yposition[i]==6.0 and xposition[i]==6:
            xtitle = "Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"
            xtexter=graph.axis.texter.mixed()
            myticks = [graph.axis.tick.tick(1e-12, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-10, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-8, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-6, label=" ", labelattrs=[text.mathmode])]
        if len(objects) == 7 and yposition[i]==6.0 and xposition[i]==12:
            xtitle = "Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"
            xtexter=graph.axis.texter.mixed()
            myticks = [graph.axis.tick.tick(1e-12, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-10, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-8, label=" ", labelattrs=[text.mathmode]),
                       graph.axis.tick.tick(1e-6, label=" ", labelattrs=[text.mathmode])]

    	g=c.insert(graph.graphxy(width=6.0,
                                 height=6.0,
                                 xpos=xposition[i],
                                 ypos=yposition[i],
	                             x=graph.axis.log(min=1e-12,max=1e-6,title=xtitle,texter=xtexter,manualticks=myticks),
	                             y=graph.axis.lin(min=0.0,max=2.75,title=ytitle,texter=ytexter)))

        # Plot Neutron Stars
#        grey= color.cmyk(0,0,0,0.5)
#        nsstyle = [graph.style.symbol(size=0.1, symbolattrs=[grey])]
#        g.plot(graph.data.values(x=x_ns, y=y_ns, title='Neutron Stars'), nsstyle)

    	g.plot(values,[graph.style.symbol(symbolattrs=[color.rgb.red],size=0.1)])
        xtext, ytext = g.pos(6e-7, 2.6)
        g.text(xtext,ytext, names[obj], [text.halign.boxright, text.valign.top])

    outputfile = '/scratch/david/master_project/plots/publication/hi/pane_%i' %nr
    c.writePDFfile(outputfile)
    os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')


if __name__=='__main__':

    nr = 1
    pane = ['4U_0614p09',
            '4U_1636_m53',
            '4U_1702m43',
            '4u_1705_m44',
            '4U_1728_34',
            'aquila_X1',
            'cyg_x2',
            'gx_5m1',
            'gx_17p2',
            'gx_340p0',
            'gx_349p2',
            'HJ1900d1_2455']
    plotpcpane(pane, nr)

    nr = 2
    pane = ['IGR_J00291p5934',
            'IGR_J17480m2446',
            'IGR_J17498m2921',
            'KS_1731m260',
            'xte_J1808_369',
            'S_J1756d9m2508',
            'sco_x1',
            'sgr_x1',
            'sgr_x2',
            'v4634_sgr',
            'XB_1254_m690',
            'xte_J0929m314']
    plotpcpane(pane, nr)

    nr = 3
    pane = ['J1701_462',
            'xte_J1751m305',
            'xte_J1807m294',
            'xte_J1814m338']
    plotpcpane(pane, nr)

    nr = 4
    pane = ['gx_339_d4','H1743m322','xte_J1550m564']
    plotpcpane(pane, nr)
