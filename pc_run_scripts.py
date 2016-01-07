from pc_ss.A_find_data_files import *
from pc_ss.B_split_info_per_obsid import *
from pc_ss.C_create_time_filters import *
from pc_ss.C_goodxenon_to_fits import *
from pc_ss.D_cut_pcu_change import *
from pc_ss.D_create_background import *
from pc_ss.D_find_channels import *
from pc_ss.E_extract_light_curves import *
from pc_ss.FG_rebin_background import *
from pc_ss.H_cut_xray_flares import *
from pc_ss.I_create_power_spectra import *
from pc_ss.J_create_power_colours import *
from pc_ss.print_dictionary import *

PATH = '/scratch/david/master_project/garching/'
OBJECT_NAME = 'various'
VERBOSE = True

os.chdir(PATH)

#find_data(OBJECT_NAME, verbose=VERBOSE)
# Note running split_files will reset the dictionary with information
# split_files(OBJECT_NAME, verbose=VERBOSE)
# create_time_filters(verbose=VERBOSE)
# xenon2fits(print_output=VERBOSE)
# cut_pcu_change(verbose=VERBOSE)
# create_background(print_output=VERBOSE)
# find_channels(verbose=VERBOSE)
# extract_light_curves(verbose=VERBOSE)
# rebin_background(print_output=VERBOSE)
# cut_xray_flares(print_output=VERBOSE)
# create_power_spectra(print_output=VERBOSE)
#create_power_colours(print_output=VERBOSE)
# ---------------------------------------------
print_dictionary()
