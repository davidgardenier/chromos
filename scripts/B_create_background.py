import os
from subprocess import Popen, PIPE, STDOUT

# -----------------------------------------------------------------------------
# --------------------------- Create background -------------------------------
# -----------------------------------------------------------------------------

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

    filters = []
    std2 = []

    # Find the standard2 files
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.Standard2f.xdf'):
                with open(os.path.join(root, f), 'r') as txt:
                    for l in txt:
                        std2.append(l.strip())

    # Without duplicate files
    std2_wd = []
    [std2_wd.append(item) for item in std2 if item not in std2_wd]

    # Determining the path of the filter files
    for s in std2_wd:
        f = s.split('/')
        path = s.split(f[7])[0] + 'stdprod/x'
        filterfile = path + f[6].replace('-','') + '.xfl.gz'
        filters.append(filterfile)

    obsid = ''
    number = 1

    # Basically going through each obsid folder
    for i, f in enumerate(filters):

        # Code to ensure multiple files per obsid don't create a background
        # file with the same name
        new_obsid = std2_wd[i].split('pca')[0][-15:-1]

        if new_obsid == obsid:
            number += 1
        else:
            obsid = new_obsid
            number = 1
        
        # Remove prior versions of the background models
        try:
            os.remove(f.split('std')[0] + object_name + '_bkg_' + str(number))
        except OSError:
            pass

        # Give pcabackest options
        pcabackest = ['pcabackest',
                      'infile=' + std2_wd[i],
                      'outfile=' + f.split('std')[0] + object_name + '_bkg_' + str(number),
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
        p = Popen(pcabackest, stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)

        # Print output of program
        if print_output is True:
            with p.stdout:
                for line in iter(p.stdout.readline, b''):
                    print '    ' + line,
                p.stdout.close()
                p.wait()

    print '---> Completed'
