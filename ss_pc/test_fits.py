from astropy.io import fits

path = '/scratch/david/master_project/full_data/P60054/60054-02-02-01/pca/FS3f_e1a6f09-e1a7446.gz'

print fits.open(path)[1].header['TDDES2']
