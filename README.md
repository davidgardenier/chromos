Scripts to automate the extraction of light curves from RXTE data, create power
spectra and subsequently plot power colour colour diagrams for Aquila X-1

---------------

File structure of scripts is on basis of execution order, and built in modular
style. It is safe to run subscripts with larger letters (say J) without 
changing the output of lower letters (say B). The same goes for files with the 
same letter (C and C).

Essential to the data extraction is the dictionary with paths to different 
files. This is updated as subscripts are executed, and allows subscripts to be
run multiple times without causing errors. Ideally this should be transformed 
to a class, with functions returning the paths.

File structure:
```
A                find_all_data
                       |
B                 split_files -----------
                 /   | | |  |            \
C create_time_filter | | | gx_to_fits    cut_pcu_change
      |          |   / | \  |             |
D     |    create_bkg_ |  find_channels   |
      \          \     |    /             /
E      -----------extract_lc--------------
                       |
F               rebin_background--------
                       |               |
G            account_for_background    |
                       |               |
H               cut_xray_flares---------
                       |
I             create_power_spectrum
                       |
J             create_power_colours
'''
---------------

Author: David Gardenier

Project: Master Project @ Anton Pannekoek Institute for Astronomy

Date: July 2015 - July 2016
