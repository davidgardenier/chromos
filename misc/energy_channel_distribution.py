# Function to determine the energy channel range needed for input during
# extraction. Requires the file energy_conversion_table.txt to determine the
# initial channel selection.
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

from datetime import datetime
from astropy.io import fits

obj = [ '4U_0614p09',
        '4U_1636_m53',
        '4U_1702m43',
        '4u_1705_m44',
        '4U_1728_34',
        'aquila_X1',
        'cir_x1',
        'cyg_x2',
        'EXO_0748_676',
        'gx_17p2',
        'gx_340p0',
        'gx_349p2',
        'gx_5m1',
        'HJ1900d1_2455',
        'IGR_J00291p5934',
        'IGR_J17480m2446',
        'IGR_J17498m2921',
        'KS_1731m260',
        'xte_J1808_369',
        'S_J1756d9m2508',
        'sco_x1',
        'sgr_x1',
        'sgr_x2',
        'v4634_sgr',
        'XB_1254_m690',
        'xte_J0929m314',
        'J1701_462',
        'xte_J1751m305',
        'xte_J1807m294',
        'xte_J1814m338',
        'gx_339_d4',
        'H1743m322',
        'xte_J1550m564']

def ch2e(ch,date):

    ss = '/scratch/david/master_project/scripts/subscripts/'
    
    with open(ss + 'energy_channel_conversion.txt', 'r') as txt:
        text = list(txt)
        stop_dates = [x + y for x, y in zip(text[2].split()[2:6], text[3].split()[2:6])]
        end_dates = [datetime.strptime(t, '%m/%d/%y(%H:%M)') for t in stop_dates]

        if len(date) == 8:
            date = datetime.strptime(date, '%d/%m/%y')
        else:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

        if date < end_dates[0]:
            epoch = 1
        elif date < end_dates[1]:
            epoch = 2
        elif date < end_dates[2]:
            epoch = 3
        elif date < end_dates[3]:
            epoch = 4
        else:
            epoch = 5

        if epoch < 5:
            column = epoch + 1
        else:
            column = -1

        # Make a list of energies
        energies = [float(i.split()[column]) for i in text[12:]]
        channels = [i.split()[0] for i in text[12:]]
        
        if type(ch) is float:
            return float('NaN')
        
        if ch[0]<5:
            ei = 0
        else:
            ei = channels.index(str(ch[0]))
        
        # starting energy
        return float(energies[ei])


def start_ch(mode,path):
    '''
    Look inside each file to get the channel range it contains
    '''

    # Get the list in which you want search for channels
    if mode == 'event':
        tevtb2 = fits.open(path)[1].header['TEVTB2']
        if 'C' not in tevtb2:
            try:
                # I think this fixes VLE (Very Long Event) data files hidden as event files.
                # Not entirely sure about the rel_channels (usually they're given in the
                # header as 5-255, but presumably that doesn't mean it's all one bin?)
                tddes2 = fits.open(path)[1].header['TDDES2']
                rel_channels = tddes2.split('& C')[1][1:].split(']')[0].replace('~','-')
                rel_channels = ','.join([str(e) for e in range(int(rel_channels.split('-')[0]), int(rel_channels.split('-')[1])+1)])
            except:
                print 'ERROR: No channel information in this file'
                return float('NaN')
        else:
            # Cut out the channels
            rel_channels = tevtb2.split(',C')[1][1:].split(']')[0].replace('~','-')
    elif mode == 'binned':
        tddes2 = fits.open(path)[1].header['TDDES2']
        rel_channels = tddes2.split('& C')[1][1:].split(']')[0].replace('~','-')
        if ',' not in rel_channels:
            return float('NaN')

    # Get a list of numbers to actually search through
    chs = []
    for cr in rel_channels.split(','):

        # Spent ages looking, but couldn't find what 0~4,(5:35) means, or (0-4),
        # (5:35). Am assuming ':' means all channel in that range (on basis of
        # an extracted spectrum), and not sure what () means
        if '(' in cr:
            cr = cr.split(')')[0].split('(')[1]
            if '-' in cr:
                crs = cr.split('-')
            if ':' in cr:
                crs = cr.split(':')
            cr = [e for e in range(int(crs[0]), int(crs[1])+1)]
        elif '-' in cr:
            cr = [e for e in range(int(cr.split('-')[0]), int(cr.split('-')[1])+1)]
        elif ':' in cr:
            crs = cr.split(':')
            cr = [e for e in range(int(crs[0]), int(crs[1])+1)]
        else:
            cr = [int(cr)]

        chs.append(cr)

    # Ensure the lowest energy channel is not returned
    # See Gleissner T., Wilms J., Pottschimdt K. etc. 2004
    if chs[0][0] == 0:
        if len(chs) > 2:
            chs = chs[1] #Assuming channels doesn't do 0-19,etc
        else:
            chs = float('NaN')
    else:
        chs = chs[0]

    return chs


def find_channels():
    '''
    Find the distribution of starting energies
    '''

    purpose = 'Find starting energy distribution'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict

    filein = '/scratch/david/master_project/scripts/misc/paths.txt'
    fileout = '/scratch/david/master_project/scripts/subscripts/paths.py'

    f = open(filein,'r')
    filedata = f.read()
    f.close()


    d = defaultdict(list)
    for o in obj:

        data = '/scratch/david/master_project/' + o + '/'
        database = '/scratch/david/master_project/'+o+'/info/database_'+o+'.csv'
        os.chdir(data)
        db = pd.read_csv(database)


        for obsid, group in db.groupby(['obsids']):
            group = group.drop_duplicates('paths_data')

            es = []
            ms = []
            for mode, path, time in zip(group.modes,group.paths_data,group.times):
                
                if mode == 'std1' or mode=='std2' or mode=='gx2':
                    continue
                elif mode == 'gx1':
                    e = ch2e([0],time)
                else:
                    ch = start_ch(mode,path)
                    e = ch2e(ch,time)

                print obsid, mode, ch, e
                
                es.append(e)
                ms.append(mode)
            
            if 'gx1' in ms:
                i = ms.index('gx1')
                m = 'gx1'
                fe = es[i]
            elif 'event' in ms:
                i = ms.index('event')
                m = 'event'
                fe = es[i]
            elif 'binned' in ms:
                i = ms.index('binned')
                m = 'binned'
                fe = es[i]
            
            d['mode'].append(m)
            d['energies'].append(fe)
            d['objects'].append(o)
            d['obsid'].append(obsid)
            
        df = pd.DataFrame(d)
        df.to_csv('/scratch/david/master_project/misc/energy_dist_' + o + '.csv')     


def plotting():
    import matplotlib.pyplot as plt
    import pandas as pd
    
    for o in obj:
        df = pd.read_csv('/scratch/david/master_project/misc/energy_dist_' + o + '.csv')
        df.hist(column='energies')
        plt.savefig('/scratch/david/master_project/misc/energy_dist_' + o + '.png')

           
#find_channels()
plotting()
