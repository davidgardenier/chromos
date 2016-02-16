# Short function to simplify capturing output of executing subprocesses

def execute(command):
    from subprocess import Popen, PIPE, STDOUT
    
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=1)
    
    # Print output of program
    with p.stdout:
        for oline in iter(p.stdout.readline, b''):
            print oline,
        p.stdout.close()
        p.wait()
