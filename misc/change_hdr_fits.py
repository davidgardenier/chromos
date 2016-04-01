from astropy.io import fits
import astropy
out = '/scratch/david/master_project/EXO_0748_676/P40039/40039-02-04-00sp.rsp'
sp = '/scratch/david/master_project/EXO_0748_676/P40039/40039-02-04-00/std2_16s_per_layer.pha'
test = '/scratch/david/master_project/HJ1900d1_2455/P91015/91015-01-01-00/stdprod/xp91015010100_b2.pha.gz'
#hdulist = fits.open(sp)
#hdu = hdulist[1]
#hdu.header['RESPFILE'] = out
#print hdu.header['RESPFILE']
#hdu.writeto(sp, clobber=True)

# pcarsp doesn't allow for long file name to be written in the header
# of the spectrum, so have to manually do it
# Must have astropy version >1.0. Trust me.
hdulist = fits.open(sp, mode='update')
hdu = hdulist[1]
hdu.header['RESPFILE'] = out
hdulist.flush() #.writeto(sp, clobber=True)
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
