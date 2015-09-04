import os
from subprocess import Popen, PIPE, STDOUT

# -----------------------------------------------------------------------------
# ---------------------------- Create filter ----------------------------------
# -----------------------------------------------------------------------------

object_name = 'aquila'


def make_time(object_name, print_output=False):
    '''
    Function to run the maketime command on all filters. This allows a filter
    to be created, ensuring measurements don't contain any pointing errors, 
    occulations etc. This program creates a basic_<unitoftime>.gti file in the
    obsid directories.
    
    Arguments:
     - object_name: as it says
     - print_output: if True, will print the output of maketime function
    '''
    
    for folder in os.listdir('.'):
        if folder.startswith('P'):
            subfolder = os.path.join('./', folder)
            
            # Open obsid list  
            text = open(subfolder + '/' + object_name + '.obsid.list', 'r')
            
            # Find event mode files
            for line in text:
                if 'E_' in line:
                    os.chdir(subfolder + '/' + line.split('/')[0] + '/stdprod')
                    
                    # Find filter files
                    for f in os.listdir('.'):
                        if f.endswith('.xfl.gz'):
                            
                            # Avoid problems with running maketime by removing
                            # previous versions of basic.gti
                            try:
                                os.remove('./../basic_' + line.split('_')[2] + '.gti')
                            except OSError:
                                pass
                            
                            # Execute maketime
                            p = Popen(['maketime'], stdout=PIPE, stdin=PIPE,
                                      stderr=STDOUT, bufsize=1)
                            
                            if print_output is True:
                                print('---> Running maketime on ' + line.split('/')[0])
                                
                            # Give the required input
                            # -----------------------
                            # Name of FITS file
                            p.stdin.write('./' + f + ' \n')
                            # Name of output FITS file
                            p.stdin.write('./../basic_' + line.split('_')[2] + '.gti \n')
                            # Selection expression. Note I have omitted the num_pcu_on_eq_5!
                            p.stdin.write('elv.gt.10.and.offset.lt.0.02.and.num_pcu_on.gt.1.and.(time_since_saa.gt.30.or.time_since_saa.lt.0.0) \n')
                            # Flag yes, if HK format is compact
                            p.stdin.write('no \n')
                            # Column containing HK parameter times
                            p.stdin.write('TIME \n')


                            # Print output of program
                            if print_output is True:
                                with p.stdout:
                                    for line in iter(p.stdout.readline, b''):
                                        print line,
                                    p.stdout.close()
                                    p.wait()

                    os.chdir('./../../../')

    print '----------- \n Successfully created basic.gti files'


if __name__ == '__main__':
    make_time(object_name, print_output=False)
