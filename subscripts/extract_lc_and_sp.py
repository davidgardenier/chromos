# Functions to extract lightcurves and spectra from RXTE-data
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def seextrct(mode, path_data, gti, output, time_range, channels):
    '''
    Run seextrct over all event and goodxenon mode files. See the cookbooks and
    the manual of seextrct for guidance on the input commands.
    (https://heasarc.gsfc.nasa.gov/ftools/caldb/help/seextrct.txt)
    '''
    import paths
    import execute_shell_commands as shell

    command = ['seextrct',
               'infile=@' + path_data, # Input file name
               'gtiorfile=-', # Input GTI files to be OR'd with INFILE
               'gtiandfile=' + gti, # Input GTI file to be AND'd with INFILE
               'outroot=' + output, # Root name for output file
               'timecol=TIME', # Name of TIME column
               'columns=Event', # Name of COLUMN to be accumulated
               'binsz=0.0078125', # Input the binsize in seconds'
               'printmode=LIGHTCURVE', # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
               'lcmode=RATE', # Type of binning for LIGHTCURVE
               'spmode=SUM', # Type of binning for SPECTRUM
               'timemin=INDEF', # Starting time for summation in seconds
               'timemax=INDEF', # Ending time for summation in seconds
               'timeint=@' + time_range, # Input time intervals t1-t2,t3-t4 in seconds
               'chmin=INDEF', # Minimum energy bin to include in Spectra
               'chmax=INDEF', # Maximum energy bin to include in Spectra
               'chint=' + channels, # Input energy intervals to be retained 0-1,2-255
               'chbin=INDEF'] # Input channels for each bin 0-5,6-255

    # Bitmasks should only be applied to event mode files
    # (and not to goodxenon files, unless layering gx files)
    if mode == 'event':
        command.append('bitfile=' + paths.subscripts + 'bitfile_M')

    shell.execute(command)


def saextrct(mode, path_data, gti, output, time_range, channels, layer):
    '''
    Function to extract a light curve file from binned and std2 files
    '''
    import paths
    import execute_shell_commands as shell

    # Give different time resolutions dependent on mode
    if mode == 'binned':
        b = '0.0078125'
    else:
        b = '16'

    # Change commands on basis of to extract it per layer or not
    if layer is True:
        columns = '@' + paths.subscripts + 'pcu2_columns.txt'
        printmode = 'BOTH'
        channels = 'INDEF'
    else:
        columns = 'GOOD'
        printmode='LIGHTCURVE'

    # Needed for deadtime corrections
#    if mode == 'std1':
#        b = '0.125'
#        columns = '@' + paths.subscripts + 'deadtime_columns.txt'
#        printmode='LIGHTCURVE'

    command = ['saextrct',
               'infile=@' + path_data, # Input file name
               'gtiorfile=-', # Input GTI files to be OR'd with INFILE
               'gtiandfile=' + gti, # Input GTI file to be AND'd with INFILE
               'outroot=' + output, # Root name for output file
               'accumulate=ONE', # Accumulate (ONE) or (MANY) Spectral/Light Curves
               'timecol=TIME', # Name of TIME column
               'columns=' + columns, # Name of COLUMN to be accumulated
               'binsz=' + b, # Input the binsize in seconds
               'printmode=' + printmode, # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
               'lcmode=RATE', # Type of binning for LIGHTCURVE
               'spmode=SUM', # Type of binning for SPECTRUM
               'timemin=INDEF', # Starting time for summation in seconds
               'timemax=INDEF', # Ending time for summation in seconds
               'timeint=@' + time_range, # Input time intervals t1-t2,t3-t4 in seconds
               'chmin=INDEF', # Minimum energy bin to include in Spectra
               'chmax=INDEF', # Maximum energy bin to include in Spectra
               'chint=' + channels, # Input energy intervals to be retained 0-1,2-255
               'chbin=INDEF'] # Input channels for each bin 0-5,6-255

    shell.execute(command)


def extract_lc_and_sp():
    '''
    Function to extract light curves and spectra from data files
    '''

    purpose = 'Extracting light curves & spectra'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    import shutil
    import random
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

    # Backgrounds together with resolutions are the longest list over which one
    # loops - want to prevent having to extract a file which has already been
    # extracted

    d = defaultdict(list)
    for names, df in db.drop_duplicates(['paths_bkg','resolutions']).groupby(['paths_bkg', 'resolutions']):
        path_bkg = names[0]
        res = names[1]

        # Set parameters
        obsid = df.obsids.values[0]
        gti = df.gti.values[0]
        times_pcu = df.times_pcu.values[0]

        # Adapt vaules depending on goodxenon
        mode = df.modes.values[0]
        if mode[:2] == 'gx':
            mode = 'gx'
            path_data = df.paths_gx.values[0]
        else:
            path_data = df.paths_po_pm_pr.values[0]

        # Check if corresponding energy channels have been found
        channels = df.energy_channels.values[0]
        if type(channels)==float:
            if isnan(channels):
                print obsid, mode, res, 'ERROR: No energy channels'
                continue
        if type(times_pcu)==float:
            if isnan(times_pcu):
                print obsid, mode, res, 'ERROR: No pcu times, as no filter file'
                continue

        # You get problems if the file name is longer than 80 characters (incl@)
        filenametoolong = False
        if len(times_pcu) > 79:
            filenametoolong = True
            # Add random number to avoid overwriting files when runnning
            # multiple pipelines
            newname = paths.data + 'times_pcu_' + str(random.random()*1e6)[:5] + '.tmp'
            shutil.copy(times_pcu, newname)
            times_pcu = newname

        # Check whether layering is needed
        layer = False
        if path_bkg.endswith('per_layer.lst'):
            layer = True

        # Set up output names
        output = df.paths_obsid.values[0] + mode + '_' + res
        output_bkg = df.paths_obsid.values[0] + mode + '_' + res + '_bkg'

        if layer is True:
            output += '_per_layer'
            output_bkg += '_per_layer'

        print obsid, mode, res, '--> Extracting Lightcurve'

        # Extract files
        if mode == 'event' or mode =='gx':
            seextrct(mode, path_data, gti, output, times_pcu, channels)
        if mode == 'std2' or mode == 'binned':
            saextrct(mode, path_data, gti, output, times_pcu, channels, layer)

        # Run saextrct for background files
        saextrct('std2',path_bkg, gti, output_bkg, times_pcu, channels, layer)

        # Check if extraction worked or not
        lc = output + '.lc'
        lc_bkg = output_bkg + '.lc'
        if not (os.path.isfile(lc) or os.path.isfile(lc_bkg)):
            print 'ERROR: Lightcurve not created'
            continue
        if layer:
            sp = output + '.pha'
            sp_bkg = output_bkg + '.pha'
            if not (os.path.isfile(sp) or os.path.isfile(sp_bkg)):
                print 'ERROR: Spectrum not created'
                continue
        else:
            sp = float('NaN')
            sp_bkg = float('NaN')

        if filenametoolong:
            os.remove(times_pcu)

        d['paths_bkg'].append(path_bkg)
        d['resolutions'].append(res)
        d['lightcurves'].append(lc)
        d['lightcurves_bkg'].append(lc_bkg)
        d['spectra'].append(sp)
        d['spectra_bkg'].append(sp_bkg)

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['lightcurves','lightcurves_bkg','spectra','spectra_bkg'])
    database.save(db)
    logs.stop_logging()
