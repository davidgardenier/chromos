import os

PATH = '/scratch/david/master_project/full_data/'

def find_light_curves():
    '''
    Function to obtain a list with paths to all light curves & backgrounds
    
    Output:
     - list with paths to all lightcurves & backgrounds
    '''
    
    light_curves = []
    backgrounds = []
    os.chdir(PATH)
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.startswith('firstlight') and f.endswith('.lc'):
                light_curves.append(os.path.join(root, f))
            if f.startswith('rebinned_background_') and f.endswith('.dat'):
                backgrounds.append(os.path.join(root, f))
                
    return light_curves, backgrounds
    
a, b = find_light_curves()

for i in range(len(a)):
    print a[i], b[i]
