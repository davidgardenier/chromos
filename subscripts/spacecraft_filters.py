# Creates time filters on basis of properties of the spacecraft, whether
# the electron count wasn't too high, whether it was passing through
# the south Atlantic Anomality etc. Uses the ftool maketime
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def spacecraft_filters():
    '''
    Function to run the ftool maketime over all filter files (.xfl.gz files).
    Creates time_filter.gti files and updates database with path to gti files
    '''

    purpose = 'Create time filters'
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

    # Run maketime for each obsid
    d = defaultdict(list)
    for obsid, group in db.groupby(['obsids']):

        print obsid

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
              'time_since_saa.lt.0.0).and.' +
              'electron2.lt.0.1')

        command = ['maketime',
                   f, # Name of FITS file
                   gti, # Name of output FITS file
                   sel, # Selection expression
                   'compact=no', # Flag yes, if HK format is compact
                   'time="TIME"'] # Column containing HK parameter times

        shell.execute(command)

        d['obsids'].append(obsid)
        d['filters'].append(f)
        d['gti'].append(gti)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['filters','gti'])
    database.save(db)
    logs.stop_logging()
