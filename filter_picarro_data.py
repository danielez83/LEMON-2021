#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 16:45:52 2022
Functions to filter data from the lemon ground validation campaign.

To run the filter, the impulse response is needed, run plot_picarro_timings_playing.py
now the response function is stored into 

response_functions_15032022.pkl
[P_H2O_reponse, P_d18O_reponse, P_dD_reponse,f_H2O, f_d18O, f_dD, fs_H2O, fs_d18O, fs_dD]

@author: daniele
"""

def filter_picarro_data(raw_data_in, time_in, variable):
    import pandas as pd
    import numpy as np
    import datetime
    import pickle

    from scipy import signal
    from scipy.fft import rfft, rfftfreq, irfft
    
    # Delay configuration
    delay_H2O = -13.75 # s
    delay_d18O = -15.36 # s
    delay_dD = -15.60 # s
    
    # BW filter configuration
    order = 1
    f_cut_lowpass = .1 # Hz
    
    # Import Response function
    with open('response_functions_15032022.pkl', 'rb') as f:
              P_H2O_reponse, P_d18O_reponse, P_dD_reponse,f_H2O, f_d18O, f_dD, fs_H2O, fs_d18O, fs_dD = pickle.load(f)
    
    del f
    
    # Prepare variables
    timebase = np.mean(np.diff(time_in))
    t_unit = 1e-9*timebase.astype(int)
    if variable == 'H2O':
        delay = round(delay_H2O/t_unit)
        P_OI = P_H2O_reponse
        f_OI = f_H2O
    elif variable == 'd18O':
        delay = round(delay_d18O/t_unit)
        P_OI = P_d18O_reponse
        f_OI = f_d18O
    elif variable == 'dD':
        delay = round(delay_dD/t_unit)
        P_OI = P_dD_reponse
        f_OI = f_dD

    # interpolate nans 
    raw_data_in.interpolate(inplace = True) # Required because FaVaCal returns NaNs
    # Convert to numpy arrays
    y = raw_data_in.to_numpy()
    t = time_in.to_numpy()

    
    # Delay data
    y = np.roll(y, delay)
      
    # Compute FFT of first derivative of the raw signal
    yf = np.fft.rfft(np.gradient(y))
    # Determine sampling frequency
    fs  = np.timedelta64(1, 's')/np.mean(np.diff(t))
    # Calculate vector of frequencies for fft
    xf = np.fft.rfftfreq(len(y), 1 / fs)
    # Calculate a dummy fft for offset
    y_dummy = np.nancumsum(np.fft.irfft(yf))
    offset = y_dummy - y
    # Interpolate impulse response function
    yh = np.interp(xf, f_OI, P_OI, left=1+0*1j, right = 0*1j)          
    # Convolve raw signal with transfer function
    y_product   = yf*yh
    # Compute iFFT of the filtered signal
    y_ifft      = np.fft.irfft(y_product)
    # Integrate filtered signal and remove offset (dc gain)
    y_filtered  = np.cumsum(y_ifft) - offset
     
    # Apply lowpass filter to filtered timeseries
    b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs) # Build butterworth filter
    y_filtered = signal.filtfilt(b, a, y_filtered) # Appy filter to the time series   
    return y_filtered

def delay_picarro_data(raw_data_in, time_in, variable):
    import pandas as pd
    import numpy as np
    import datetime

    # Delay configuration
    delay_H2O = -13.75 # s
    delay_d18O = -15.36 # s
    delay_dD = -15.60 # s
    
    y = raw_data_in.to_numpy()
    #t = time_in.to_numpy()
    
    # Prepare variables
    timebase = np.mean(np.diff(time_in))
    t_unit = 1e-9*timebase.astype(int)
    if variable == 'H2O':
        delay = round(delay_H2O/t_unit)
    elif variable == 'd18O':
        delay = round(delay_d18O/t_unit)
    elif variable == 'dD':
        delay = round(delay_dD/t_unit)
        
    y = np.roll(y, delay)
    return y
    