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


def plot_allpcs():
    import numpy as np
    import itertools

    scos=[('sco_x1', 'Sco X-1'),
          ('gx_17p2', 'GX 17+2'),
          ('gx_349p2', 'GX 349+2')]

    cygs = [('cyg_x2', 'Cyg X-2'),
          ('gx_5m1', 'GX 5-1'),
          ('gx_340p0', 'GX 340+0')]

    # Set up plot details
    g = graph.graphxy(height=7,
                      width=7,
                      x=graph.axis.log(min=1e-9, max=1e-6, title="Intensity (photons$\ $ergs$\ $cm$^{-2}$ s$^{-1}$)"),
                      y=graph.axis.lin(min=0.25, max=1, title=r"Hardness"),
                      key=graph.key.key(pos='br', dist=0.1))

    #scos = sorted(scos, key=lambda x: x[1])
    #cygs = sorted(cygs, key=lambda x: x[1])

    scatterstyle= [graph.style.symbol(graph.style.symbol.changecross, size=0.15, symbolattrs=[color.rgb.red])]

    for i, o in enumerate(scos):

        x_scos = []
        y_scos = []

        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = db[np.isfinite(db['flux_i3t16_s6p4t9p7_h9p7t16'])]
        x_scos.extend(db.flux_i3t16_s6p4t9p7_h9p7t16.values)
        y_scos.extend(db.hardness_i3t16_s6p4t9p7_h9p7t16.values)

    # Plot Atolls
        g.plot(graph.data.values(x=x_scos, y=y_scos, title=name), scatterstyle)
    #g.plot(graph.data.values(x=x_scos, y=y_scos, dx=xerror_scos, dy=yerror_scos, title='Sco-like Z sources'), errstyle)
    #plot Black Holes


    scatterstyle= [graph.style.symbol(graph.style.symbol.changetriangle, size=0.15, symbolattrs=[color.rgb.blue])]

    for i, o in enumerate(cygs):
        x_cygs = []
        y_cygs = []

        print o[-1]
        name = o[-1]
        o = o[0]
        p = path(o)
        db = pd.read_csv(p)
        db = db[np.isfinite(db['flux_i3t16_s6p4t9p7_h9p7t16'])]
        x_cygs.extend(db.flux_i3t16_s6p4t9p7_h9p7t16.values)
        y_cygs.extend(db.hardness_i3t16_s6p4t9p7_h9p7t16.values)

    # Plot Z
        g.plot(graph.data.values(x=x_cygs, y=y_cygs, title=name), scatterstyle)
    #g.plot(graph.data.values(x=x_cygs, y=y_cygs, dx=xerror_cygs, dy=yerror_cygs, title='Cyg-like Z sources'), errstyle)

    g.writePDFfile('/scratch/david/master_project/plots/publication/hi/sco_cyg')

if __name__=='__main__':
    plot_allpcs()
