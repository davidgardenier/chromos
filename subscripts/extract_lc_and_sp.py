def extract_lc_and_sp():
    '''
    Function to determine the channel range needed for input during extraction.
    Requires the file energy_conversion_table.txt to determine the initial
    channel selection.
    '''

    purpose = 'Finding the correct channels for later extraction'
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

    for names, group in db.groupby(['obsids', 'modes']):
        obsid = names[0]
        mode = names[1]

        # For each path of a list of paths to event/goodmode mode
        # files (may be more than one if there are different
        # resolutions within one obsid)
        for index, row in group.iterrows():
            print mode, row.paths_po_pm_pr
