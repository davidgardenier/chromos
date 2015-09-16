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
    backgrounds = []
    
    folders = [x[0] for x in os.walk('.')]
    upper_level = os.getcwd()

    for d in folders:
        os.chdir(d)
        xray_flare = False
        
        for f in os.listdir('.'):
            
            # If an xray flare was present, use the corrected file minus xray flare
            if f.startswith('corrected_rate_minus_xray_flares_') and f.endswith('.dat'):
                light_curves.append(os.path.join(os.getcwd(), f))
                xray_flare = True
            # If there was an xray flare, there should be a background
            # which had been corrected for the flare
            if f.startswith('corrected_bkg_rate_minus_xray_flares_') and f.endswith('.dat'):
                backgrounds.append(os.path.join(os.getcwd(), f))
                xray_flare = True
           
            else:
                continue
                
        os.chdir(upper_level)

    return light_curves, backgrounds

files = find_files()[0] + find_files()[1]

for i in files:
    os.system('rm ' + str(i))
