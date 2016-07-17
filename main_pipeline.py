# Master Project - Scripts for working with RXTE-data
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

from subscripts.download_data import *
from subscripts.locate_files import *
from subscripts.determine_info import *
from subscripts.spacecraft_filters import *
from subscripts.goodxenon_to_fits import *
from subscripts.pcu_filters import *
from subscripts.create_backgrounds import *
from subscripts.find_channels import *
from subscripts.extract_lc_and_sp import *
from subscripts.correct_for_background import *
from subscripts.find_xray_flares import *
from subscripts.create_power_spectra import *
from subscripts.create_power_colours import *
from subscripts.create_responses import *
from subscripts.calculate_hi import *

# Run the following first:
# --------------------------------------
# virtualenv venv --system-site-packages
# source venv/bin/activate
# setup_xray
# pip install --no-deps astropy==1.0.3
# --------------------------------------
# To quit the virtual enviroment, use:
# --------------------------------------
# deactivate
# --------------------------------------
# Do not deviate from this order in pipeline, as the subscripts all depend on
# each other to have run in a particular order.

# download()
# locate_files()
# determine_info()
# spacecraft_filters()
# goodxenon_to_fits()
# pcu_filters()
# create_backgrounds()
# find_channels()
# extract_lc_and_sp()
# correct_for_background()
# cut_xray_flares()
# create_power_spectra()
# create_power_colours()
# create_response()
calculate_hi()
