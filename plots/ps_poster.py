import os
import glob
import pandas as pd
from math import atan2, degrees, pi, log10, sqrt, radians
from scipy.stats import binned_statistic
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from pyx import *

# Import data
try:
    all_data = np.loadtxt('/scratch/david/master_project/aquila_X1/P40033/40033-10-03-00/event_125us.ps',dtype=float)
    inverted_data = np.transpose(all_data)
except IOError:
    print 'No power spectrum'


# Give the columns their names
ps = inverted_data[0]
ps_error = inverted_data[1]
freq = inverted_data[2]
freq_error = inverted_data[3]
ps_squared = inverted_data[4]
num_seg = inverted_data[5][0]
binmeans, binedges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=50))
values = graph.data.values(x=binedges[:-1], y=binmeans)

# Set up plot details
g = graph.graphxy(width=5,
                  x=graph.axis.log(min=1e-2,max=60,title="Frequency (Hz)"),
                  y=graph.axis.log(min=1e-4,max=1e-1, title="Frequency $\cdot$ Power"))

g.plot(values,[graph.style.histogram(lineattrs=[ style.linewidth.Thick,],autohistogrampointpos=0,fromvalue=1e-6,steps=1)])

outputfile = '/scratch/david/master_project/plots/publication/poster/ps'
g.writePDFfile(outputfile)
#os.system('convert -density 300 '+outputfile+'.pdf -quality 90 '+outputfile+'.png')
