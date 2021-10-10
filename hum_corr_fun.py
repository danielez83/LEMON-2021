#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 21:47:08 2021

@author: daniele
"""
def hum_corr_fun(h2o, delta_raw, isotope, ref_level, correction):
    from numpy import mean    
    if isotope == 18:
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
        
        # Apply function
        base        =  offset + amplitude * ref_level**exponent
        observed    = offset + amplitude * h2o**exponent
        return delta_raw - (observed - base)
    
    elif isotope == 2:
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
        # Apply function
        base        =  offset + amplitude * ref_level**exponent
        observed    = offset + amplitude * h2o**exponent
        return delta_raw - (observed - base)
        
