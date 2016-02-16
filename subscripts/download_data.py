# Program to download data with just an obsid list and name of file. Basically
# an extended Python wrapper for Abbie's earlier bash script program, which has
# been adapted for better intregration with this program.
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def download():
    '''
    Python wrapper for an adapted bash script for downloading data. Requires an
    <obsid_list>.lst file to be present in the obsid_lists folder with the name
    of the selection (object name etc.)
    '''

    message = 'Downloading data'
    print message + '\n' + len(message)*'='

    import os
    import paths
    import logs
    import execute_shell_commands as shell

    # Check whether a file structure is in place for downloading the data, if
    # not then create the necessary file structure
    if not os.path.exists(paths.data):
        os.makedirs(paths.data)
        os.makedirs(paths.data_info)
        os.makedirs(paths.logs)

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    # Check whether obsid file exists
    if not os.path.exists(paths.obsid_list):
        print('No obsid list for %s in the obsids_list folder' %(paths.selection))
        return

    # Execute an adapted version of Abbie's code
    command = ['bash',
                paths.subscripts + 'download_data.sh',
                paths.obsid_list,
                paths.data,
                paths.data_info[:-1]]

    shell.execute(command)
