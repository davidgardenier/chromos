import json
import numpy as np
import matplotlib.pyplot as plt

def plot_hid(verbose=False):
    '''
    Function to plot the Hardness-Intensity diagram
    '''

    # Print purpose of program
    purpose = 'Plotting a hardness-intensity diagram'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    flx = []
    flx_err = []
    rt = []
    rt_err = []

    for obsid in d:
        if 'std2' in d[obsid].keys():
            if 'hardint' not in d[obsid]['std2']:
                continue

            mode = 'std2'
            hardint = d[obsid][mode]['hardint'][0]

            data = np.genfromtxt(hardint)
            flx.append(data[0])
            flx_err.append(data[1])
            rt.append(data[2])
            rt_err.append(data[3])

    plt.errorbar(flx, rt, xerr=flx_err, yerr=rt_err)
    plt.xlabel('Intensity (counts/s)') #TODO Check units
    plt.ylabel('Hardness')
    plt.savefig('./../plots/hid.png')
