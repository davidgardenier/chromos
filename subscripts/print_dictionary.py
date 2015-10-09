import json
import os

def print_dictionary():

    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Write dictionary with all information to file
    with open('./../scripts/logs/dictionary.txt', 'w') as info:
        info.write(json.dumps(d, sort_keys=True, indent=4))
