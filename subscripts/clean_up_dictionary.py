#!/usr/bin/env python
# Program to test whether all lightcurves have been created or not

import os.path
import json
import os

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True

os.chdir(PATH)

with open('./info_on_files.json', 'r') as info:
    d = json.load(info)
    
for obsid in d:
    for mode in d[obsid]:
        for data in d[obsid][mode].keys():
            if 'path' in data:
                
                if isinstance(d[obsid][mode][data], list):
                    for path in d[obsid][mode][data]:
                        if 'pca' not in path:
                            if os.path.isfile(path) is False:
                                print obsid, path.split('/')[-1], os.path.isfile(path)
