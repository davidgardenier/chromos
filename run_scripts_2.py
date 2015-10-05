from subscripts.A_find_data_files import *
from subscripts.B_split_info_per_obsid import *
from subscripts.C_create_time_filters import *
from subscripts.C_create_background import *
from subscripts.C_goodxenon_to_fits import *

PATH = '/scratch/david/master_project/full_data'
OBJECT_NAME = 'aquila'
PRINT_OUTPUT = True
os.chdir(PATH)

#determine_files(OBJECT_NAME, print_output=PRINT_OUTPUT)
#split_files(OBJECT_NAME, print_output=PRINT_OUTPUT)
#create_time_filters(print_output=PRINT_OUTPUT)
create_background(print_output=PRINT_OUTPUT)
#xenon2fits(print_output=PRINT_OUTPUT)
