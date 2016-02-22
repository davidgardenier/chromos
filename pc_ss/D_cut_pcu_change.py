from astropy.io import fits
import json
import os
from subprocess import Popen, PIPE, STDOUT

def cut_pcu_change(verbose=False):
    '''
    Function to determine if pcu changes have take place, and if so cut 32s
    around them. Returns a string suitable for input in extracting lightcurves.
    '''

    # Let the user know what's going to happen
    purpose = 'Determine if number of PCUs has changed'
    print purpose + '\n' + '='*len(purpose)

    # Import data
    with open('./info_on_files.json', 'r') as info:
        d = json.load(info)

    for obsid in d:
        print obsid
        path = d[obsid]['filter']['paths'][0]

        # Import data
        hdulist = fits.open(path)
        tstart = hdulist[0].header['TSTART']
        timezero = hdulist[0].header['TIMEZERO']
        num_pcu_on = hdulist[1].data.field('NUM_PCU_ON')
        time = hdulist[1].data.field('Time')
        # Remember time has an offset due to spacecraft time
        time -= time[0]
        #time += tstart + timezero

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

        if verbose:
            print '    ', obsid, '-->', t_range

        output = path.split('std')[0] + 'pcu.tint'

        time_command = ['timetrans',
                        '-i', # Input file
                        path,
                        '-f', # Output file
                        output,
                        '-t', # Time range
                        t_range]

        # Execute timetrans
        p = Popen(time_command, stdout=PIPE, stdin=PIPE,
                  stderr=STDOUT, bufsize=1)

        # Print output of program
#        if verbose:
#            with p.stdout:
#                for line in iter(p.stdout.readline, b''):
#                    print '        ' + line,
#                p.stdout.close()
#                p.wait()

        d[obsid]['filter']['time_range'] = output

    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))

    print '---> Determined if PCU changes have taken place'
