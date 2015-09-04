import os
from subprocess import Popen, PIPE, STDOUT

# -----------------------------------------------------------------------------
# --------------------------- Create background -------------------------------
# -----------------------------------------------------------------------------

object_name = 'aquila'


def create_background(object_name, print_output=False):
    '''
    Function to create background filters using pcabackest. Goes through 
    .xfl.gz and .Standard2f.xdf files to be able to create background files in
    each obsid folder, called <objectname>_bkg. Ensure create_filters() has
    been run beforehand, as well as get_event_mode.
    
    Arguments:
     - object_name: name of the observed object (needed to find files)
     - print_output: if true, will print the output of pcabackest
    
    '''

    # First the filter files must be found, as well as the Standard2 files
    filters = []
    std2 = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.xfl.gz'):
                filters.append(os.path.join(root, f))
            if f.endswith('.Standard2f.xdf'):
                with open(os.path.join(root, f), 'r') as txt:
                    for l in txt:
                        std2.append(l.strip())


    # Basically going through each obsid folder
    for i, f in enumerate(filters):
        
        # Remove prior versions of the background models
        try:
            os.remove(f.split('std')[0] + object_name + '_bkg')
        except OSError:
            pass
        
        # Give pcabackest options
        pcabackest = ['pcabackest',
                      'infile=' + std2[i],
                      'outfile=' + f.split('std')[0] + object_name + '_bkg',
                      'filterfile=' + f,
                      'modelfile=./scripts/pca_bkgd_cmbrightvle_eMv20051128.mdl',
                      'saahfile=./scripts/pca_saa_history.gz',
                      'modeltype=both',
                      'interval=16',
                      'propane=no',
                      'layers=no',
                      'gaincorr=yes',
                      'gcorrfile=caldb',
                      'fullspec=yes',
                      'interp=yes',
                      'syserr=no',
                      'clobber=yes',
                      'mode=no']
        
        # Execute pcabackest
        p = Popen(pcabackest, stdout=PIPE, stdin=PIPE,
                  stderr=STDOUT, bufsize=1)

        # Print output of program
        if print_output is True:
            with p.stdout:
                for line in iter(p.stdout.readline, b''):
                    print line,
                p.stdout.close()
                p.wait()

    print '----------- \n Successfully created background files'


if __name__ == '__main__':
    create_background(object_name, print_output=False)
