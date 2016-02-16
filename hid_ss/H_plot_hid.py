import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

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
    dates = []

    for obsid in d:
        if 'std2' in d[obsid].keys():
            if 'hardint' not in d[obsid]['std2']:
                continue

            mode = 'std2'
            hardint = d[obsid][mode]['hardint'][0]

            date = d[obsid][mode]['times'][0]
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            dates.append(date)

            data = np.genfromtxt(hardint)
            flx.append(data[0])
            flx_err.append(data[1])
            rt.append(data[2])
            rt_err.append(data[3])

            if data[0] < 0.1e-8 and (0.4 < data[2] < 0.6):
                print obsid, data[0], data[1], data[2], data[3]
            if obsid == '93703-01-03-05':
                print obsid, data[0], data[1], data[2], data[3]

    #Sort according to date
    flx = [x for (y,x) in sorted(zip(dates,flx))]
    flx_err = [x for (y,x) in sorted(zip(dates,flx_err))]
    rt = [x for (y,x) in sorted(zip(dates,rt))]
    rt_err = [x for (y,x) in sorted(zip(dates,rt_err))]

    plt.errorbar(flx, rt, xerr=flx_err, yerr=rt_err)
    # 93703-01-03-05
    #JOEL
    #plt.errorbar([5.8682e-10], [1.64044], xerr=[4.1236e-11],  yerr=[0.01474], fmt='o', capsize=6)
    #MINE
    plt.errorbar([4.1705e-10], [0.68118], xerr=[1.1752e-12],  yerr=[0.00365], fmt='o', capsize=6)
    plt.xlabel('Intensity (Photons*ergs/cm^2/s)')
    #plt.xscale('log')
    plt.ylabel('Hardness')
    plt.savefig('./../plots/hid.png')
