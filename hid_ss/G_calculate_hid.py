import json
import glob
import os
from subprocess import Popen, PIPE, STDOUT
import xspec

def create_hid(DATA, SCRIPTS, verbose=False):
    '''
    Function to create a Hardness-Intensity diagram
    Search for RANGE to find all instances of integration & energy ranges
    '''

    # Print purpose of program
    purpose = 'Creating a hardness-intensity diagram'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    # Compile fortran code
    cmpl = ['gfortran', SCRIPTS + 'integflux.f', '-o', SCRIPTS + 'integflux.xf']
    print ' '.join(cmpl)
    os.system(' '.join(cmpl))

    # Find all filter files and add to dictionary
    for obsid in d:
        if 'std2' in d[obsid].keys():
            mode = 'std2'
            path = d[obsid][mode]['path_sp'][0]
            bkg_path = d[obsid][mode]['path_bkg_sp'][0]
            root = os.getcwd() + path.split('std2')[0].split('.')[1]

            print obsid, '\n=============='

            # Test if spectrum file exists
            test = os.path.isfile
            if test(path) is False or test(bkg_path) is False:
              continue

            # XSPEC Commands to unfold spectrum around flat powerlaw
            #xspec.Plot.device = '/xs'
            s1 = xspec.Spectrum(path)
            s1.background = bkg_path
            # Not really sure why you need to do ignore, and then notice
            s1.ignore('**-3.0 13.0-**') #RANGE
            s1.notice('2.0-13.0') #RANGE
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
            eufspec  = root + 'eufspec.dat'
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
            integflux = root + 'integflux.in'
            with open(integflux, 'w') as f:
                line = ['eufspec.dat', 2.0, 13.0, 2.0, 6.0, 6.0, 13.0] #RANGE
                line = [str(e) for e in line]
                f.write(' '.join(line) + '\n')

            # Remove hardness intensity file if existing
            if test(root + 'hardint.out'):
                os.remove(root + 'hardint.out')

            # Run fortran script to create calculate hardness-intensity values
            # Will output a file with the columns
            # flux_low flux_high ratio ratio_error
            os.chdir(root)
            os.system(SCRIPTS + 'integflux.xf')
            os.chdir(DATA)

            # Add path to file
            d[obsid][mode]['hardint'] = [root + 'hardint.out']

            # Clear xspec spectrum
            xspec.AllData.clear()

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Calculated hardness-intensity values for all files'
