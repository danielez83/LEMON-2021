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
    from numpy import mean, exp
    if isotope == 18:
        offset = 0
        amplitude = 0
        exponent = 0
        # Chose fitting parameters --------------------------------------------
        if correction == 'mean':
            # mean parameters
            #offset      =  0
            #amplitude   =  [-0.29956791326329024, -1.4431892314634496]
            #exponent    =  [0.19799994325897938, 0.09535956113906896]
            # Parameters updated on 30.11.2021, run fit_humidity_resposne_d18O.py
            #offset      = [2.019471236336247, 3.6831025919760405, 0.5521030363683059]
            offset      = [2.019471236336247, 3.6831025919760405]
            #amplitude   = [-0.2995690340810427, -0.2995690340810427, -8.412971043088432e-08]
            amplitude   = [-0.2995690340810427, -0.2995690340810427]
            #exponent    = [0.19799967307975017, 0.09535932244861908, 1.5609181427821488]
            exponent    = [0.19799967307975017, 0.09535932244861908]
            offset      = mean(offset)
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
            #offset      =  0
            #amplitude   =  [20042.963583308014, 19676.719362224634]
            #exponent    =  [0.00011362319076875247, 0.000143895062984707]
            # Parameters updated on 30.11.2021, run fit_humidity_resposne_dD.py
            #offset      = [-0.635680041585749, -16629.747872948374, -16490.816678197258]
            offset      = [-16629.747872948374, -16490.816678197258]
            #amplitude   = [111144.42281681988, 16607.14033442959, 16463.28088216032]
            amplitude   = [16607.14033442959, 16463.28088216032]
            #exponent    = [-1.623438528449282, 0.00013710375689641975, 0.00017193692019899255]
            exponent    = [0.00013710375689641975, 0.00017193692019899255]
            offset      = mean(offset)
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
        

def hum_corr_fun_v2(h2o, delta_raw, isotope, ref_level, correction):
    from numpy import mean, exp
    from FARLAB_standards import standard
    if isotope == 18:
        offset = 0
        amplitude = 0
        b = 0
        # Chose fitting parameters --------------------------------------------
        if correction == 'mean': # Use only GLW and FINSE
            offset      = mean([-0.1504144982664188, -0.06227032189174321])
            amplitude   = mean([1.070301863755927, 1.0538273137810708])
            b           = mean([-0.00012824517621849688, -0.00014474400748255454])
        elif correction == 'GLW':
            offset      =  -0.1504144982664188
            amplitude   =  1.070301863755927
            b           =  -0.00012824517621849688 
        elif correction == 'FINSE':
            offset      =  -0.06227032189174321
            amplitude   =  1.0538273137810708
            b           =  -0.00014474400748255454 
        elif correction == 'BER':
            offset      =  -1063.700284143874
            amplitude   =  1064.3363757714112
            b           =  -2.3911906420482837e-08         
        # Apply function -----------------------------------------------------
        base        =  offset + amplitude * exp(b*ref_level)
        observed    = offset + amplitude * exp(b*h2o)
        return delta_raw - (observed - base)
        #correction_val = offset + amplitude * exp(b*h2o)
        #return delta_raw - correction_val
    
    elif isotope == 2:
        offset = 0
        amplitude = 0
        b = 0
        # Chose fitting parameters --------------------------------------------
        if correction == 'mean': # Use only GLW and FINSE, see Fitting_Params_dep_on_delta
            #offset      = mean([-0.3238486826299902, -0.03737740194196507])
            #amplitude   = mean([-8.136719793176624, -11.432037281562975])
            #b           = mean([-0.00021683177456712982, -0.00025837731781128495])
            #--- Estimate GLW correction
            offset              = 206.95644144911225
            amplitude           = -207.44118373656121
            b                   = 2.0622508335883677e-08
            GLW_corr_base       = offset + amplitude * exp(b*ref_level)
            GLW_corr_observed   = offset + amplitude * exp(b*h2o)
            #--- Estimate FIN correction
            offset              = -0.3238486826299902
            amplitude           = -8.136719793176624
            b                   = -0.00021683177456712982
            FIN_corr_base       = offset + amplitude * exp(b*ref_level)
            FIN_corr_observed   = offset + amplitude * exp(b*h2o)
            #--- Estimate relative weights based on raw dD measured
            dD_FIN      = standard('FINSE', 'dD')
            dD_GLW      = standard('GLW', 'dD')
            x           = (delta_raw - dD_FIN)/(dD_GLW - dD_FIN)
            base        = FIN_corr_base*(1-x) + GLW_corr_base*x
            observed    = FIN_corr_observed*(1-x) + GLW_corr_observed*x
            return delta_raw - (observed - base)
            
        elif correction == 'GLW':
            offset      =  206.95644144911225
            amplitude   =  -207.44118373656121
            b           =  2.0622508335883677e-08
            # Apply function -----------------------------------------------------
            base        =  offset + amplitude * exp(b*ref_level)
            observed    = offset + amplitude * exp(b*h2o)
            return delta_raw - (observed - base)
        elif correction == 'FINSE':
            offset      =  -0.3238486826299902
            amplitude   =  -8.136719793176624
            b           =   -0.00021683177456712982
            # Apply function -----------------------------------------------------
            base        =  offset + amplitude * exp(b*ref_level)
            observed    = offset + amplitude * exp(b*h2o)
            return delta_raw - (observed - base)
        elif correction == 'BER':
            offset      =  -0.03737740194196507
            b           =  -11.432037281562975
            exponent    =  -0.00025837731781128495
            # Apply function -----------------------------------------------------
            base        =  offset + amplitude * exp(b*ref_level)
            observed    = offset + amplitude * exp(b*h2o)
            return delta_raw - (observed - base)
        #return delta_raw - correction_val