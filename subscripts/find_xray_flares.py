# Functions to detect when an X-ray flare happens and to cut around it
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def cut_xray_flares():
    '''
    Function to find X-ray flares in a light curve by finding when the rate
    exceeds more than 7sigma, and then cut around it. Write output to a file
    in an obsid-folder with the name corrected_rate_minus_xray_flare_
    <timingresolution>.dat if an X-ray flare was detected
    '''

    # Let the user know what's going to happen
    purpose = 'Determining X-ray flares'
    print purpose + '\n' + '='*len(purpose)
