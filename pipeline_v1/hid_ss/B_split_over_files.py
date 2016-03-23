import glob
import json
import os
from collections import defaultdict

def split_files(obj, verbose=False):
    '''
    Function to split out the files created by Phil's script in find_data_files
    over each obsid folder, allowing code to be executed per obsid. Also
    creates a dictionary with information on each obsid
    '''

    # Let the user know what's going to happen
    purpose = 'Splitting out data over files'
    print purpose + '\n' + '='*len(purpose)

    # Find all obsids
    initial_obsids = [f.split('/')[-1] for f in glob.glob('./*/*-??-??-*')]
    # Getting rid of potential obsids with letters at the end
    obsids = [o for o in initial_obsids if o[-1].isdigit()]
    # Form into dictionary of form
    # d['<obsid>']['<datamode>']['<paths/time/etc.>'] = []
    d = {el:defaultdict(lambda : defaultdict(list)) for el in obsids}

    # For all files created by find_data_files loop through
    all_files = glob.glob('./*/' + obj + '*.list')
    # Remove all 500us event files
    all_files = [a for a in all_files if '500us' not in a]

    for a in all_files:
        mode = a.split('.')[-2]

        # Extract needed data into dictionary
        if 'Standard2f' in mode:
            with open(a) as s:
                for i, line in enumerate(s):
                    obsid = line.split('/')[0]
                    path = os.getcwd() + '/P' + obsid.split('-')[0] + '/' + line.split(' ')[0].split('.')[0]
                    time = line.split(' ')[2]

                    d[obsid]['std2']['paths'].append(path)
                    d[obsid]['std2']['times'].append(time)

    # Split paths out into a file per obsid
    for obsid in d:
        for mode in d[obsid]:
            # Split out std2 mode files
            if mode == 'std2':
                filename = 'paths_'+mode
                path_to_output = '/'.join([os.getcwd(),'P'+obsid.split('-')[0],obsid,filename])
                with open(path_to_output, 'w') as text:
                    text.write('\n'.join(d[obsid][mode]['paths']) + '\n')
                d[obsid][mode]['path_list'].append(path_to_output)

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Split out information to each obsid folder'
