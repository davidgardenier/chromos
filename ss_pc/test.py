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

n = 0
o = 0
for obsid in d:
    if 'event' not in d[obsid].keys() and 'goodxenon' not in d[obsid].keys():
        print 'Not present:', obsid
    if 'event' in d[obsid].keys() and 'goodxenon' in d[obsid].keys():
        print 'Present:', obsid
        for m in ['event','goodxenon']:
            print d[obsid][m]
