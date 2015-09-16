import os

def find_files():
    '''
    Function to obtain a list with paths to corrected light curves for both 
    xray flares and background, if not existant, only the light curves which 
    have been corrected for the background. Also import the rebinned background
    or if available the corrected for xray flares background files.
    
    Output:
     - list with paths to all background corrected data
     - list with paths to all background data
    '''
    
    light_curves = []
    
    folders = [x[0] for x in os.walk('.')]
    upper_level = os.getcwd()

    for d in folders:
        os.chdir(d)
        
        for f in os.listdir('.'):
            
            # If an xray flare was present, use the corrected file minus xray flare
            if f.startswith('power_spectrum_'):
                light_curves.append(os.path.join(os.getcwd(), f))
        os.chdir(upper_level)

    return light_curves

files = find_files()

for i in files:
    os.system('rm ' + str(i))
