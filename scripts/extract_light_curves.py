import os
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime

# -----------------------------------------------------------------------------
# ------------------------- Extract lightcurves -------------------------------
# -----------------------------------------------------------------------------

object_name = 'aquila'


def energy_to_channel(epoch, table, energy):
    '''
    Function determine which channel corresponds best to an energy
    
    Arguments:
     - epoch in which measurement took place
     - table in which to look
     - energy which needs to be converted to a channel number
     
    Output:
     - channel number closest to the energy given
    '''
    
    # Split between the epochs 1&2&3&4 and 5.
    # Epoch 5 has two columns for different PCU1 and the others, however only
    # the latter column is taken, which strictly speaking is only for PCU123,4
    
    if epoch < 5:
        column = epoch + 1
    else:
        column = -1
    
    # Make a list of energies
    energies = [float(i.split()[column]) for i in table]
    
    # Compare the energy value to the energies list
    for i, e in enumerate(energies):
        if e > energy:
        
            # Check which element is closer to the energy
            above = energies[i]-energy
            below = energies[i-1]-energy
            
            # Return the associated channel number of that energy
            if abs(above) < abs(below):
                channel = table[i].split()[0]
            else:
                channel = table[i-1].split()[0]
            
            # Ensure the lowest energy channel is not returned
            # See Gleissner T., Wilms J., Pottschimdt K. etc. 2004
            if channel == '0-4':
                channel = table[1].split()[0]
            
            # Return the channel
            return channel


def calculated_energy_range(date,min_energy,max_energy):
    '''
    Import the channel energy conversion table, and return the required channel
    range in a format suitable for seextrct.
    
    Requires:
     - ./energy_channel_conversion.txt
    
    Arguments:
     - date at which the observation took place (in form 2001-06-28T15:36:23)
     - lowest energy in keV
     - highest energy in keV
    
    Output:
     - Channel range
    '''
    
    with open('./../../scripts/energy_channel_conversion.txt', 'r') as txt:
        text = list(txt)
        stop_dates = [x + y for x, y in zip(text[2].split()[2:6], text[3].split()[2:6])]
        end_dates = [datetime.strptime(t, '%m/%d/%y(%H:%M)') for t in stop_dates]
    
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        
        if date < end_dates[0]:
            epoch = 1
        elif date < end_dates[1]:
            epoch = 2
        elif date < end_dates[2]:
            epoch = 3
        elif date < end_dates[3]:
            epoch = 4
        else:
            epoch = 5
        
        lower_range = energy_to_channel(epoch, text[12:], min_energy)
        upper_range = energy_to_channel(epoch, text[12:], max_energy)
        
    return str(lower_range) + '-' + str(upper_range)


def extract_light_curve(object_name, extrct_event_mode=True, 
                        extrct_background=True, print_output=False):
    '''
    Function to extract lightcurves for each obsid. These are placed in the
    obsid folders with the file name firstlight_<unit of time>.lc. While some
    errors will be caught, print output if unsure.
    
    Creates:
     - lightcurves files in each obsid folder, per time bin
     
    Arguments:
     - object_name: name of object
     - extrct_event_mode: whether the function should execute seextrct to 
                          extract the data to a light curve
     - extrct_background: whether the function should exectute seaxtrct to 
                          extract the background to data
     - print_output: prints the output of the seextrct program
    '''

    # Go through P<number> folders
    for folder in os.listdir('.'):
        if folder.startswith('P'):
            subfolder = os.path.join('./', folder)
            
            # List files in one of these P<number> folders
            for files in os.listdir(subfolder):
                # List of event mode files
                if files.startswith(object_name + '.E_') and files.endswith('.xdf'):
                
                    # Check whether it's an M - the only bitfile I have implemented
                    if files.split('E_')[1][8] != 'M':
                        print 'Woah, you\'ll need a different bitfile'
                        return
                        
                    # Extract lightcurve
                    else:
                        
                        # Extract the dates on which the observations took place
                        text_for_date = open(subfolder + '/' + files[:-4] + '.list', 'r')
                        dates = []
                        for line in text_for_date:
                            dates.append(line.split()[2])
                        # Date counter
                        d = 0
                        
                        # Open the previously created file with paths to lightcurves
                        text = open(subfolder + '/' + files, 'r')
                                                
                        for line in text:
                            os.chdir('./' + line.split('data')[1].split('pca')[0])
                            
                            # Let you know which file it's working on 
                            if print_output is True:
                                print '-----------------------\n Working on', os.getcwd(), '\n-----------------------'
                            
                            
                            # Time resolution
                            time_resolution = files.split('_')[1]
                            
                            # Current date:
                            date = dates[d]
                            
                            if extrct_event_mode:
                                print os.getcwd()
                                # Execute seextrct with the required bitfile
                                p = Popen(['seextrct','bitfile=./../../scripts/bitfile_M'],
                                          stdout=PIPE, stdin=PIPE, stderr=STDOUT,
                                          bufsize=1)                        
                            
                                # Give the required input
                                # -----------------------
                                # Input file name
                                p.stdin.write(line)
                                # Input GTI files to be OR'd with INFILE 
                                p.stdin.write('- \n')
                                # Input GTI file to be AND'd with INFILE 
                                p.stdin.write('basic_' + time_resolution + '.gti \n')
                                # Root name for output file
                                p.stdin.write('firstlight_' + time_resolution + ' \n')
                                # Name of TIME column
                                p.stdin.write('TIME \n')
                                # Name of COLUMN to be accumulated
                                p.stdin.write('Event \n')
                                # Input the binsize in seconds
                                p.stdin.write('0.0078125 \n')   
                                # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
                                p.stdin.write('LIGHTCURVE \n')
                                # Type of binning for LIGHTCURVE
                                p.stdin.write('RATE \n')
                                # Type of binning for SPECTRUM
                                p.stdin.write('SUM \n')
                                # Starting time for summation in seconds
                                p.stdin.write('INDEF \n')
                                # Ending time for summation in seconds 
                                p.stdin.write('INDEF \n')
                                # Input time intervals t1-t2,t3-t4 in seconds 
                                p.stdin.write('INDEF \n')
                                # Minimum energy bin to include in Spectra
                                p.stdin.write('INDEF \n')
                                # Maximum energy bin to include in Spectra
                                p.stdin.write('INDEF \n')
                                # Input energy intervals to be retained 0-1,2-255 
                                p.stdin.write(calculated_energy_range(date,2,13) + ' \n')
                                # Input channels for each bin 0-5,6-255
                                p.stdin.write('INDEF \n')

                                # Print output of program
                                with p.stdout:
                                    for oline in iter(p.stdout.readline, b''):
                                    
                                        # Ensure an aborting error is caught and displayed
                                        if oline.strip()=='Aborting...':
                                            print 'Had to abort while working on a file of type ' + files.split('_')[1] + ':\n', line
                                        elif print_output is True:
                                            print oline,
                                    p.stdout.close()
                                    p.wait()
                            
                            # If you also want to extract the light curves
                            # of the background files, then run 
                            # extract_background
                            if extrct_background:
                                extract_background(object_name, print_output, time_resolution, date)
    
                            # Date counter (to loop through list of dates)    
                            d += 1
                            
                            os.chdir('./../../')

    print '----------- \n Created lightcurves'


def extract_background(object_name, print_output, time_resolution, date):
    '''
    Function to extract a light curve file from background files
    '''

    # Let you know which file it's working on 
    if print_output is True:
        print '-----------------------\n Working on background file', os.getcwd(), '\n-----------------------'

    # Execute seextrct with the required bitfile
    p = Popen(['saextrct'], stdout=PIPE, stdin=PIPE, stderr=STDOUT,
              bufsize=1)                        

    # Give the required input
    # -----------------------
    # Input file name
    p.stdin.write(object_name + '_bkg \n')
    # Input GTI files to be OR'd with INFILE 
    p.stdin.write('APPLY \n')
    # Input GTI file to be AND'd with INFILE 
    p.stdin.write('basic_' + time_resolution + '.gti \n')
    # Root name for output file
    p.stdin.write('background_' + time_resolution + ' \n')
    # Accumulate (ONE) or (MANY) Spectral/Light Curves
    p.stdin.write('ONE \n')
    # Name of TIME column
    p.stdin.write('TIME \n')
    # Name of COLUMN to be accumulated
    p.stdin.write('GOOD \n')
    # Input the binsize in seconds
    p.stdin.write('16 \n')
    # Chose print option, LIGHTCURVE, SPECTRUM, or BOTH
    p.stdin.write('LIGHTCURVE \n')
    # Type of binning for LIGHTCURVE
    p.stdin.write('RATE \n')
    # Type of binning for SPECTRUM
    p.stdin.write('SUM \n')
    # Starting time for summation in seconds
    p.stdin.write('INDEF \n')
    # Ending time for summation in seconds 
    p.stdin.write('INDEF \n')
    # Input time intervals t1-t2,t3-t4 in seconds 
    p.stdin.write('INDEF \n')
    # Minimum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Maximum energy bin to include in Spectra
    p.stdin.write('INDEF \n')
    # Input energy intervals to be retained 0-1,2-255
    p.stdin.write(calculated_energy_range(date,2,13) + ' \n')
    # Input channels for each bin 0-5,6-255
    p.stdin.write('INDEF \n')

    # Print output of program
    with p.stdout:
        for oline in iter(p.stdout.readline, b''):
        
            # Ensure an aborting error is caught and displayed
            if oline.strip()=='Aborting...':
                print 'Had to abort while working on a file of type ' + files.split('_')[1] + ':\n', line
            elif print_output is True:
                print oline,
        p.stdout.close()
        p.wait()
    
                
if __name__ == '__main__':
    extract_light_curve(object_name, print_output=False)
