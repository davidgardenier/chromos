from pyx import *
import numpy as np

PATH = '/scratch/david/master_project/aquila_X1/pwr_colours.dat'
PLOTS = '/scratch/david/master_project/plots/'
d = np.genfromtxt(PATH, dtype=None)

d = [l for l in d if l[-1]==True]
c = zip(*d)
c = [list(l) for l in c]
pc1 = c[0]
pc1_error = c[1]
pc2 = c[2]
pc2_error = c[3]
obsid = c[4]
mode = c[5]
constraint = c[6]
pp = color.cmyk(0,0.8,0.69,0.39)
g = graph.graphxy(width=8,
                  x=graph.axis.log(min=0.05, max=101, title=r"PC1"),
                  y=graph.axis.log(min=0.01, max=12, title=r"PC2"))
g.plot(graph.data.values(x=pc1, dx=pc1_error, y=pc2, dy=pc2_error),[graph.style.symbol(size=0.08,symbolattrs=[pp]), graph.style.errorbar(errorbarattrs=[pp])])
g.writePDFfile(PLOTS + 'aquila_pcs')
