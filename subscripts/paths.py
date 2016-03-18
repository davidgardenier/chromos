import os

selection = 'test_aquila'
subscripts = os.getcwd() + '/subscripts/'

data = '/scratch/david/master_project/test_aquila/'
data_info = data + 'info/'
database = data_info + 'database.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/scratch/david/master_project/obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'
