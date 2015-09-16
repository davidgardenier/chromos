import os

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.startswith('corrected_rate_minus') or f.startswith('corrected_bkg_rate_minus'):
            print root, f
            os.system('rm ' + root + '/' + f)
