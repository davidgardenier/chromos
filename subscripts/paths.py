import os

selection = 'gx_339_d4'
subscripts = os.getcwd() + '/subscripts/'

data = '/scratch/david/master_project/gx_339_d4/'
data_info = data + 'info/'
database = data_info + 'database_gx_339_d4.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/scratch/david/master_project/obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'
