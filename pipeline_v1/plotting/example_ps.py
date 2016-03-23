from pyx import *
import numpy as np
from scipy.stats import binned_statistic

PATH = '/scratch/david/master_project/plots/example_ps/'
F = 'power_spectrum_goodxenon_2s'
bl = color.cmyk(0,0,0,1)

ps, ps_err, freq, freq_err , _ , _ = np.loadtxt(PATH + F,dtype=float,unpack=True)

idx = [i for i, pe in enumerate(ps_err) if ps[i] - pe<=0]
#print len(ps_err), len(idx)
#ps = [i for j, i in enumerate(ps) if j not in idx]
#ps_err = [i for j, i in enumerate(ps_err) if j not in idx]
#freq = [i for j, i in enumerate(freq) if j not in idx]
#freq_err = [i for j, i in enumerate(freq_err) if j not in idx]

bin_means, bin_edges, binnumber = binned_statistic(freq, ps, bins=np.logspace(-2,2, num=25), statistic='mean')

bin_x = [(a + b) / 2. for a, b in zip(bin_edges[:-1], bin_edges[1:])]
#print bin_x, bin_means
pp = color.cmyk(0,0.8,0.69,0.39)

#red = [x for i, x in enumerate(bin_means) if (bin_x[i] <100 and bin_x[i] >10)]
#red_x = [x for i, x in enumerate(bin_x) if (bin_x[i] <100 and bin_x[i] >10)]
#bin_means = [x for x in bin_means if x not in red]
#bin_x = [x for x in bin_x if x not in red_x]
#del bin_means[-1]

g = graph.graphxy(width=12, height=3,
                  x2=graph.axis.log(title=r'Temporal Frequency (Hz)'),
                  y=graph.axis.log(title=r'Power'))
g.plot(graph.data.values(y=bin_means, x=bin_x),[graph.style.symbol(size=0.2,symbolattrs=[bl])])
#g.plot(graph.data.values(y=red, x=red_x),[graph.style.symbol(graph.style.symbol.plus, size=0.3,symbolattrs=[pp])])

g.finish()
g.stroke(g.xgridpath(0.1))

g.writePDFfile(PATH + 'ps_dotted')
