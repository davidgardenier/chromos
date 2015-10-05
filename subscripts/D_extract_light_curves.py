import glob
import os

PATH = '/scratch/david/master_project/full_data/'
objectname = 'aquila'

os.chdir(PATH)

def extract_lightcurves():
    
    # Find all obsids
    initial_obsids = sorted([r.split('/')[-1] for r in glob.glob('./*/?????-??-??-*')])
    # Getting rid of obsids with letters at the end
    obsids = [o for o in initial_obsids if o[-1].isdigit()]
    # Form into dictionary
    d = {el:[] for el in obsids}
    
    # Look into each directory and find all type of files contained within
    for o in d:
        d[o].extend(glob.glob('./*/' + o + '/event_mode_*'))
        d[o].extend(glob.glob('./*/' + o + '/' + objectname + '_bkg.list'))
        d[o].extend(glob.glob('./*/' + o + '/gxlist_*'))
    
    # For each obsid
    for o in d:
    
        # Give the user some information
        print '--------------'
        print o
        
        # Ensure there's always more than just a background file present
        if len(d[o]) == 1:
            print 'Only background'
            continue
        
        for f in d[o]:
            if 'event_mode' in f:
                print 'E'
            if 'bkg' in f:
                print 'B'
            if 'gxlist' in f:
                print 'GX'
        #print '------------'

extract_lightcurves()
