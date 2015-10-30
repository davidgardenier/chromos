from sys import stdout
from datetime import datetime

def update_progress(progress, t0, t):
    """
    https://stackoverflow.com/questions/3160699/python-progress-bar
    update_progress() : Displays or updates a console progress bar
    Accepts a float between 0 and 1. Any int will be converted to a float.
    A value under 0 represents a 'halt'.
    A value at 1 or bigger represents 100%
    """

    # Modify length to change the length of the progress bar
    length = 20
    status = ""

    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt \r\n"
    if progress >= 1 - 0.0001:
        progress = 1
        status = "Done \r\n"

    tdel = (t - t0).seconds/60.
    tleft = int(tdel/progress - tdel)
    block = int(round(length * progress))
    text = "\r    progress: [{0}] {1:.2f}% {2}".\
        format("#" * block + "-" * (length - block), progress * 100, tleft) + 'min ' + str(status)
    stdout.write(text)  # sys function
    stdout.flush()  # sys function
