import numpy as np
import os
import json

PATH = '/scratch/david/master_project/full_data/'
os.chdir(PATH)

text = np.genfromtxt('./pwr_colours.dat', delimiter=' ', dtype=None)
pc1s, pc2s, obsids, modes, limited = zip(*text)
obsids = np.array(obsids)
# Import data
with open('./info_on_files.json', 'r') as info:
    d = json.load(info)

o = 0
k = 0
for obsid in d:
    o += 1
    f = np.where(obsids == obsid)[0]
    if len(f) == 0:
        k += 1

print o, k
