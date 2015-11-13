import glob
import json
import os
from collections import defaultdict

def split_files(objectname, print_output=False):
    '''
    Function to split out the files created by Phil's script in find_data_files
    over each obsid folder, allowing code to be executed per obsid. Also
    creates a dictionary with information on each obsid
    '''

    # Let the user know what's going to happen
    purpose = 'Splitting out data over files'
    print purpose + '\n' + '='*len(purpose)

    # Find all obsids
    initial_obsids = sorted([r.split('/')[-1] for r in glob.glob('./*/?????-??-??-*')])
    # Getting rid of obsids with letters at the end
    obsids = [o for o in initial_obsids if o[-1].isdigit()]
    # Form into dictionary of form
    # d['<obsid>']['<datamode>']['<paths/time/etc.>'] = []
    d = {el:defaultdict(lambda : defaultdict(list)) for el in obsids}

    # For all files created by find_data_files loop through
    all_files = glob.glob('./*/' + objectname + '*.list')
    # Remove all 500us event files
    all_files = [a for a in all_files if '500us' not in a]

    for a in all_files:
        mode = a.split('.')[-2]

        # Extract needed data into dictionary

        if 'E_' in mode:
            with open(a) as e:
                for line in e:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d[obsid]['event']['paths'].append(path)
                    d[obsid]['event']['times'].append(time)
                    d[obsid]['event']['resolutions'].append(resolution)

        if 'Standard2f' in mode:
            with open(a) as s:
                for i, line in enumerate(s):
                    # Only every third line is needed
                    if i%3 == 0:
                        obsid = line.split('/')[0]
                        path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                        time = line.split(' ')[2]

                        d[obsid]['std2']['paths'].append(path)
                        d[obsid]['std2']['times'].append(time)

        if 'GoodXenon1' in mode:
            with open(a) as g:
                for line in g:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d[obsid]['goodxenon1']['paths'].append(path)
                    d[obsid]['goodxenon1']['times'].append(time)
                    d[obsid]['goodxenon1']['resolutions'].append(resolution)

        if 'GoodXenon2' in mode:
            with open(a) as g:
                for line in g:
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]
                    resolution = line.split(' ')[1].split('_')[1]

                    d[obsid]['goodxenon2']['paths'].append(path)
                    d[obsid]['goodxenon2']['times'].append(time)
                    d[obsid]['goodxenon2']['resolutions'].append(resolution)


    # Split paths out into a file per obsid
    for obsid in d:
        for mode in d[obsid]:

            # Split out event mode files
            if mode == 'event':
                # This complicated code returns a list with per element,
                # the resolution and index of the resolution, to enable those
                # to be joined
                resolutions = map(lambda val: (val, [i for i in xrange(len(d[obsid][mode]['resolutions'])) if d[obsid][mode]['resolutions'][i] == val]), list(set(d[obsid][mode]['resolutions'])))

                # for each resolution, create a paths_<event_500us> file
                for r in resolutions:
                    res = r[0]
                    filename = 'paths_'+mode+'_'+res
                    path_to_output = '/'.join([os.getcwd(),'P'+obsid.split('-')[0],obsid,filename])
                    with open(path_to_output, 'w') as text:
                        text.write('\n'.join([d[obsid][mode]['paths'][i] for i in r[1]]) + '\n')
                    d[obsid][mode]['path_list'].append(path_to_output)

            # Split out std2 mode files
            if mode == 'std2':
                filename = 'paths_'+mode
                path_to_output = '/'.join([os.getcwd(),'P'+obsid.split('-')[0],obsid,filename])
                with open(path_to_output, 'w') as text:
                    text.write('\n'.join(d[obsid][mode]['paths']) + '\n')
                d[obsid][mode]['path_list'].append(path_to_output)

            # Split out GoodXenon files (and add GoodXenon1&2 paths to same file)
            if mode == 'goodxenon1':

                # Determine the resolution of each 'path'
                resolutions = map(lambda val: (val, [i for i in xrange(len(d[obsid][mode]['resolutions'])) if d[obsid][mode]['resolutions'][i] == val]), list(set(d[obsid][mode]['resolutions'])))

                # for each resolution, create a paths_<goodxenon_2s> file
                for r in resolutions:
                    res = r[0]
                    filename = 'paths_'+mode[:-1]+'_'+res
                    path_to_output = '/'.join([os.getcwd(),'P'+obsid.split('-')[0],obsid,filename])
                    with open(path_to_output, 'w') as text:
                        text.write('\n'.join(d[obsid][mode]['paths'] + d[obsid]['goodxenon2']['paths']) + '\n')
                    d[obsid]['goodxenon1']['path_list'].append(path_to_output)

        # Create a new dictionary entry for goodxenon, rendering the goodxenon1
        # and goodxenon2 entries obsolete
        if 'goodxenon1' in d[obsid]:
            d[obsid]['goodxenon'] = d[obsid]['goodxenon1']

        if 'goodxenon' not in d[obsid] and 'event' not in d[obsid]:
            print('!'*79,
                  'WARNING - NO SUITABLE DATAMODES FOUND',
                  'IMPLEMENT SUPPORT FOR STANDARD2 DATA',
                  '!'*79)
      
        '''
        # Create a filter: only use event files if goodxenon not present
        # else use Standard2 files (not necessary in this case)
        # Note this doesn't account for the length of observations - it could
        # well be that event mode files have longer, and thus more useful
        # lightcurves
        if 'goodxenon' in d[obsid] and 'event' in d[obsid]:
            del d[obsid]['event']
        if 'goodxenon' not in d[obsid] and 'event' not in d[obsid]:
            print('!'*79,
                  'WARNING - NO SUITABLE DATAMODES FOUND',
                  'IMPLEMENT SUPPORT FOR STANDARD2 DATA',
                  '!'*79)
        '''

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Split out information to each obsid folder'
