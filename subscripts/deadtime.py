# Functions to determine the Poisson noise level with dead-time correction
# Written by David Gardenier, davidgardenier@gmail.com, 2016-2017

def calculate_deadtime(std1path, f, npcu=5, vle_correction='mean'):
    '''
    Function to calculate the deadtime correction factor upon being given the
    path, array with frequencies and number of pcus
    
    Based partially on a script written by Daniella Huppenkothen
    (see https://github.com/dhuppenkothen/RXTEAnalysis/)
    '''

    import pandas as pd
    import pyfits
    from numpy import sin, cos, pi, mean
        
    hdulist = pyfits.open(std1path)
    data = hdulist[1].data
    header = hdulist[1].header
        
    vlecnt = data["VLECnt"].flatten()
    
    # Good Xenon events
    xecntpcu0 = data["XeCntPcu0"].flatten()
    xecntpcu1 = data["XeCntPcu1"].flatten()
    xecntpcu2 = data["XeCntPcu2"].flatten()
    xecntpcu3 = data["XeCntPcu3"].flatten()
    xecntpcu4 = data["XeCntPcu4"].flatten()
    xecnt = xecntpcu0+xecntpcu1+xecntpcu2+xecntpcu3+xecntpcu4
    
    # Propane layer events
    vpcnt = data["VpCnt"].flatten()

    # Coincident events
    remainingcnt = data["RemainingCnt"].flatten()
    
    # Total events
    totalcnt = vlecnt + xecnt + vpcnt + remainingcnt

    # Default VLE window
    tau = 1.7e-4
    # Bin size
    tb = 0.0078125
    # Nyquist frequency
    fnyq = 64
    # Dead time
    td = 1.0e-5
    # Total number of frequencies
    N = len(f)
    
    # Method of correction (could be also use the mean)
    if vle_correction == 'mean':
        corvle = mean(vlecnt)/float(npcu)
        corxe = mean(xecnt)/float(npcu)
        cortotal = mean(totalcnt)/float(npcu)
    
    # VLE correction factor
    pvle = 2*corvle*corxe*tau**2*(sin(pi*tau*f)/(pi*tau*f))**2
    
    # Dead time coefficients
    p1 = 2*(1-2*cortotal*td*(1-(td/float(2*tb))))
    p2 = 2*cortotal*td*((N-1)/float(N))*(td/float(tb))
    
    # Total correction factor
    pd = p1 - p2*cos((pi*f)/float(fnyq))

    return pd + pvle
