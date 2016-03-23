from pyx import *
import numpy as np
import matplotlib.pyplot as plt

PATH = '/scratch/david/master_project/garching/pwr_colours.dat'
PLOTS = '/scratch/david/master_project/plots/'
d = np.genfromtxt(PATH, dtype=None)

#d = [l for l in d if l[-1]==True]
c = zip(*d)
c = [list(l) for l in c]
pc1 = c[0]
pc1_error = c[1]
pc2 = c[2]
pc2_error = c[3]
obsid = c[4]
mode = c[5]
constraint = c[6]

g = graph.graphxy(width=8,
                  x=graph.axis.log(min=0.01, title=r"PC1"),
                  y=graph.axis.log(min=0.01, title=r"PC2"),
                  key=graph.key.key(pos='mr', hinside=0, vinside=0, dist=0.1))

points = []
for i in range(len(pc1)):
    points.append(graph.data.values(x=[pc1[i]], dx=[pc1_error[i]], y=[pc2[i]], dy=[pc2_error[i]], title=obsid[i]))

mystyle = [graph.style.symbol(size=0.15, symbolattrs=[color.gradient.Rainbow]),
           graph.style.errorbar(errorbarattrs=[color.gradient.Rainbow])]

g.plot(points, mystyle)
g.writePDFfile(PLOTS + 'garching_pcs')
