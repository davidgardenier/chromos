import os
import glob
import pandas as pd
from math import atan2, degrees, pi, log10, sqrt, radians
import matplotlib.pyplot as plt
from collections import defaultdict
from pyx import *

def read_light_curve(path):
    '''
    Function to read the data from the lightcurve fits files.

    Input parameters:
     - path: path of the lightcurve

    Output parameters:
     - rate: rate of photons per second
     - t: time grid of the observation
     - dt: time resolution; usually 1/128. for RXTE data
     - n_bins: number of time bins in the total observation.
     - error: error on the rate of photons per second
    '''
    from astropy.io import fits

    hdulist = fits.open(path)
    # Header stuff
    header = hdulist[1].header
    n_bins = header['NAXIS2']
    dt = header['TIMEDEL']
    # Data stuff
    data = hdulist[1].data
    t = data['TIME']
    rate = data['RATE']
    error = data['ERROR']
    hdulist.close()

    return rate, t, dt, n_bins, error

rate, t, dt, n_bins, error = read_light_curve('/scratch/david/master_project/aquila_X1/P60054/60054-02-01-03/event_125us.lc')
t = t - t[0]
# Set up plot details
g = graph.graphxy(width=8,
                  x=graph.axis.lin(min=1800,max=2500, title="Time (s)",density=1),
                  y=graph.axis.lin(min=0.01, max=4000, title="Rate (s$^{-1}$)"))

g.plot(graph.data.values(x=t,y=rate),[graph.style.line([style.linewidth.Thin, color.rgb.red])])

outputfile = '/scratch/david/master_project/plots/publication/lc/burst'
g.writePDFfile(outputfile)
#os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')
