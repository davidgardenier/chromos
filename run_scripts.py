from scripts.get_event_mode import *
from scripts.create_filters import *
from scripts.extract_light_curves import *
from scripts.create_background import *
from scripts.rebin_background import *
from scripts.account_for_background import *
from scripts.cut_xray_flares import *
from scripts.create_power_spectra import *
from scripts.create_power_colours import *

object_name = 'aquila'

#determine_files(object_name, print_output=True)
#make_time(object_name, print_output=True)
#create_background(object_name, print_output=True)
#extract_light_curve(object_name, extrct_event_mode=True, extrct_background=True, print_output=True)
#rebin_background(print_output=True)
#account_for_background(print_output=True)
cut_xray_flares(print_output=True)
generate_power_spectra(print_output=True)
calculate_power_colours(print_output=True)
