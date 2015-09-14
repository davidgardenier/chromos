import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate

# -----------------------------------------------------------------------------
# ---------------------- Calculate power colours ------------------------------
# -----------------------------------------------------------------------------

def find_power_spectra():
    '''
    Function to obtain a list with paths to all power spectra within obsid
    folders
    
    Output:
     - list with paths to all power spectra
    '''
    
    power_spectra = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.startswith('power') and f.endswith('s.dat'):
                power_spectra.append(os.path.join(root, f))

    return power_spectra
    

def calculate_power_colours(print_output=False):
    '''
    Function to calculate power colours for each power spectrum
    '''
    # Define the frequency bands in Hz
    frequency_bands = [0.0039,0.031,0.25,2.0,16.0]
        
    pc_1 = []
    pc_2 = []
    
    # Determine whether the power spectra are located
    paths = find_power_spectra()
    
    # Define colour for plotting
    color=iter(plt.cm.rainbow(np.linspace(0,1,len(paths))))
    
    # For each power spectrum
    for path in paths:
    
        # Import data
        all_data = np.loadtxt(path,dtype=float)
        inverted_data = np.transpose(all_data)
        
        # Give the columns their names
        power_spectrum = inverted_data[0]
        power_spectrum_error = inverted_data[1]
        frequency = inverted_data[2]
        frequency_error = inverted_data[3]
        
        index_frequency_bands = []
        
        # Convert frequency bands to index values from in the frequency list
        for fb in frequency_bands:
            index = min(range(len(frequency)), key=lambda i: abs(frequency[i]-fb))
            index_frequency_bands.append(index)
        
        variances = []
        
        # Integrate the power spectra within the frequency bands
        for i, e in enumerate(index_frequency_bands[:-1]):
            variance = integrate.simps(power_spectrum[e:index_frequency_bands[i+1]])
            variances.append(variance)
        
        pc1 = variances[1]/variances[0]
        pc2 = variances[2]/variances[3]
        
        pc_1.append(pc1)
        pc_2.append(pc2)
                
    # Sort the power colours
    srt_list = []
    for i in range(len(pc_1)):
        srt_list.append((pc_1[i], pc_2[i], paths[i].split('/')[2]))
    
    sorted_list = sorted(srt_list, key=lambda obsid: obsid[2]) 
    pc1, pc2, obsid = zip(*sorted_list)
    
    for i in range(len(paths)):
        plt.loglog(pc1[i], pc2[i], 'o', c=next(color), label=obsid[i])
    
    plt.xlim([0.03, 101])
    plt.ylim([0.03, 101])
    plt.legend()
    plt.show()
    
    # Write power colours to file
    f = open('./pwr_colours.dat', 'w')

    # For each value in a power spectrum
    for i, value in enumerate(pc1):
        # power_spectra value, error, frequency, freq_error
        line = (repr(pc1[i]) + ' ' + 
                repr(pc2[i]) + ' ' + 
                obsid[i] + '\n')
        
        f.write(line)
        
    f.close()

if __name__ == '__main__':
    calculate_power_colours(print_output=True)
