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
    pc_1_error = []
    pc_2 = []
    pc_2_error = []
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
        power_spectrum_squared = inverted_data[4]
        number_of_segments = inverted_data[5][0]
        
        variances = []
        variance_errors = []
        index_frequency_bands = []

        # Convert frequency bands to index values from in the frequency list
        for fb in frequency_bands:
            index = min(range(len(frequency)), key=lambda i: abs(frequency[i]-fb))
            index_frequency_bands.append([index])

        # Group indexes into sets of style [low, high)
        for i, e in enumerate(index_frequency_bands[:-1]):
            e.append(index_frequency_bands[i+1][0]-1)

        del index_frequency_bands[-1]

        # Integrate the power spectra within the frequency bands
        bin_width = frequency[1]-frequency[0]

        for e in index_frequency_bands:
            variance = bin_width*sum(power_spectrum[e[0]:e[1]])
            variances.append(variance)

            # Calculate errors on the variance (see appendix Heil, Vaughan & Uttley 2012)
            # M refers to the number of segments
            one_over_sqrt_M = 1/float(np.sqrt(number_of_segments))
            prop_std = sum(power_spectrum_squared[e[0]:e[1]])
            variance_error = bin_width*one_over_sqrt_M*np.sqrt(prop_std)
            variance_errors.append(variance_error)
            
        pc1 = variances[2]/float(variances[0])
        pc2 = variances[1]/float(variances[3])
        
        pc1_error = np.sqrt((variance_errors[2]**2/float(variances[2]) + variance_errors[0]**2/float(variances[0]))*pc1)
        pc2_error = np.sqrt((variance_errors[1]**2/float(variances[1]) + variance_errors[3]**2/float(variances[3]))*pc2)

        pc_1.append(pc1)
        pc_2.append(pc2)
        
        pc_1_error.append(pc1_error)
        pc_2_error.append(pc2_error)

    # Sort the power colours
    srt_list = []
    for i in range(len(pc_1)):
        srt_list.append((pc_1[i], pc_2[i], pc_1_error[i], pc_2_error[i], paths[i].split('/')[2]))

    sorted_list = sorted(srt_list, key=lambda obsid: obsid[4])
    pc1, pc2, pc1_error, pc2_error, obsid = zip(*sorted_list)

    for i in range(len(paths)):
        print(pc1[i], pc2[i], pc1_error[i], pc2_error[i])
        plt.errorbar(pc1[i], pc2[i], xerr=pc1_error[i], yerr=pc2_error[i], ls='none', marker='x', c=next(color), label=obsid[i])

    plt.xscale('log')
    plt.yscale('log')
    plt.xlim([0.001, 1000])
    plt.ylim([0.001, 1000])
    plt.legend()
    plt.show()#('./pwr_colours.png')

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
