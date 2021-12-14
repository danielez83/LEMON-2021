#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 10:26:03 2021

Call this script if you want to calibrate Picarro data

@author: daniele
"""
#%% 
def calibrate_picarro_data(df_Picarro_raw, Calibration_param_filename, calibrate_isotopes, calibrate_humidity, ref_val_humidity):
    # IMPORTS ----------------------------------------------------------------
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import datetime
    from hum_corr_fun import hum_corr_fun

    # Calibrate Picarro data -------------------------------------------------
    #ref_val_humidity = 17000 # ppm
    calibration_paramters = pd.read_pickle(Calibration_param_filename)
    DOI = df_Picarro_raw.index[1000].day
    tot = calibration_paramters.index.day == DOI
    IOI = np.where(tot==True)
    IOI = IOI[0][0]
    
    df_Picarro_data_calibrated = df_Picarro_raw.copy()
    # Humidity-isotope correction
    df_Picarro_data_calibrated['d18O'] = hum_corr_fun(df_Picarro_raw['H2O'], 
                                                   df_Picarro_raw['d18O'], 
                                                   18, ref_val_humidity, 'mean')
    df_Picarro_data_calibrated['dD'] = hum_corr_fun(df_Picarro_raw['H2O'], 
                                                   df_Picarro_raw['dD'], 
                                                   2, ref_val_humidity, 'mean')
    # Isotope calibration
    if calibrate_isotopes == 'yes':
        df_Picarro_data_calibrated['d18O'] = df_Picarro_data_calibrated['d18O']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
        df_Picarro_data_calibrated['dD'] = df_Picarro_data_calibrated['dD']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]
    else:
        df_Picarro_data_calibrated['d18O'] = df_Picarro_subset['d18O']
        df_Picarro_data_calibrated['dD'] = df_Picarro_subset['dD']
    
    # Humidity calibration, using OPTISONDE relationship
    if calibrate_humidity == 'yes':
        df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']*0.957 - 6.431
    else:
        df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']
        
    return df_Picarro_data_calibrated
        
    
    return df_Picarro_data_calibrated
