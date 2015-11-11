from subscripts.A_find_data_files import *
from subscripts.B_split_info_per_obsid import *
from subscripts.C_create_time_filters import *
from subscripts.C_goodxenon_to_fits import *
from subscripts.C_cut_pcu_change import *
from subscripts.D_create_background import *
from subscripts.D_find_channels import *
from subscripts.E_extract_light_curves import *
from subscripts.FG_rebin_background import *
from subscripts.H_cut_xray_flares import *
from subscripts.I_create_power_spectra import *
from subscripts.J_create_power_colours import *
from subscripts.print_dictionary import *

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True

os.chdir(PATH)

#determine_files(OBJECT_NAME, print_output=PRINT_OUTPUT)
## Note running split_files will reset the dictionary with information
#split_files(OBJECT_NAME, print_output=PRINT_OUTPUT)
#create_time_filters(print_output=PRINT_OUTPUT)
#xenon2fits(print_output=PRINT_OUTPUT)
#cut_pcu_change(print_output=PRINT_OUTPUT)
#create_background(print_output=PRINT_OUTPUT)
#find_channels(print_output=PRINT_OUTPUT)
#extract_light_curves(print_output=PRINT_OUTPUT)
#rebin_background(print_output=PRINT_OUTPUT)
#cut_xray_flares(print_output=PRINT_OUTPUT)
#create_power_spectra(print_output=PRINT_OUTPUT)
create_power_colours(print_output=PRINT_OUTPUT)
# ---------------------------------------------
print_dictionary()
