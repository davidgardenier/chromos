# Creates time filters on basis of properties of the spacecraft, whether
# the electron count wasn't too high, whether it was passing through
# the South Atlantic Anomality etc. Uses the ftool maketime
# Written by David Gardenier, 2015-2016

def spacecraft_filters():
    '''
    Function to run the ftool maketime over all filter files (.xfl.gz files).
    Creates time_filter.gti files and updates database with path to gti files
    '''

    purpose = 'Create time filters'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    from astropy.io import fits
    import os
    import pandas as pd
    import glob
    import numpy as np
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

    # Run maketime for each obsid
    d = defaultdict(list)
    for obsid, group in db.groupby(['obsids']):

        print obsid

        # Check whether an observation has high count rates
        lc = group.paths_obsid.values[0] + 'stdprod/xp' + obsid.replace('-','') + '_n1.lc.gz'
        try:
            hdulist = fits.open(lc)
            data = hdulist[1].data
            _, rate, _, _, _ = zip(*data)
            mean = np.nanmean(rate)
        except IOError:
            mean = 0.

        f = group.paths_obsid.values[0] + 'stdprod/x' + obsid.replace('-','') + '.xfl.gz'
        gti = group.paths_obsid.values[0] + 'time_filter.gti'

        # Remove previous version (maketime doesn't like them)
        try:
            os.remove(gti)
        except OSError:
            pass

        # Selection expression for maketime
        sel = ('elv.gt.10.and.' +
              'offset.lt.0.02.and.' +
              'num_pcu_on.ge.1.and.' +
              '(time_since_saa.gt.10.or.' + #South Atlantic Anomality
              'time_since_saa.lt.0.0)')

        if mean <= 500:
            sel += '.and.electron2.lt.0.1'

        command = ['maketime',
                   f, # Name of FITS file
                   gti, # Name of output FITS file
                   sel, # Selection expression
                   'compact=no', # Flag yes, if HK format is compact
                   'time="TIME"'] # Column containing HK parameter times

        if os.path.exists(f):
            shell.execute(command)
            # Check if gti file is empty (exclude if so)
            hdulist = fits.open(gti)
            data = hdulist[1].data
            if len(data) == 0:
                gti = float('nan')
        else:
            git = float('nan')

        d['obsids'].append(obsid)
        d['filters'].append(f)
        d['gti'].append(gti)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['filters','gti'])
    database.save(db)
    logs.stop_logging()
