# Functions to calculate hardness intensity diagrams
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016


def calculate_hi(low_e=2.0,
                 high_e=13.0,
                 soft=(2.0,6.0),
                 hard=(6.0,13.0)):
    '''
    Function to calculate hardness & intensity values.

    Arguments:
        Energy ranges in keV
        - low_e (float): Lower energy boundary for selection
        - high_e (float): Higher energy boundary for selection
        - soft (tuple of floats): Energy range between which to integrate
                                  the soft range
        - hard (tuple of floats): Energy range between which to integrate
                                  the hard range
    '''

    purpose = 'Calculating hardness & intensity values'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import pandas as pd
    import glob
    import xspec
    from collections import defaultdict
    from math import isnan
    from numpy import genfromtxt
    import paths
    import logs
    import execute_shell_commands as shell
    import database

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    # Import data
    os.chdir(paths.data)
    db = pd.read_csv(paths.database)

    # Compile Fortran code for later use
    cmpl = ['gfortran',
            paths.subscripts + 'integflux.f',
            '-o',
            paths.subscripts + 'integflux.xf']
    shell.execute(cmpl)

    # Only want spectra from std2
    d = defaultdict(list)
    for sp, group in db[(db.modes=='std2')].groupby('spectra'):

        # Determine variables
        obsid = group.obsids.values[0]
        path_obsid = group.paths_obsid.values[0]
        bkg_sp = group.spectra_bkg.values[0]
        rsp = group.rsp.values[0]
        fltr = group.filters.values[0]

        print obsid

        # Check whether response file is there
        if not os.path.isfile(rsp):
            print 'ERROR: No response file'
            continue

        # XSPEC Commands to unfold spectrum around flat powerlaw
        # Reason as per Heil et al. (see doi:10.1093/mnras/stv240):
        # "In order to measure the energy spectral hardness independantly of
        # long term changes in the PCA instrument response, fluxes are
        # generated in a model-independant way by dividing the PCA standard
        # 2 mode spectrum by the effective area of the intstrument response
        # in each spectral channel. This is carried out by unfolding the
        # spectrum with respect to a zero-slope power law (i.e. a constant)
        # in the XSPEC spectral-fitting software, and measuring the unfolded
        # flux over the specified energy range (interpolating where the
        # specified energy does not fall neatly at the each of a spectral
        # channel)."
        #xspec.Plot.device = '/xs'

        s1 = xspec.Spectrum(sp)
        s1.background = bkg_sp
        s1.response = os.path.join(paths.data, rsp)
        # Not really sure why you need to do ignore, and then notice
        s1.ignore('**-' + str(low_e+1.) + ' ' + str(high_e-1) + '-**')
        s1.notice(str(low_e) + '-' + str(high_e))
        xspec.Model('powerlaw')
        xspec.AllModels(1).setPars(0.0, 1.0) # Index, Norm
        xspec.AllModels(1)(1).frozen = True
        xspec.AllModels(1)(2).frozen = True
        xspec.Plot('eufspec')

        # Output unfolded spectrum to lists
        e = xspec.Plot.x()
        e_err = xspec.Plot.xErr()
        ef = xspec.Plot.y()
        ef_err = xspec.Plot.yErr()
        model = xspec.Plot.model()

        # Pipe output to file
        eufspec  = path_obsid + 'eufspec.dat'
        with open(eufspec, 'w') as f:
            #Give header of file - must be three lines
            h = ['#Unfolded spectrum',
                 '#',
                 '#Energy EnergyError Energy*Flux Energy*FluxError ModelValues']
            f.write('\n'.join(h) + '\n')
            for i in range(len(e)):
                data = [e[i], e_err[i], ef[i], ef_err[i], model[i]]
                line = [str(j) for j in data]
                f.write(' '.join(line) + '\n')

        # Create a file to input into integflux
        integflux = path_obsid + 'integflux.in'
        with open(integflux, 'w') as f:
            #intgr_low, intgr_high, soft_low, soft_high, hard_low, hard_high
            #line = ['eufspec.dat', 2.0, 60.0, 7.3, 9.8, 9.8, 18.2] #JOEL
            #line = ['eufspec.dat', 2.0, 13.0, 2.0, 6.0, 6.0, 13.0] #ME
            line = ['eufspec.dat',
                    str(low_e),
                    str(high_e),
                    str(soft[0]),
                    str(soft[-1]),
                    str(hard[0]),
                    str(hard[-1])]
            line = [str(e) for e in line]
            f.write(' '.join(line) + '\n')

        # Remove previous versions of the output
        if os.path.isfile(path_obsid + 'hardint.out'):
            os.remove(path_obsid + 'hardint.out')

        # Run fortran script to create calculate hardness-intensity values
        # Will output a file with the columns (with flux in Photons*ergs/cm^2/s)
        # flux flux_err ratio ratio_error
        os.chdir(path_obsid)
        shell.execute(paths.subscripts + 'integflux.xf')
        os.chdir(paths.data)

        # Get ouput of the fortran script
        txt = genfromtxt(path_obsid + 'hardint.out')
        flux = float(txt[0])
        flux_err = float(txt[1])
        ratio = float(txt[2])
        ratio_err = float(txt[3])

        d['spectra'].append(sp)
        d['flux'].append(flux)
        d['flux_err'].append(flux_err)
        d['hardness'].append(ratio)
        d['hardness_err'].append(ratio_err)

        # Clear xspec spectrum
        xspec.AllData.clear()
        os.system('rm ' + rsp + '&')

    # Update database and save
    df = pd.DataFrame(d)
    db = database.merge(db,df,['flux','flux_err','hardness','hardness_err'])
    print 'Number of unique elements in database'
    print '======================='
    print db.apply(pd.Series.nunique)
    print '======================='
    print 'Pipeline completed'
    database.save(db)
    logs.stop_logging()
