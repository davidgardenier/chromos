
obj = [ '4U_0614p09',
        '4U_1636_m53',
        '4U_1702m43',
        '4u_1705_m44',
        '4U_1728_34',
        'aquila_X1',
        'cir_x1',
        'cyg_x2',
        'EXO_0748_676',
        'gx_17p2',
        'gx_340p0',
        'gx_349p2',
        'gx_5m1',
        'HJ1900d1_2455',
        'IGR_J00291p5934',
        'IGR_J17480m2446',
        'IGR_J17498m2921',
        'KS_1731m260',
        'xte_J1808_369',
        'S_J1756d9m2508',
        'sco_x1',
        'sgr_x1',
        'sgr_x2',
        'v4634_sgr',
        'XB_1254_m690',
        'xte_J0929m314',
        'J1701_462',
        'xte_J1751m305',
        'xte_J1807m294',
        'xte_J1814m338',
        'gx_339_d4',
        'H1743m322',
        'xte_J1550m564']

for o in obj:
    data = '/scratch/david/master_project/' + o + '/'
    database = '/scratch/david/master_project/'+o+'/info/database_'+o+'.csv'
    
    filein = database
    fileout = database

    f = open(filein,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace("gx2_2s.ps","gx_2s.ps")

    f = open(fileout,'w')
    f.write(newdata)
    f.close()
