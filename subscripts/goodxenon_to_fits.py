# Function to convert goodxenon files to fits files
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def goodxenon_to_fits():
    '''
    Function to convert GoodXenon files to fitsfiles using make_se. Subsequently
    groups the paths to the produced files into a file
    path_gxfits_<resolution> and updates db.
    '''

    purpose = 'Converting GoodXenon files to fits files'
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

    # Running it over gx1 or gx2 will give same result, but only needs to be
    # run once
    if 'gx1' not in db.modes.unique():
       print 'No GoodXenon files found'
       return

    # Run maketime for each obsid
    sdb = db[db.modes=='gx1']

    sdb['gxfits'] = sdb.paths_obsid + 'gxfits_' + sdb.resolutions

    # Create a list of the gxfits files
    d = defaultdict(list)

    for i, row in sdb.iterrows():
        # Create goodxenon fits files
        command = ['make_se',
                   '-i', #Input file with list to gx1 and gx2 files
                   row.paths_po_pm_pr,
                   '-p', #Output the prefix for the goodxenon files
                   row.gxfits
                   ]

        shell.execute(command)

        gxfiles = row.paths_obsid + 'gxfits_' + row.resolutions + '*'
        paths_gx = glob.glob(gxfiles)

        d['obsids'].append(row.obsids)
        d['modes'].append(row.modes)
        d['resolutions'].append(row.resolutions)
        path_gx = row.paths_obsid + 'paths_gxfits_' + row.resolutions
        d['paths_gx'].append(path_gx)

        with open(path_gx, 'w') as text:
            text.write('\n'.join(paths_gx) + '\n')

    # Ensure gx2 has the same data as gx1
    for k in d:
        if k != 'modes':
            d[k].extend(d[k])
        else:
            d[k].extend(['gx2' for g in d[k]])
    df = pd.DataFrame(d)

    # Ensure that the column paths_gx is updated
    db = database.merge(db,df,['paths_gx'])

    database.save(db)
    logs.stop_logging()
