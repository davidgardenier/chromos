def pcu_filters():
    '''
    Function to determine if pcu changes have take place, and if so cut 32s
    around them. Used the times scripts to save the times of pcu changes to
    a database
    '''

    purpose = 'Determine if number of PCUs has changed'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    from astropy.io import fits
    from collections import defaultdict
    import paths
    import logs
    import execute_shell_commands as shell
    import database
    import filters

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    d = defaultdict(list)
    for obsid, path, filt in zip(db.obsids.unique(), db.paths_obsid, db.filters):

        # Import data
        hdulist = fits.open(filt)
        tstart = hdulist[0].header['TSTART']
        timezero = hdulist[0].header['TIMEZERO']
        num_pcu_on = hdulist[1].data.field('NUM_PCU_ON')
        time = hdulist[1].data.field('Time')
        # Remember time has an offset due to spacecraft time
        time -= time[0]
        time += tstart + timezero
        # Counter to determine when the number of pcus changes
        pcu = num_pcu_on[0]
        # The acceptable time range
        t_range = repr(time[0]) + '-'

        for i, n in enumerate(num_pcu_on):
            # Check if the number of pcus has changed
            if n != pcu:

                pcu = n

                # Cut 32s around it
                low_t = time[i] - 16
                high_t = time[i] + 16
                previous_t = float(t_range.split('-')[-2].split(',')[-1])

                # Check whether there's any overlap
                if low_t <= previous_t:
                    # Replace the previous upper time if there is
                    t_range = t_range.replace(t_range.split('-')[-2].split(',')[-1], repr(high_t))
                    continue
                else:
                    t_range += repr(low_t) + ','

                # Check whether you've reached the end
                if high_t > time[-1]:
                    t_range = t_range[:-1]
                    break
                else:
                    t_range += repr(high_t) + '-'

        if t_range[-1] == '-':
            t_range += repr(time[-1])

        print obsid, '-->', t_range

        # Bit convoluted method to get the times, but couldn't be bothered
        # changing my previous code which took ages to debug
        '''
        t = []
        for v in t_range.replace('-',' ').replace(',',' ').split():
            try:
                t.append(float(v))
            except ValueError:
                pass

        pcu_h = t[0:][::2],
        pcu_l = t[1:][::2]

        filters.addtimes(obsid, 'pcu', pcu_h, pcu_l)
        '''

        d['obsids'].append(obsid)
        d['times_obsid'].append(str(tstart+timezero) + '-' + str(time[-1]))
        d['times_pcu'].append(t_range)

    # Add starting times of each obsid to database
    df = pd.DataFrame(d)
    db = database.merge(db,df,['rxte_time', 'times_pcu'])
    database.save(db)