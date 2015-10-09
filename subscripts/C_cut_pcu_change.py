from astropy.io import fits
import json
import os

def cut_pcu_change(print_output=False):
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
        path = d[obsid]['filter']['paths'][0]

        # Import data
        hdulist = fits.open(path)
        tstart = hdulist[0].header['TSTART']
        timezero = hdulist[0].header['TIMEZERO']
        num_pcu_on = hdulist[1].data.field('NUM_PCU_ON')
        time = hdulist[1].data.field('Time')
        # Remember time has an offset due to spacecraft time
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
                symbol = '-'
                
                # TAKE CARE: Have not built in what would happen if the number
                # of PCUs would change rapidly -> The high_t of one may be larger
                # than the low_t of another... This has not been tested
                # This could be used: previous_t = t_range[-19:-1]
                
                # Careful of going beyond the total time range
                if low_t > time[0]:
                    t_range += repr(low_t) + ','
                # If low_t is smaller than the initial t, use the high boundary
                else:
                    t_range = repr(high_t) + '-'
                    continue
                 
                if high_t < time[-1]:
                    t_range += repr(high_t) + '-'
                # If high_t is larger than the last t, strip the comma off the end
                else:
                    t_range = t_range[:-1]
                    break

        if t_range[-1] == '-':
            t_range += repr(time[-1])

        if print_output:
            print '    ', obsid, '-->', t_range

        d[obsid]['filter']['time_range'] = t_range
        
    # Write dictionary with all information to file
    with open('./info_on_files.json', 'w') as info:
        info.write(json.dumps(d))
        
    print '---> Determined if PCU changes have taken place'
        
