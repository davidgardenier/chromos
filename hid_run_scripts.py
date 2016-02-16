#!/usr/bin/env python

'''
Scripts to run data through pipeline to calculate hardness intensity values.
'''

import os
from pc_ss.A_find_data_files import *
from hid_ss.B_split_over_files import *
from hid_ss.C_create_time_filters import *
from pc_ss.D_cut_pcu_change import *
from hid_ss.D_create_background import *
from pc_ss.D_find_channels import *
from hid_ss.E_extract_light_curves import *
from hid_ss.F_create_response import *
from hid_ss.G_calculate_hid import *
from hid_ss.H_plot_hid import *
from pc_ss.print_dictionary import *

OBJECT_NAME = 'J1701_462'
DATA = '/scratch/david/master_project/' + OBJECT_NAME
SCRIPTS = os.getcwd() + '/hid_ss/'
VERBOSE = True

os.chdir(DATA)

if __name__ == '__main__':
    #find_data(OBJECT_NAME, verbose=VERBOSE)
    #split_files(OBJECT_NAME, verbose=VERBOSE)
    #create_time_filters(verbose=VERBOSE)
    #cut_pcu_change(verbose=VERBOSE)
    #create_background(verbose=VERBOSE)
    #find_channels(verbose=VERBOSE)
    #extract_light_curves(verbose=VERBOSE)
    #create_response(verbose=VERBOSE)
    #create_hid(DATA, SCRIPTS, verbose=VERBOSE)
    #plot_hid(verbose=VERBOSE)
    print_dictionary()
