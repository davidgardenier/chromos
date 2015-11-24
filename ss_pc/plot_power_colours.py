import os
import matplotlib.pyplot as plt
import numpy as np

PATH = '/scratch/david/master_project/full_data'
os.chdir(PATH)

pc1, pc2, obs, m, const = np.genfromtxt('./pwr_colours.dat',
                                        delimiter=' ',
                                        dtype=np.str,
                                        unpack=True)

pc1 = [float(i) for i in pc1]
pc2 = [float(i) for i in pc2]

for i in range(len(pc1)):
    if const[i] == 'True':
        colour = 'b'
    else:
        colour = 'r'

    plt.scatter(pc1[i],pc2[i], color=colour)

plt.axis([0.01, 1000, 0.01, 1000])
plt.xlabel('PC1 ([0.25-2.0]/[0.0039-0.031])')
plt.xscale('log')
plt.ylabel('PC2 ([0.031-0.25]/[2.0-16.0])')
plt.yscale('log')
plt.show()
