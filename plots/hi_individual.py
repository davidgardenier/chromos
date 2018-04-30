# Quick script to overplot hardness-intensity values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
from pyx import *


def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'


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
        #('H1743m322':'H1743-322'),  # BH system
        #('xte_J1550m564', 'XTE J1550-564'), #BH system
        ]

    errstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow]),
               graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]
    scatterstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow])]

    objects = sorted(objects, key=lambda x: x[1])
    for i, o in enumerate(objects):
        name = o[-1]
        o = o[0]
        print o

        # Set up plot details
        g = graph.graphxy(height=6,
                          width=6,
                          x=graph.axis.log(min=1e-12, max=1e-6, title="Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"),
                          y=graph.axis.lin(min=0.00, max=2.5, title=r"Hardness"),
                          key=graph.key.key(pos=None,hpos=1.0,vpos=0.5,hinside=0, dist=0.05, textattrs=[text.size.small]))

        p = path(o)
        db = pd.read_csv(p)
        db = db[np.isfinite(db['flux_i3t16_s6p4t9p7_h9p7t16'])]
        x = db.flux_i3t16_s6p4t9p7_h9p7t16.values
        y = db.hardness_i3t16_s6p4t9p7_h9p7t16.values

        g.plot(graph.data.values(x=x, y=y, title=name), scatterstyle)

        g.writePDFfile('/scratch/david/master_project/plots/publication/hi/individual/%s' %o)

if __name__=='__main__':
    plot_allpcs()
