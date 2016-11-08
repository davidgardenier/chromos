import os

selection = '4U_0614p09'
subscripts = os.getcwd() + '/subscripts/'

data = '/scratch/david/master_project/4U_0614p09/'
data_info = data + 'info/'
database = data_info + 'database_4U_0614p09.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/scratch/david/master_project/obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'
