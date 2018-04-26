# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from collections import defaultdict
from pyx import *

#obj = '4u_1705_m44'
obj = 'aquila_X1'
#obj = '4U_1728_m34'

def path(o):
    return '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'


def findbestres(res):
    '''Find the smallest resolution from a list of resolutions'''

    # Split resolutions into values and units
    heads = []
    tails = []
    for s in res:
        unit = s.strip('0123456789')
        num = s[:-len(unit)]
        heads.append(num)
        tails.append(unit)

    # Sort by unit, then by value
    unitorder = ['us','ms','s']
    for u in unitorder:
        if u in tails:
            indices = [i for i, x in enumerate(tails) if x==u]
            sameunits = [heads[i] for i in indices]
            sortvalues = sorted(sameunits)
            return sortvalues[0]+u


def findbestdataperobsid(df):
    '''Select the data with best mode and resolution'''
    ordering = ['gx1','gx2','event','binned','std2']
    for mode in ordering:
        if mode in df.modes.values:
            df = df[df.modes==mode]
            if df.shape[0] > 1:
                bestres = findbestres(df.resolutions.values)
                return df[df.resolutions==bestres].iloc[0]
            else:
                return df.iloc[0]


def findbestdata(db):
    # Apply constraint to the data
    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db

# Plot colour-colour diagram------------------------------------------
abr_states = ['eis','is','llb','lb','ub']

# Import data
p = path(obj)
db = pd.read_csv(p)
# Get hardness values
soft = 'hardness_i3t16_s2t3p5_h3p5t6'
hard = 'hardness_i3t16_s6p4t9p7_h9p7t16'
db = db[(np.isfinite(db[soft]) & np.isfinite(db[hard]))]

# Start up plot
g = graph.graphxy(height=7,
                  width=7,
                  x=graph.axis.lin(min=2.5, max=4.5, title="Softness"),
                  y=graph.axis.lin(min=0.5, max=1.5, title=r"Hardness"),
                  key=graph.key.key(pos='br', dist=0.1))
scatterstyle= [graph.style.symbol(size=0.1, symbolattrs=[color.gradient.Rainbow])]

# Split into states
states = {s:defaultdict(list) for s in abr_states}
dbs = {}
dbs['eis'] = db[(db[hard]>1.18)]
dbs['is'] = db[(db[hard]>0.63) & (db[hard]<1.18)]
dbs['llb'] = db[(db[hard]<0.63) & (db[soft]<3.15)]
dbs['lb'] = db[(db[hard]<0.63) & (db[soft]>3.15) & (db[soft]<3.4)]
dbs['ub'] = db[(db[hard]<0.63) & (db[soft]>3.4)]

# Plot per state
for state in abr_states:
    states[state]['obsids'] = list(set(dbs[state].obsids.values))
    x = dbs[state][soft].values
    y = dbs[state][hard].values

    g.plot(graph.data.values(x=x, y=y, title=state.upper()), scatterstyle)
    
g.writePDFfile('/scratch/david/master_project/plots/publication/cc/ns_states_' + obj)
#------------------------------------------------------------------------------

#Plot PCC diagram--------------------------------------------------------------
# Set up plot details
g = graph.graphxy(height=7,
                  width=7,
                  x=graph.axis.log(min=0.01, max=1000, title=r"PC1"),
                  y=graph.axis.log(min=0.01, max=100, title=r"PC2"),
                  key=graph.key.key(pos='tr', dist=0.1))
errstyle= [graph.style.symbol(graph.style.symbol.changesquare, size=0.1, symbolattrs=[color.gradient.Rainbow]),
           graph.style.errorbar(size=0,errorbarattrs=[color.gradient.Rainbow])]

db = pd.read_csv(p)
db = findbestdata(db)
        
for state in abr_states:
    obsids = states[state]['obsids']
    df = db[db['obsids'].isin(obsids)]

    x = df.pc1.values
    y = df.pc2.values
    xerror = df.pc1_err.values
    yerror = df.pc2_err.values
    g.plot(graph.data.values(x=x, y=y, title=state.upper()), scatterstyle)
    

g.writePDFfile('/scratch/david/master_project/plots/publication/pc/ns_states_' + obj)
