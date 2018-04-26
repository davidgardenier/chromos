# Program to download data with just an obsid list and name of file. Basically
# an extended Python wrapper for Abbie's earlier bash script program, which has
# been adapted for better intregration with this program.
# Written by David Gardenier, 2015-2016

def download():
    '''
    Python wrapper for an adapted bash script for downloading data. Requires an
    <obsid_list>.lst file to be present in the obsid_lists folder with the name
    of the selection (object name etc.)
    '''

    purpose = 'Downloading data'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import paths
    import logs
    import execute_shell_commands as shell

    # Check whether a file structure is in place for downloading the data, if
    # not then create the necessary file structure
    folders = [paths.data, paths.data_info, paths.logs]
    for f in folders:
        if not os.path.exists(f):
            os.makedirs(f)

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    # Check whether obsid file exists
    if not os.path.exists(paths.obsid_list):
        print('No obsid list for %s in obsids_list folder' %(paths.selection))
        return

    # Execute an adapted version of Abbie's code
    command = ['bash',
                paths.subscripts + 'download_data.sh',
                paths.obsid_list,
                paths.data,
                paths.data_info[:-1]]

    shell.execute(command)

    logs.stop_logging()
