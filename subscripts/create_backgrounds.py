# Functions to create a background files for each standard2 data file, and
# create a list of paths directing to these piles. Uses the ftool pcabackest
# to create the backgrounds.
# Written by David Gardenier, 2015-2016

def pcabackest(mode,infile,outfile,filt,allpcus=True):
    '''
    Determine input commands for pcabackest
    '''

    import paths
    import execute_shell_commands as shell

    gaincorr = 'yes'
    gcorrfile = 'calb'
    fullspec = 'yes'
    layers = 'no'

    if mode[:2] == 'gx':
        gaincorr = 'no'
    if (mode == 'std2' or mode=='std1') and allpcus is True:
        gaincorr = 'no'
        fullspec = 'no'
    if mode == 'std2' and allpcus is False:
        gaincorr = 'no'
        fullspec = 'no'
        layers = 'yes'

    # Set up the command for pcabackest
    pcabackest = ['pcabackest',
                  'infile=' + infile,
                  'outfile=' + outfile,
                  'filterfile=' + filt,
                  'modelfile=' + paths.subscripts + 'pca_bkgd_cmbrightvle_eMv20051128.mdl',
                  'saahfile=' + paths.subscripts + '/pca_saa_history.gz',
                  'modeltype=both',
                  'interval=16',
                  'propane=no',
                  'layers=' + layers,
                  'gaincorr=' + gaincorr,
                  'fullspec=' + fullspec,
                  'interp=yes',
                  'syserr=no',
                  'clobber=yes',
                  'mode=no']

    if gaincorr == 'yes':
        pcabackest.extend(['gcorrfile=caldb'])

    shell.execute(pcabackest)


def create_backgrounds():
    '''
    Function to create a background files for each standard2 data file, and
    create a list of paths directing to these piles. Uses the ftool pcabackest
    to create the backgrounds.
    '''

    purpose = 'Creating background files'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from collections import defaultdict
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    d = defaultdict(list)
    for obsid, group in db.groupby(['obsids']):
        path_obsid = group.paths_obsid.values[0]

        for mode, modegroup in group.groupby('modes'):
            print obsid, mode
            # Don't overdo pcabackest - will be same for gx1 or gx2
            if mode == 'gx1':
                mode = 'gx'
            if mode == 'gx2':
                continue

            n = 0
            # To ensure you're not running more times than necessary
            ngroup = group[group.modes=='std2'].drop_duplicates('paths_data')
            if ngroup.shape[0]==0:
                print 'ERROR: No standard-2 files for this obsid'
                continue

            # Keep track of files you'll create
            bkgs = []
            bkgs_per_layer = []

            for i, r in ngroup.iterrows():
                n += 1

                # Note infile is always a std2-data file, but not always the same mode!
                infile = r.paths_data
                outfile = r.paths_obsid + 'bkg_' + mode + '_' + str(n)
                bkgs.append(outfile)
                filt = r.filters

                pcabackest(mode,infile,outfile,filt)

                # Make special backgrounds for when you extract spectra per layer
                if mode == 'std2':
                    outfile = r.paths_obsid + 'bkg_' + mode + '_' + str(n) + '_per_layer'
                    bkgs_per_layer.append(outfile)
                    pcabackest(mode,infile,outfile,filt,allpcus=False)

            # Save a list of all the files pcabackest has created
            outfile = path_obsid + 'bkg_' + mode + '.lst'
            with open(outfile, 'w') as text:
                text.write('\n'.join(bkgs) + '\n')

            # Ugly, I know
            if mode == 'gx':
                d['obsids'].append(obsid)
                d['modes'].append('gx2')
                d['paths_bkg'].append(outfile)
                mode = 'gx1'

            d['obsids'].append(obsid)
            d['modes'].append(mode)
            d['paths_bkg'].append(outfile)

            # Ugly way of getting the files for the layered background
            if mode == 'std2':
                outfile = path_obsid + 'bkg_std2_per_layer.lst'
                with open(outfile, 'w') as text:
                    text.write('\n'.join(bkgs_per_layer) + '\n')
                d['obsids'].append(obsid)
                d['modes'].append(mode)
                d['paths_bkg'].append(outfile)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['paths_bkg'])
    database.save(db)
    logs.stop_logging()
