#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 21:47:08 2021

@author:        Daniele Zannoni

Description:    apply humidity-isotope correction based on characterization
                runs for standards GLW, FINSE, BER. 
                Parameters:
                h2o         is the measured mixing ratio by the Picarro
                delta_raw   is the raw delta value measured by the Picarro
                isotope     can be '18' or '2' for d18O and dD, respectively
                ref_level   the raw isotope measurements will be corrected to 
                            this reference value
                correction  can be 'mean', 'function', 'GLW', 'FINSE', 'BER'.  
                            Each choise has its own fitting coeffiecents for the
                            correction curve
Notes:          
"""
def hum_corr_fun(h2o, delta_raw, isotope, ref_level, correction):
    from numpy import mean    
    if isotope == 18:
        offset = 0
        amplitude = 0
        exponent = 0
        # Chose fitting parameters --------------------------------------------
        if correction == 'mean':
            # mean parameters
            offset      =  0
            amplitude   =  [-0.29956791326329024, -1.4431892314634496]
            exponent    =  [0.19799994325897938, 0.09535956113906896]
            amplitude   = mean(amplitude)
            exponent    = mean(exponent)
        elif correction == 'function':  
            # function parameters
            offset      = 0
            amplitude   = 0.005*(delta_raw**2) + 0.1903*delta_raw + 0.0322
            exponent    = 0.0039*(delta_raw**2) + 0.1804*delta_raw + 1.5915
        elif correction == 'GLW':
            offset      =  5.658515995189071
            amplitude   =  -0.29956791326329024
            exponent    =  0.19799994325897938 
        elif correction == 'FINSE':
            offset      =  4.217725115130757
            amplitude   =  -1.4431892314634496
            exponent    =  0.09535956113906896 
        elif correction == 'BER':
            offset      =  4.217725115130757
            amplitude   =  -1.4431892314634496
            exponent    =  0.09535956113906896         
        # Apply function -----------------------------------------------------
        base        =  offset + amplitude * ref_level**exponent
        observed    = offset + amplitude * h2o**exponent
        return delta_raw - (observed - base)
    
    elif isotope == 2:
        offset = 0
        amplitude = 0
        exponent = 0
        # Chose fitting parameters --------------------------------------------
        if correction == 'mean':
            # mean parameters
            offset      =  0
            amplitude   =  [20042.963583308014, 19676.719362224634]
            exponent    =  [0.00011362319076875247, 0.000143895062984707]
            amplitude   = mean(amplitude)
            exponent    = mean(exponent)
        elif correction == 'function':  
            # function parameters
            offset      = 0
            amplitude   = 1.0718*(delta_raw**2) + 65.418*delta_raw + 18458
            exponent    = -0.00002*(delta_raw**2) - 0.0012*delta_raw + 0.0231
        elif correction == 'GLW':
            offset      =  -18.071154390404402
            amplitude   =  111100.39555439672
            exponent    =  -1.623384478608584
        elif correction == 'FINSE':
            offset      =  -20061.99424613493
            amplitude   =  20042.963583308014
            exponent    =  0.00011362319076875247
        elif correction == 'BER':
            offset      =  -19694.174170468268
            amplitude   =  19676.719362224634
            exponent    =  0.000143895062984707
        # Apply function -----------------------------------------------------
        base        =  offset + amplitude * ref_level**exponent
        observed    = offset + amplitude * h2o**exponent
        return delta_raw - (observed - base)
        
