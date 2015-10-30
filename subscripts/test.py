import json
import os

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True

os.chdir(PATH)

with open('./info_on_files.json', 'r') as info:
    d = json.load(info)

print json.dumps(d, sort_keys=True, indent=4)
