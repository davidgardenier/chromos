import json
import os
import glob

PATH = '/scratch/david/master_project/garching'
OBJECT_NAME = 'various'
PRINT_OUTPUT = True

os.chdir(PATH)

# Find all obsids
initial_obsids = sorted([r.split('/')[-1] for r in glob.glob('./*/?????-??-??-*')])
# Getting rid of obsids with letters at the end
obsids = [o for o in initial_obsids if o[-1].isdigit()]

with open('./info_on_files.json', 'r') as info:
    d = json.load(info)

for obsid in d:
    print obsid, d[obsid]['filter']['paths']
