from scripts.A_find_event_mode_files import *
from scripts.B_create_time_filters import *
from scripts.B_create_background import *
from scripts.C_extract_light_curves import *
from scripts.D_rebin_background import *
from scripts.E_account_for_background import *
from scripts.F_cut_xray_flares import *
from scripts.G_create_power_spectra import *
from scripts.H_create_power_colours import *
import os

PATH = '/scratch/david/master_project/data'
OBJECT_NAME = 'aquila'

os.chdir(PATH)

#determine_files(OBJECT_NAME, print_output=True)
#make_time(OBJECT_NAME, print_output=True)
#create_background(OBJECT_NAME, print_output=True)
#extract_light_curve(OBJECT_NAME, extract_event_mode=True, extract_background=True, print_output=True)
#rebin_background(print_output=True)
#account_for_background(print_output=True)
#cut_xray_flares(print_output=True)
#generate_power_spectra(print_output=True)
calculate_power_colours(print_output=True)
