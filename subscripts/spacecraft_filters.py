def spacecraft_filters():
    '''
    Function to run the ftool maketime over all filter files (.xfl.gz files).
    Creates time_filter.gz files and updates database with path to gti files
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

    # Determine filter files
    db['filters'] = db.paths_obsid + 'stdprod/x' + db.obsids.str.replace('-','') + '.xfl.gz'
    db['gti'] = db.paths_obsid + 'time_filter.gti'

    # Run maketime for each obsid
    for f, gti, obsid in zip(db.filters.unique(), db.gti, db.obsids):

            print obsid

            # Remove previous version (maketime doesn't like them)
            try:
                os.system('rm ' + gti)
            except OSError:
                continue

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

    database.save(db)
    logs.stop_logging()
