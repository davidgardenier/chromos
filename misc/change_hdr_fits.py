from astropy.io import fits
import astropy
out = '/scratch/david/master_project/HJ1900d1_2455/P91015/91015-01-01-00/sp.rsp'
sp = '/scratch/david/master_project/HJ1900d1_2455/P91015/91015-01-01-00/std2_16s_per_layer.pha'

hdulist = fits.open(sp)
hdu = hdulist[1]
hdu.header['RESPFILE'] = out
print astropy.__version__
print hdu.header['RESPFILE']
hdu.writeto(sp, clobber=True)

#Check whether it worked
hdulist2 = fits.open(sp)
hdu2 = hdulist[1]
print hdu2.header
print hdu2.header['RESPFILE']

#import fitsio

#sp_fits = fitsio.FITS(sp)
#sp_header = sp_fits['SPECTRUM'].read_header()
#i = 0
#for c in sp_header:
#    print i, c
#    if c=='COMMENT':
#        print sp_header[c]
#    i += 1
#import pyfits
#hdulist = pyfits.open(sp)  # open a FITS file
#prihdr = hdulist[1].header           # the primary HDU header
#print prihdr['RESPFILE']
