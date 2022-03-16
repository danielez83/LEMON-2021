#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 21:30:51 2022

@author: daniele
"""

def filter_picarro_data(raw_data_in, variable):
    import numpy as np
    from scipy import signal
    from scipy.special import erfc
    
    # Set win lenght
    win_length = 200
    
    # Build impulse function
    EMG_ = lambda x, mu, tau, sigma, h : (h*sigma/tau)*np.sqrt(np.pi/2)*np.exp((0.5 * np.power((sigma/tau), 2) - (x - mu)/tau))*erfc((1/np.sqrt(2))*(sigma/tau - (x - mu)/sigma))
    # Build dummy x
    x = np.linspace(1,win_length, win_length)
    
    # Build window, see plot_picarro_timings.py
    if variable == 'H2O':
        win = EMG_(x,
                  win_length/2-3, # mu
                  12.287346839653226, # tau
                  3.020655564273876, # sigma
                  0.1256536034352582) # h
    elif variable == 'd18O':
        win = EMG_(x,
                  win_length/2-4, # mu
                  14.064032260447744, # tau
                  4.063406740644367, # sigma
                  0.09171335392583457) # h
    elif variable == 'dD':
        win = EMG_(x,
                  win_length/2-5, # mu
                  18.46400472143487, # tau
                  3.9318095547128897, # sigma
                  0.09445648265929235) # h
    
    # Convovlve impulse response with timeseries
    y = signal.convolve(raw_data_in, win, mode='same')/sum(win)
    return y

def filter_picarro_data_BW(original_time_in, raw_data_in, variable):
    import numpy as np
    from scipy import signal
    import pandas as pd
    import datetime
    # Determine sampling frequency
    timebase = np.mean(np.diff(original_time_in))
    t_unit = 1e-9*timebase.astype(int)
    fs = 1/t_unit
    # Set correct time constant 
    if variable == 'H2O':
        tau = 5.19
    elif variable == 'd18O':
        tau = 5.75
    elif variable == 'dD':
        tau = 6.72
    Omega_c =  1/(2*np.pi*(tau/fs))
    # Filter order
    n = 1
    b, a = signal.butter(n, Omega_c, 'low')
    y = signal.filtfilt(b,a, raw_data_in)
    return y
    

def delay_picarro_data(original_time_in, original_data_in, variable):
    import numpy as np
    import pandas as pd
    import datetime
    delay_H2O = -13.75
    delay_d18O = -15.36
    delay_dD = -15.60
    #
    timebase = np.mean(np.diff(original_time_in))
    t_unit = 1e-9*timebase.astype(int)
    if variable == 'H2O':
        delay = round(delay_H2O/t_unit)
    elif variable == 'd18O':
        delay = round(delay_d18O/t_unit)
    elif variable == 'dD':
        delay = round(delay_dD/t_unit)
    
    y = np.roll(original_data_in, delay)
    return y
            