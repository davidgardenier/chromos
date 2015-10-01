import glob
import os
from subprocess import Popen, PIPE, STDOUT
from collections import defaultdict


def split_lists_per_obsid():
    '''
    Function to split out lists of locations of GoodXenon files to each obsid 
    folder, and to merge the location paths of GoodXenon1 and GoodXenon2 files
    to enable make_se to read these files
    
    Output:
     - a list of paths to all files with the locations of the GoodXenon files
    '''

    # Find paths to all files
    gx1 = glob.glob('./*/aquila.GoodXenon1*.xdf')
    gx2 = glob.glob('./*/aquila.GoodXenon2*.xdf')

    # Check if both GoodXenon files have been found
    if len(gx1) != len(gx2):
        print ' Warning - mismatch of GoodXenon files'

    paths = []

    # Split files out over each obsid folder
    for i in range(len(gx1)):

        # Split out GoodXenonwithpropane files:
        if 'Propane' in gx1[i]:
            print ' Skipping over gx file with propane:', gx1[i]
            continue
        else:
            # Open the GoodXenon.xdf files
            with open(gx1[i], 'r') as g1, open(gx2[i], 'r') as g2:
            
                d = defaultdict(list)
                
                # Get the timing to ensure multiple timings per obsid don't cause
                # any problems
                timing = gx1[i].split('_')[-1].split('.')[0]
                
                # Split files out per obsid
                for line in g1:
                    obsid = line.split('/')[6]
                    d[obsid].append(line)

                for line in g2:
                    obsid = line.split('/')[6]
                    d[obsid].append(line)
                
                # Write out per obsid    
                for key in d:
                    path = d[key][0].split('pca')[0]
                    # Write to file
                    f = open(path + 'goodxenon_' + timing + '.list', 'w')
                    f.write(''.join(d[key]))
                    f.close()
                    
                    paths.append(path + 'goodxenon_' + timing + '.list')

    # Sort the paths
    paths.sort()

    return paths
    

def xenon2fits(print_output=False):
    '''
    Function to convert all goodxenon files to fits files suitable for
    later extracting. Uses the perl function make_se. Subsequently creates a 
    file named gxlist_<timing> for the input of seextrct
    
    Arguments:
        - print_output
    '''
    
    # Find paths to files with list of GoodXenon files
    paths = split_lists_per_obsid()
    # Create a list of paths to which to save
    saving_paths = ['/'.join(p.split('/')[:-1]) + '/gx_' + p.split('_')[-1].split('.')[0] for p in paths]

    # For each path
    for i in range(len(paths)):

        # Execute make_se
        p = Popen(['make_se'], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
                  bufsize=1)

        # Give the required input
        # -----------------------
        # Input file name
        p.stdin.write(paths[i] + '\n')
        # Output file name
        p.stdin.write(saving_paths[i] + '\n')
        
        # Print output of program
        if print_output is True:
            with p.stdout:
                for line in iter(p.stdout.readline, b''):
                    print '    ' + line,
                p.stdout.close()
                p.wait()
    
    # Find the root of each path
    root_dir = ['/'.join(r.split('/')[:-1]) + '/' for r in saving_paths]
    # Get the timings for each path
    timings = [p.split('_')[-1].split('.')[0] for p in paths]
    
    # Create a file with the paths to each of the newly created goodxenon files
    for i, r in enumerate(root_dir):
    
        # Find all newly created goodxenon files
        gxfiles = glob.glob(r + 'gx*') 

        # Write to file
        f = open(r + 'gxlist_' + timings[i], 'w')
        f.write('\n'.join(gxfiles))
        f.close()
