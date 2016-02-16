import os

selection = 'test'
subscripts = os.getcwd() + '/subscripts/'

root = '/scratch/david/master_project/'

data = root + selection + '/'
data_info = data + 'info/'

logs = data_info + 'logs/'
terminal_output = True

obsid_lists = root + 'obsid_lists/'
obsid_list = obsid_lists + selection + '.lst'


