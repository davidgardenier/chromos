def locate_files():
    '''
    Function to locate the zipped files across multiple data folders,
    circumventing the use of the xdf file browser. Information on files is then
    grouped per P<number> folder, so still needs to be split out afterwards.
    '''
    purpose = 'Locating data files'
    print len(purpose)*'=' + '\n' + purpose + '\n' + len(purpose)*'='

    import os
    import glob
    from subprocess import Popen, PIPE
    import paths
    import logs
    import execute_shell_commands as shell

    # Set log file
    filename = __file__.split('/')[-1].split('.')[0]
    logs.output(filename)

    os.chdir(paths.data)

    for e in glob.glob('./P*'):

        os.chdir(e)

        # The shell script needs an obsid file per folder
        obsids = [o.split('/')[-1] for o in glob.glob('./*-*-*-*')]
        with open('../obsids.list','w') as f:
            f.write('\n'.join(obsids))

        # Execute Phil's code to circumvent having to use xdf
        command = ['csh',
                    paths.subscripts + 'xtescan2',
                    '../obsids.list',
                    paths.selection]

        shell.execute(command)
        os.chdir(paths.data)
