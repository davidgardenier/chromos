import os
import glob
import pandas as pd

def path(o):
    return '/scratch/david/master_project/' + o + '/info/database.csv'

def plot_dif_pcs():
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    objects = ['4u_1705_m44',
               'xte_J1808_369',
               'cir_x1',
               'cyg_x2',
               'EXO_0748_676',
               'HJ1900d1_2455',
               'sco_x1',
               'v4634_sgr',
               '4U_1728_34',
               '4U_0614p09',
               '4U_1702m43',
               'J1701_462',
               'aquila_X1',
               '4U_1636_m53',
               'gx_339_d4']

    # Set up plot details
    plt.figure(figsize=(10,10))
    colormap = plt.cm.Paired
    colours = [colormap(i) for i in np.linspace(0.1, 0.9, len(objects))]
    #marker = itertools.cycle(('^', '+', '.', 'o', '*'))

    for i, o in enumerate(objects):

        p = path(o)
        db = pd.read_csv(p)
        if 'pc1_wf' in db:
            db = db.dropna(subset=['pc1','pc1_wf'])
        else:
            continue
        print o

        x = db.pc1.values
        y = db.pc1.values / db.pc1_wf.values
        x2 = db.pc1_err.values
        y2 = db.pc1_err.values / db.pc1_err_wf.values
        # One big plot
        plt.scatter(x, y, marker='x', label=o, linewidth=2, color=colours[i])
        plt.scatter(x, y, marker='o', label=o, linewidth=2, color=colours[i])
        # Subplots
        #plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', linewidth=2)

        plt.xlim([0.01, 1000])
        plt.xlabel('PC1 (C/A = [0.25-2.0]/[0.0039-0.031])')
        plt.xscale('log', nonposx='clip')
        plt.ylabel('pc1_without_flare/pc_with_flare')
        #plt.yscale('log', nonposy='clip')
        plt.title('x=value, o=error')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        plt.savefig('/scratch/david/master_project/plots/flares/flare_effect_pc1_' + o + '.png', transparent=True)
        plt.gcf().clear()

        # ---------------------------------------------------------------------

        x = db.pc2.values
        y = db.pc2.values / db.pc2_wf.values
        x2 = db.pc2_err.values
        y2 = db.pc2_err.values / db.pc2_err_wf.values

        # One big plot
        plt.scatter(x, y, marker='x', label=o, linewidth=2, color=colours[i])
        plt.scatter(x, y, marker='o', label=o, linewidth=2, color=colours[i])
        # Subplots
        #plt.errorbar(x, y, xerr=xerror, yerr=yerror, fmt='o', linewidth=2)

        plt.xlim([0.01, 100])
        plt.xlabel('PC2 (B/D = [0.031-0.25]/[2.0-16.0])')
        plt.xscale('log', nonposx='clip')
        plt.ylabel('pc1_without_flare/pc_with_flare')
        #plt.yscale('log', nonposy='clip')
        plt.title('x=value, o=error')
        plt.legend(loc='best', numpoints=1)

        # In case you want to save each figure individually
        plt.savefig('/scratch/david/master_project/plots/flares/flare_effect_pc2_' + o + '.png', transparent=True)
        plt.gcf().clear()
        #plt.clf()

    #plt.show()

if __name__=='__main__':
    plot_dif_pcs()
