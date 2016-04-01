# Functions to create response files on basis of extracted std2 spectra
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016


def create_response():
    '''
    Function to create responses for spectra
    '''

    purpose = 'Creating responses'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from astropy.io import fits
    from collections import defaultdict
    from math import isnan
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    # Only want std2 data
    d = defaultdict(list)
    for sp, group in db[(db.modes=='std2')].groupby('spectra'):

        # Determine variables
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        bkg_sp = group.spectra_bkg.values[0]
        fltr = group.filters.values[0]

        # Check whether extracting per layer
        layers = False
        if sp.endswith('_per_layer.pha'):
            layers = True

        # Setup names
        # Must be short, otherwise it can't be written in the header of the
        # spectrum file
        out = path_obsid + 'sp.rsp'
        #out_bkg = path_obsid + 'sb.rsp'

        print obsid

        # Set up the command for pcarsp
        pcarsp = ['pcarsp',
                  '-f' + sp, #Input
                  '-a' + fltr, #Filter file
                  '-n' + out, #Output file
                  '-s'] #Use smart std2 mode

        # # Set up the command for pcarsp
        # bkgpcarsp = ['pcarsp',
        #              '-f' + bkg_sp, #Input
        #              '-a' + fltr, #Filter file
        #              '-n' + out_bkg, #Output file
        #              '-s'] #Use smart std2 mode

        # Create responses
        shell.execute(pcarsp)
        #shell.execute(bkgpcarsp)

        # pcarsp doesn't allow for long file name to be written in the header
        # of the spectrum, so have to manually do it
        # Must have astropy version >1.0. Trust me.
        hdulist = fits.open(sp, mode='update')
        hdu = hdulist[1]
        hdu.header['RESPFILE'] = out
        hdulist.flush() #.writeto(sp, clobber=True)

        d['spectra'].append(sp)
        d['rsp'].append(out)
        #d['rsp_bkg'].append(out_bkg)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['rsp'])#, 'rsp_bkg'])
    database.save(db)
    logs.stop_logging()
