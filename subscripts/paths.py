import os

selection = 'xte_J1550m564'
subscripts = os.getcwd() + '/subscripts/'

data = '/scratch/david/master_project/xte_J1550m564/'
data_info = data + 'info/'
database = data_info + 'database_xte_J1550m564.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/scratch/david/master_project/obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'
