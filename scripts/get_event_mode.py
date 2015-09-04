import os
from subprocess import Popen, PIPE

# -----------------------------------------------------------------------------
# -------------------------- Get Event modes ----------------------------------
# -----------------------------------------------------------------------------

object_name = 'aquila'


def determine_files(object_name, print_output=False):
    '''
    Function to determine which files are needed for event mode. 
    Creates a file named <object>.obsid.list containing the paths to the
    different modes in each P<number> folder
    
    Required:
     - Cshell script xtescan2 in same working directiory as this script
     
    Arguments:
     - object_name: for file creation
     - print_output: if True, will print the output of xtescan2 function
    '''

    for folder in os.listdir('.'):
        if folder.startswith('P'):
            subfolder = os.path.join('./', folder)
            
            if print_output is True:
                print '-----------' 
            
            obsid = []

            # Find obsids
            for dirs in os.listdir(subfolder):
                if dirs[-1].isdigit() and len(dirs) > 9:
                    obsid.append(dirs)
                    if print_output is True:
                        print 'Found: ', dirs

            # Write them to list to give to xtescan2
            with open(subfolder + '/obsid.lst','w') as f:
                f.write('\n'.join(obsid))
                if print_output is True:
                    print 'Written to obsid.lst \n-----------'
            
            # Execute xtescan2
            os.chdir(subfolder)
            p = Popen(['csh','./../scripts/xtescan2','obsid.lst', object_name], stdout=PIPE)
            
            # Print output
            if print_output is True:
                for line in p.stdout:
                    print line
            p.wait()

            f.close()
            os.chdir('./../')
            
    print '----------- \n Successfully extracted data files'


if __name__ == '__main__':
    determine_files(object_name, print_output=False)
