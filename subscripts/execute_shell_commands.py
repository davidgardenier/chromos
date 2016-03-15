# Short function to simplify capturing output of executing subprocesses
# Written by David Gardenier, davidgardenier@gmail.com, 2015-2016

def execute(command):
    import subprocess

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() != None:
            break
        if len(nextline) != 0:
            print nextline.strip()

    output = process.communicate()
    normal_output = output[0]
    error = output[1]
    exitCode = process.returncode

    if (exitCode == 0):
        return normal_output
    else:
        print 'ERROR:', ' '.join(command), error
