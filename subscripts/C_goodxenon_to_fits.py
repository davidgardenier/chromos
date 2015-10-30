import json
from subprocess import Popen, PIPE, STDOUT
import glob

def xenon2fits(print_output=False):
    '''
    Function to convert GoodXenon files to fits files using make_se. Subsequently
    groups the paths to the produced files into a file 
    path_goodxenonfits_<resolution>. Updates the directionary with paths to
    these files
    '''

    # Let the user know what's going to happen
    purpose = 'Converting GoodXenon files to fits files'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    for obsid in d:
        if 'goodxenon' in d[obsid]:
            d[obsid]['goodxenon']['path_list_fits'] = []
            for path in sorted(d[obsid]['goodxenon']['path_list']):

                output = path.split('paths')[0] + 'gxfits_' + path.split('_')[-1]

                # Execute make_se
                p = Popen(['make_se'], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
                          bufsize=1)

                # Give the required input
                # -----------------------
                # Input file name
                p.stdin.write(path + '\n')
                # Output file name
                p.stdin.write(output + '\n')

                # Print output of program
                if print_output is True:
                    with p.stdout:
                        for line in iter(p.stdout.readline, b''):
                            print '    ' + line,
                        p.stdout.close()
                        p.wait()

                list_with_paths = glob.glob('./P' + obsid[:5] + '/' + obsid + '/gxfits*')
                output = path.split('paths')[0] + 'paths_goodxenonfits_' + path.split('_')[-1]
                d[obsid]['goodxenon']['path_list_fits'].append(output)
                
                # Write the list of paths to file
                with open(output, 'w') as text:
                    text.write('\n'.join(list_with_paths) + '\n')

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Converted all GoodXenon files to GoodXenon fits files'
