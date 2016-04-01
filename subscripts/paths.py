import os

selection = 'KS_1731m260'
subscripts = os.getcwd() + '/subscripts/'

data = '/scratch/david/master_project/KS_1731m260/'
data_info = data + 'info/'
database = data_info + 'database.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/scratch/david/master_project/obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'
