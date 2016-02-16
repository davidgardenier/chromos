from pyx import *
import numpy as np
from scipy.stats import binned_statistic

PATH = '/scratch/david/master_project/plots/example_ps/'

pp = color.cmyk(0,0.8,0.69,0.39)
bl = color.cmyk(0,0,0,1)
def func1(x):
    x = x*10.
    return 0.1*np.sin(2*x) + 0.5*np.sin(1000*x) + 1.75 #0.3*np.random.random() #+ 1.5

def func2(x):
    x = x*10.
    return 0.5*np.sin(20*x) + 0.5*np.sin(x) + 1.75 #+ 0.3*np.random.random() + 1.5

def func3(x):
    return 0.8*np.sin(0.05*(x+25)) + 0.1*np.sin(5*x) + 2
    
x1 = np.linspace(0.01,0.1,100)
f1 = [func1(x) for x in x1]
x2 = np.linspace(0.1,1,100)
f2 = [func2(x) for x in x2]
x3 = np.linspace(10,100,100)
f3 = [func3(x) for x in x3]

c = canvas.canvas()

g1 = c.insert(graph.graphxy(width=5, height=5,
                  x=graph.axis.lin(min=0.01,max=0.1,title=r'Time (s)'),
                  y=graph.axis.lin(min=1,max=3,title=r'Flux')))
g1.plot(graph.data.values(x=x1, y=f1),[graph.style.line([bl, style.linestyle.solid, style.linewidth.thick])])
#g1.writePDFfile(PATH + 'sim_lc_1')

g2 = c.insert(graph.graphxy(width=5, height=5,
                  x=graph.axis.lin(min=0.1,max=1,title=r'Time (s)'),
                  xpos=g1.width+0.5,
                  y=graph.axis.linkedaxis(g1.axes["y"])))
g2.plot(graph.data.values(x=x2, y=f2),[graph.style.line([bl, style.linestyle.solid, style.linewidth.thick])])
#g2.writePDFfile(PATH + 'sim_lc_2')

g3 = c.insert(graph.graphxy(width=5, height=5,
                  x=graph.axis.lin(min=10,max=100,title=r'Time (s)'),
                  xpos=g1.width+0.5+g2.width+0.5,
                  y=graph.axis.linkedaxis(g2.axes["y"])))
g3.plot(graph.data.values(x=x3, y=f3),[graph.style.line([bl, style.linestyle.solid, style.linewidth.thick])])
c.writePDFfile(PATH + 'sim_lc_bl')
