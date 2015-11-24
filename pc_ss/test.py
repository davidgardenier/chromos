import json
import os
import glob

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True

os.chdir(PATH)

# Find all obsids
initial_obsids = sorted([r.split('/')[-1] for r in glob.glob('./*/?????-??-??-*')])
# Getting rid of obsids with letters at the end
obsids = [o for o in initial_obsids if o[-1].isdigit()]

with open('./info_on_files.json', 'r') as info:
    d = json.load(info)

for obsid in d:
    for mode in d[obsid]:

        # Split out event mode files
        if mode == 'binned':
            # This complicated code returns a list with per element,
            # the resolution and index of the resolution, to enable those
            # to be joined
            resolutions = map(lambda val: (val, [i for i in xrange(len(d[obsid][mode]['resolutions'])) if d[obsid][mode]['resolutions'][i] == val]), list(set(d[obsid][mode]['resolutions'])))
            print d[obsid][mode]['resolutions']
            resolutions = sorted(resolutions, key=lambda tup: tup[1])
            # for each resolution, create a paths_<event_500us> file
            for r in resolutions:
                res = r[0]
                filename = 'paths_'+mode+'_'+res
                path_to_output = '/'.join([os.getcwd(),'P'+obsid.split('-')[0],obsid,filename])
                print path_to_output
