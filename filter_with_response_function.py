#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 10:56:26 2022


Filter time series using impulse response function

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import pickle

from scipy import signal
from scipy.fft import rfft, rfftfreq, irfft, fft, fftfreq, ifft


#%% Load data
# Import Picarro data
with open('picarro_data_20210918_1200_1500.pkl', 'rb') as f:
    Picarro_data = pickle.load(f)
y1 = Picarro_data['d18O'].to_numpy()
y2 = Picarro_data['dD'].to_numpy()
t = Picarro_data.index.to_numpy()
# Drop some obs
y1 = y1[160000:200050]
y2 = y2[160000:200050]
t = t[160000:200050]

# Import Response function
with open('response_functions_15032022.pkl', 'rb') as f:
          P_H2O_reponse, P_d18O_reponse, P_dD_reponse,f_H2O, f_d18O, f_dD, fs_H2O, fs_d18O, fs_dD = pickle.load(f)

del f


#%% y1, d18O
#P_OI = P_H2O_reponse
#f_OI = f_H2O
#var = 'H2O'
P_OI = P_d18O_reponse
f_OI = f_d18O
var = 'd18O'

yf = np.fft.rfft(np.gradient(y1))
fs  = np.timedelta64(1, 's')/np.mean(np.diff(t))
xf = np.fft.rfftfreq(len(y2), 1 / fs)
y_dummy = np.cumsum(np.fft.irfft(yf))
offset = y_dummy - y1
yh = np.interp(xf, f_OI, P_OI, left=1+0*1j, right = 0*1j)          
# Apply transfer function to filter segment
y_product   = yf*yh
# Compute iFFT of the segment
y_ifft      = np.fft.irfft(y_product)
# Integrate
y_filtered  = np.cumsum(y_ifft) - offset
 
# Apply lowpass filter to filtered timeseries
order = 1
f_cut_lowpass = .1
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs) # Build butterworth filter
y_filtered = signal.filtfilt(b, a, y_filtered) # Appy filter to the time 

#%% Add delay
delay_H2O = -13.75
delay_d18O = -15.36
delay_dD = -15.60
#
timebase = np.mean(np.diff(t))
t_unit = 1e-9*timebase.astype(int)
if var == 'H2O':
    delay = round(delay_H2O/t_unit)
elif var == 'd18O':
    delay = round(delay_d18O/t_unit)
elif var == 'dD':
    delay = round(delay_dD/t_unit)

y1_filtered = np.roll(y_filtered, delay)

#%% y1, dD
#P_OI = P_H2O_reponse
#f_OI = f_H2O
#var = 'H2O'
P_OI = P_dD_reponse
f_OI = f_dD
var = 'dD'

yf = np.fft.rfft(np.gradient(y2))
fs  = np.timedelta64(1, 's')/np.mean(np.diff(t))
xf = np.fft.rfftfreq(len(y2), 1 / fs)
y_dummy = np.cumsum(np.fft.irfft(yf))
offset = y_dummy - y2
yh = np.interp(xf, f_OI, P_OI, left=1+0*1j, right = 0*1j)          
# Apply transfer function to filter segment
y_product   = yf*yh
# Compute iFFT of the segment
y_ifft      = np.fft.irfft(y_product)
# Integrate
y_filtered  = np.cumsum(y_ifft) - offset
 
# Apply lowpass filter to filtered timeseries
order = 1
f_cut_lowpass = .1
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs) # Build butterworth filter
y_filtered = signal.filtfilt(b, a, y_filtered) # Appy filter to the time 

#%% Add delay
delay_H2O = -13.75
delay_d18O = -15.36
delay_dD = -15.60
#
timebase = np.mean(np.diff(t))
t_unit = 1e-9*timebase.astype(int)
if var == 'H2O':
    delay = round(delay_H2O/t_unit)
elif var == 'd18O':
    delay = round(delay_d18O/t_unit)
elif var == 'dD':
    delay = round(delay_dD/t_unit)

y2_filtered = np.roll(y_filtered, delay)

#%%
fig, ax = plt.subplots(nrows=3, dpi=150)
ax[0].plot(t,y1)
ax[0].plot(t,y1_filtered)
ax[1].plot(t,y2)
ax[1].plot(t,y2_filtered)
ax[2].plot(t,y2 - 8*y1)
ax[2].plot(t,y2_filtered - 8*y1_filtered)

#ax.set_xlim([15000, 20000])
#ax[0].plot(np.angle(yf))
#ax[1].plot(np.angle(y_seg_product))