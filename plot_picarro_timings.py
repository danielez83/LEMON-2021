#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 10:11:14 2022

@author: daniele
"""
#%% Imports

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import control

import pickle

from scipy import signal
from scipy.fft import rfft, rfftfreq, irfft, fft, fftfreq, ifft
from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.special import erfc

from filter_picarro_data import delay_picarro_data


#%% Configuration
filename_step_data              = '../Excel/step_change_tests.csv'
filename_step_timings           = '../Excel/step_change_timings.csv'

filename_response_function      = 'response_functions_15032022_test.pkl'

# Colors
color_H2O   = 'k'
color_d18O  = 'r'
color_dD    = 'b'
color_dx    = [0.5, 0.5, 0.5] # Grey


#%% Load data into pandas dataframes
df_step_changes = pd.read_csv(filename_step_data, sep=',')
df_timings      = pd.read_csv(filename_step_timings, sep = ',')

#%% Calculate mean step changes for isotopes
mean_time_base_iso  = np.mean([df_step_changes['2.1_time'], 
                               df_step_changes['3.1_time'],
                               df_step_changes['7.1_time']], axis = 0)
mean_d18O           = np.mean([df_step_changes['2.1_d18O'], 
                               df_step_changes['3.1_d18O'],
                               df_step_changes['7.1_d18O']], axis = 0)
mean_dD             = np.mean([df_step_changes['2.1_dD'], 
                               df_step_changes['3.1_dD'],
                               df_step_changes['7.1_dD']], axis = 0)

#%% Calculate mean step changes for H2O
mean_time_base_H2O  = np.mean([df_step_changes['4.6_time'], 
                               df_step_changes['7.2_time']], axis = 0)
mean_H2O            = np.mean([df_step_changes['4.6_H2O'], 
                               df_step_changes['7.2_H2O']], axis = 0)
# Adjust H2O offset
mean_H2O = mean_H2O - np.min(mean_H2O)

#%% Select fastest and slowest step change for isotopes
fast_iso = df_step_changes[['2.1_time', '2.1_d18O', '2.1_dD']]
slow_iso = df_step_changes[['7.1_time', '7.1_d18O', '7.1_dD']]

#%% Calculate mean timings
d18O_delay  = [df_timings['d18O_delay'].mean(), df_timings['d18O_delay'].std()]
d18O_tau    = [df_timings['d18O_tau'].mean(), df_timings['d18O_tau'].std()]
dD_delay    = [df_timings['dD_delay'].mean(), df_timings['dD_delay'].std()]
dD_tau      = [df_timings['dD_tau'].mean(), df_timings['dD_tau'].std()]
H2O_delay   = [df_timings['H2O_delay'].mean(), (df_timings['H2O_delay'].max() - df_timings['H2O_delay'].min())]
H2O_tau     =[df_timings['H2O_tau'].mean(), (df_timings['H2O_tau'].max() - df_timings['H2O_tau'].min())]


#%% Plot Step change
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)

ax.plot(mean_time_base_H2O, mean_H2O, color = color_H2O, linewidth = 1.5, label = 'H$_2$O')
ax.fill_between(mean_time_base_H2O, 
                df_step_changes['7.2_H2O'] - np.min(df_step_changes['7.2_H2O']), 
                df_step_changes['4.6_H2O'] - np.min(df_step_changes['4.6_H2O']), color = color_H2O, alpha = 0.4)

ax.plot(mean_time_base_iso, mean_d18O, color = color_d18O, linewidth = 1.5, label = '$\delta^{18}$O')
ax.fill_between(mean_time_base_iso,
                slow_iso['7.1_d18O'], fast_iso['2.1_d18O'], color = color_d18O, alpha = 0.4)

ax.plot(mean_time_base_iso, mean_dD, color = color_dD, linewidth = 1.5, label = '$\delta$D')
ax.fill_between(mean_time_base_iso,
                slow_iso['7.1_dD'], fast_iso['2.1_dD'], color = color_dD, alpha = 0.4)

ax.grid()
ax.set_xlabel('Time (s)', size = 24)
ax.set_xlim([0, 80])
ax.set_ylabel('Signal (AU)', size = 24)
ax.tick_params(axis='both', which='major', labelsize=18)
#ax.tick_params(axis='both', which='minor', labelsize=8)

ax.plot([0, 100], [0.63, 0.63], linestyle = '--', color = 'k')
ax.text(5, 0.65, '$\\tau_{63}$', size = 24)

ax.legend(fontsize = 18)

#%% Print timings on screen
print('Delay ------------------------------')
print('H2O  : %.2f ± %.2f seconds' % (H2O_delay[0], H2O_delay[1]))
print('d18O : %.2f ± %.2f seconds' % (d18O_delay[0], d18O_delay[1]))
print('dD   : %.2f ± %.2f seconds' % (dD_delay[0], dD_delay[1]))
print('tau (63.2 %%) ----------------------')
print('H2O  : %.2f ± %.2f seconds' % (H2O_tau[0], H2O_tau[1]))
print('d18O : %.2f ± %.2f seconds' % (d18O_tau[0], d18O_tau[1]))
print('dD   : %.2f ± %.2f seconds' % (dD_tau[0], dD_tau[1]))
print('Response time (99.3%%) ------------')
print('H2O  : %.2f seconds' % (5*H2O_tau[0]))
print('d18O : %.2f seconds' % (5*d18O_tau[0]))
print('dD   : %.2f seconds' % (5*dD_tau[0]))

#%% Caclulate and fit impulse response
# https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/full/10.1002/cem.1343
# Reconstruction of chromatographic peaks using the exponentially modified Gaussian function
# Eq. 6
# See wikipedia alternative forms
# https://en.wikipedia.org/wiki/Exponentially_modified_Gaussian_distribution#cite_note-Kalambet2011-2
impulse_H2O     = np.gradient(mean_H2O)
impulse_d18O    = np.gradient(mean_d18O)
impulse_dD      = np.gradient(mean_dD)

def EMG(x, mu, tau, sigma, h):
    # x is the time
    # mu is the position of unmodified Gaussian, 
    # tau is the relaxation time parameter of exponent used to modify Gaussian
    # sigma is the Gaussian sigma, 
    # h is the Gaussian height, 
    y =  (h*sigma/tau)*np.sqrt(np.pi/2)*np.exp((0.5 * np.power((sigma/tau), 2) - (x - mu)/tau))*erfc((1/np.sqrt(2))*(sigma/tau - (x - mu)/sigma))
    return y

def gaussian(x, mu, sigma):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sigma, 2.)))

# Fit H2O
parameters, covariance = curve_fit(EMG, mean_time_base_H2O, impulse_H2O, [30, 1, 1, 1])
impulse_H2O_fitted = EMG(mean_time_base_H2O,
                         parameters[0], # mu
                         parameters[1], # tau
                         parameters[2], # sigma
                         parameters[3]) # h
# Calculate residuals
residuals_H2O_fitted = impulse_H2O - impulse_H2O_fitted
impulse_H2O_gaussian = gaussian(mean_time_base_H2O, 
                                mean_time_base_H2O[impulse_H2O_fitted == max(impulse_H2O_fitted)][0], # peak
                                parameters[2])*parameters[3] # scale
# Print outbest-fit values
print('H2O EMG best fit ------------------------------')
print('mu = %.2f s' % parameters[0])
print('tau = %.2f' % parameters[1])
print('sigma = %.2f s' % parameters[2])
print('h = %.2f' % parameters[3])

#Fit d18O
parameters, covariance = curve_fit(EMG, mean_time_base_iso, impulse_d18O, [30, 1, 1, 1])
impulse_d18O_fitted = EMG(mean_time_base_iso,
                          parameters[0],
                          parameters[1],
                          parameters[2],
                          parameters[3]) 
residuals_d18O_fitted = impulse_d18O - impulse_d18O_fitted 
impulse_d18O_gaussian = gaussian(mean_time_base_iso, 
                                mean_time_base_iso[impulse_d18O_fitted == max(impulse_d18O_fitted)][0], # peak
                                parameters[2])*parameters[3] # scale
# Print outbest-fit values
print('d18O EMG best fit ------------------------------')
print('mu = %.2f s' % parameters[0])
print('tau = %.2f' % parameters[1])
print('sigma = %.2f s' % parameters[2])
print('h = %.2f' % parameters[3])

#Fit dD
parameters, covariance = curve_fit(EMG, mean_time_base_iso, impulse_dD, [30, 1, 1, 1])
impulse_dD_fitted = EMG(mean_time_base_iso,
                          parameters[0],
                          parameters[1],
                          parameters[2],
                          parameters[3]) 
residuals_dD_fitted = impulse_dD - impulse_dD_fitted
impulse_dD_gaussian = gaussian(mean_time_base_iso, 
                                mean_time_base_iso[impulse_dD_fitted == max(impulse_dD_fitted)][0], # peak
                                parameters[2])*parameters[3] # scale
# Print outbest-fit values
print('dD EMG best fit ------------------------------')
print('mu = %.2f s' % parameters[0])
print('tau = %.2f' % parameters[1])
print('sigma = %.2f s' % parameters[2])
print('h = %.2f' % parameters[3])

# Plot normalized curve and standardized residuals
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
#ax.plot(mean_time_base_H2O, impulse_H2O, color = color_H2O, label = 'H$_2$O')
ax.plot(mean_time_base_H2O, impulse_H2O_fitted, color = color_H2O, label = 'H$_2$O')
ax.plot(mean_time_base_H2O, impulse_H2O_gaussian, color = color_H2O, linestyle = '--', label = 'H$_2$O')
#ax.scatter(mean_time_base_H2O, residuals_H2O_fitted/np.std(residuals_H2O_fitted), marker = 'x', color = color_H2O, alpha = 0.3)
#ax.scatter(mean_time_base_H2O, impulse_H2O,  marker = 'o', color = color_H2O, alpha = 0.3)

ax.plot(mean_time_base_iso, impulse_d18O_fitted, color = color_d18O, label = '$\delta^{18}$O')
ax.plot(mean_time_base_iso, impulse_d18O_gaussian, color = color_d18O, linestyle = '--', label = '$\delta^{18}$O')
#ax.plot(mean_time_base_iso, impulse_d18O_fitted/max(impulse_d18O_fitted), color = color_d18O, label = '$\delta^{18}$O')
#ax.scatter(mean_time_base_iso, residuals_d18O_fitted/np.std(residuals_d18O_fitted), marker = 'x', color = color_d18O, alpha = 0.3)
#ax.scatter(mean_time_base_iso, impulse_d18O,  marker = 'o', color = color_d18O, alpha = 0.3)

ax.plot(mean_time_base_iso, impulse_dD_fitted, color = color_dD, label = '$\delta$D')
ax.plot(mean_time_base_iso, impulse_dD_gaussian, color = color_dD, linestyle = '--', label = '$\delta$D')
#ax.scatter(mean_time_base_iso, residuals_dD_fitted/np.std(residuals_dD_fitted), marker = 'x', color = color_dD, alpha = 0.3)
#ax.scatter(mean_time_base_iso, impulse_dD,  marker = 'o', color = color_dD, alpha = 0.3)

ax.set_xlim([0, 70])
#ax.set_ylim([0, 1.1])
ax.set_xlabel('Time (s)', size=18)
ax.set_ylabel('Normalized Impulse Response (AU)', size=18)

ax.legend(fontsize = 18)

ax.grid()

ax.tick_params(axis='both', which='major', labelsize=18)

# Print area below peak to check consistency in power
area_diff       = np.abs(np.sum(impulse_H2O_fitted) - np.sum(impulse_H2O_gaussian))
area_diff_perc  = 100*area_diff/np.sum(impulse_H2O_fitted)
print('Gaussian vs EMG peak area difference for H2O is %.2f%%' % area_diff_perc)
area_diff       = np.abs(np.sum(impulse_d18O_fitted) - np.sum(impulse_d18O_gaussian))
area_diff_perc  = 100*area_diff/np.sum(impulse_d18O_fitted)
print('Gaussian vs EMG peak area difference for d18O is %.2f%%' % area_diff_perc)
area_diff       = np.abs(np.sum(impulse_dD_fitted) - np.sum(impulse_dD_gaussian))
area_diff_perc  = 100*area_diff/np.sum(impulse_dD_fitted)
print('Gaussian vs EMG peak area difference for dD is %.2f%%' % area_diff_perc)

#%% Calculate spectra for step changes with fft dB

#H2O
fs_H2O = 1/round(np.mean(np.diff(mean_time_base_H2O)), 3)
P_H2O = np.fft.rfft(impulse_H2O_fitted)
P_H2O_gauss = np.fft.rfft(impulse_H2O_gaussian)
P_H2O_reponse = P_H2O_gauss/P_H2O
f_H2O = np.fft.rfftfreq(len(mean_H2O), 1/fs_H2O)
#d18O
fs_d18O = 1/round(np.mean(np.diff(mean_time_base_iso)), 3)
P_d18O = np.fft.rfft(impulse_d18O_fitted)
P_d18O_gauss = np.fft.rfft(impulse_d18O_gaussian)
P_d18O_reponse = P_d18O_gauss/P_d18O
f_d18O = np.fft.rfftfreq(len(mean_d18O), 1/fs_d18O)
#dD
fs_dD = 1/round(np.mean(np.diff(mean_time_base_iso)), 3)
P_dD = np.fft.rfft(impulse_dD_fitted)
P_dD_gauss = np.fft.rfft(impulse_dD_gaussian)
P_dD_reponse = P_dD_gauss/P_dD
f_dD = np.fft.rfftfreq(len(mean_dD), 1/fs_dD)

#%% Define cut frequency
f_cut = 0.25 # Hz
#H2O
indexOI = np.where(np.abs(f_H2O)>f_cut)[0]
P_H2O_reponse.real[indexOI] = 0
P_H2O_reponse.imag[indexOI] = 0
# Invert response to get window in time domain
P_H2O_reponse_time = np.cumsum(irfft(P_H2O_reponse))

#d18O
indexOI = np.where(np.abs(f_d18O)>f_cut)[0]
P_d18O_reponse.real[indexOI] = 0
P_d18O_reponse.imag[indexOI] = 0
# Invert response to get window in time domain
P_d18O_reponse_time = np.cumsum(irfft(P_d18O_reponse))

#dD
indexOI = np.where(np.abs(f_dD)>f_cut)[0]
P_dD_reponse.real[indexOI] = 0
P_dD_reponse.imag[indexOI] = 0
# Invert response to get window in time domain
P_dD_reponse_time = np.cumsum(irfft(P_dD_reponse))

#%% Save response function
with open(filename_response_function, 'wb') as f:
    pickle.dump([P_H2O_reponse, P_d18O_reponse, P_dD_reponse,
                 f_H2O, f_d18O, f_dD,
                 fs_H2O, fs_d18O, fs_dD], f)

#%% Build 1st order butt. filter
# https://en.wikipedia.org/wiki/Time_constant#:~:text=In%20physics%20and%20engineering%2C%20the,a%20first%2Dorder%20LTI%20system.
# Relation of time constant to bandwidth
cutoff_H2O = 1/(2*np.pi*H2O_tau[0])
cutoff_d18O = 1/(2*np.pi*d18O_tau[0])
cutoff_dD = 1/(2*np.pi*dD_tau[0])
# butterworth order
n = 2
#% Build ideal filter
Omegas = np.linspace(np.min(f_H2O), np.max(f_H2O), len(f_H2O), endpoint = True)
G_squared_H2O = 1/(1+(Omegas/cutoff_H2O)**(2*n))
G_squared_d18O = 1/(1+(Omegas/cutoff_d18O)**(2*n))
G_squared_dD = 1/(1+(Omegas/cutoff_dD)**(2*n))

#%% Plot spectra
# https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20scale%20is%20a,energy%2C%20the%20factor%20is%2010.
fig, ax = plt.subplots(nrows = 3, figsize=(10 , 10), dpi=300, sharex = True)

ax[0].plot(f_H2O, np.abs(P_H2O), color = color_H2O, label = 'H$_2$O impulse fft')
ax[0].plot(f_H2O, np.abs(P_H2O_gauss), color = color_H2O, linestyle = '--', label = 'H$_2$O gaussian impulse fft')
ax[1].plot(f_H2O, np.abs(P_H2O_reponse), color = color_H2O,  label = 'H$_2$O required frequency response (Mag)')
ax[2].plot(f_H2O, np.angle(P_H2O_reponse), color = color_H2O,  label = 'H$_2$O required frequency response (Ang)')

ax[0].plot(f_d18O, np.abs(P_d18O), color = color_d18O, label = '$\delta^{18}$O impulse fft')
ax[0].plot(f_d18O, np.abs(P_d18O_gauss), color = color_d18O, linestyle = '--', label = '$\delta^{18}$O  gaussian impulse fft')
ax[1].plot(f_d18O, np.abs(P_d18O_reponse), color = color_d18O,  label = '$\delta^{18}$O  required frequency response')
ax[2].plot(f_d18O, np.angle(P_d18O_reponse), color = color_d18O,  label = '$\delta^{18}$O required frequency response (Ang)')

ax[0].plot(f_dD, np.abs(P_dD), color = color_dD, label = '$\delta$D impulse fft')
ax[0].plot(f_dD, np.abs(P_dD_gauss), color = color_dD, linestyle = '--', label = '$\delta$D  gaussian impulse fft')
ax[1].plot(f_dD, np.abs(P_dD_reponse), color = color_dD,  label = '$\delta$D  required frequency response')
ax[2].plot(f_dD, np.angle(P_dD_reponse), color = color_dD,  label = '$\delta$D required frequency response (Ang)')

ax[1].set_xlabel('Frequency (Hz)', size=18)
ax[1].set_ylim([0, 30])
for axis in ax:
    axis.set_xscale('log')
    axis.set_xlim([5e-3, 2])
    axis.set_ylabel('Amplitude', size=18)
    axis.legend(fontsize = 12)
    axis.grid()
    axis.tick_params(axis='both', which='major', labelsize=18)
    
ax[2].set_ylabel('Angle', size=18)



#%% fit impulse response frequency spectrum --> transfer function
fs_H2O = 1/round(np.mean(np.diff(mean_time_base_H2O)), 3)


fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)

ax.scatter(f_H2O, P_H2O_reponse, color = color_H2O, label = 'H$_2$O impulse fft')
ax.scatter(f_d18O, P_d18O_reponse, color = color_d18O, label = '$\delta^{18}$Oimpulse fft')
ax.scatter(f_dD, P_dD_reponse, color = color_dD, label = '$\delta$D impulse fft')
ax.grid()
ax.set_xscale('log')



#%%
# padding = 1
# mean_H2O_padded = np.zeros(len(mean_H2O)+padding)
# mean_H2O_padded[0:len(mean_H2O)] = mean_H2O

# P_H2O_reponse_time_padded = np.zeros(len(mean_H2O_padded))
# P_H2O_reponse_time_padded[0:len(P_H2O_reponse_time)] = P_H2O_reponse_time

order = 1
f_cut_lowpass = .1

#H2O
yf = np.fft.rfft(np.gradient(mean_H2O))
xf = np.fft.rfftfreq(len(mean_H2O), 1 / fs_H2O)
#yh = np.fft.rfft(np.gradient(P_H2O_reponse_time))
#xh = np.fft.rfftfreq(len(P_H2O_reponse_time), 1 / fs_H2O)
#yf_filtered = yf*yh
yf_filtered = yf*P_H2O_reponse
H2O_filt = irfft(yf_filtered)
H2O_filt = np.cumsum(H2O_filt.real)
# Apply lowpass filter to filtered timeseries
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_H2O) # Build butterworth filter
H2O_filt_filt = signal.filtfilt(b, a, H2O_filt) # Appy filter to the time 
# Apply lowpass filter to original timeseries
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_H2O) # Build butterworth filter
H2O_filt_filt_orig = signal.filtfilt(b, a, mean_H2O) # Appy filter to the time 

#d18O
yf = np.fft.rfft(np.gradient(mean_d18O))
xf = np.fft.rfftfreq(len(mean_d18O), 1 / fs_d18O)
#yh = np.fft.rfft(np.gradient(P_d18O_reponse_time))
#xh = np.fft.rfftfreq(len(P_d18O_reponse_time), 1 / fs_d18O)
#yf_filtered = yf*yh
yf_filtered = yf*P_d18O_reponse
d18O_filt = np.fft.irfft(yf_filtered)
d18O_filt = np.cumsum(d18O_filt.real)
# Apply lowpass filter to filtered timeseries 
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_d18O) # Build butterworth filter
d18O_filt_filt = signal.filtfilt(b, a, d18O_filt) # Appy filter to the time 
# Apply lowpass filter to original timeseries
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_d18O) # Build butterworth filter
d18O_filt_filt_orig = signal.filtfilt(b, a, mean_d18O) # Appy filter to the time 

#dD
yf = np.fft.rfft(np.gradient(mean_dD))
xf = np.fft.rfftfreq(len(mean_d18O), 1 / fs_dD)
#yh = np.fft.rfft(np.gradient(P_dD_reponse_time))
#xh = np.fft.rfftfreq(len(P_dD_reponse_time), 1 / fs_dD)
#yf_filtered = yf*yh
yf_filtered = yf*P_dD_reponse
dD_filt = np.fft.irfft(yf_filtered)
dD_filt = np.cumsum(dD_filt.real)
# Apply lowpass filter to filtered timeseries
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_dD) # Build butterworth filter
dD_filt_filt = signal.filtfilt(b, a, dD_filt) # Appy filter to the time 
# Apply lowpass filter to original timeseries
b, a = signal.butter(order, f_cut_lowpass, 'low', fs = fs_dD) # Build butterworth filter
dD_filt_filt_orig = signal.filtfilt(b, a, mean_dD) # Appy filter to the time 

#%% Add delay
H2O_dummy_time = np.array(mean_time_base_H2O*1e9, dtype='timedelta64[ns]')
H2O_filt_filt = delay_picarro_data(H2O_dummy_time, H2O_filt_filt, 'H2O')

iso_dummy_time = np.array(mean_time_base_iso*1e9, dtype='timedelta64[ns]')
d18O_filt_filt = delay_picarro_data(iso_dummy_time, d18O_filt_filt, 'd18O')
dD_filt_filt = delay_picarro_data(iso_dummy_time, dD_filt_filt, 'dD')



#%% Plot filtered step changes
#H2O_filt_filt = signal.convolve(H2O_filt, signal.windows.hann(100), mode = 'same')/sum(signal.windows.hann(100))
#d18O_filt_filt = signal.convolve(d18O_filt, signal.windows.hann(100), mode = 'same')/sum(signal.windows.hann(100))


fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
ax.plot(mean_time_base_H2O, H2O_filt_filt_orig, color = color_H2O, linewidth = 1.5, label = 'H$_2$O')
#ax.plot(mean_time_base_H2O, new_sig, color = 'r', linewidth = 1.5, label = 'H$_2$O fft filtered + BW LP')
ax.plot(mean_time_base_H2O, H2O_filt_filt, color = color_H2O, linestyle = '--', linewidth = 2, alpha = 0.3, label = 'H$_2$O fft filtered')

ax.plot(mean_time_base_iso, d18O_filt_filt_orig, color = color_d18O, linewidth = 1.5, label = '$\delta^{18}$O')
#ax.plot(mean_time_base_iso, new_sig, color = 'r', linewidth = 1.5, label = '$\delta^{18}$ fft filtered + BW LP')
ax.plot(mean_time_base_iso, d18O_filt_filt, color = color_d18O, linestyle = '--', linewidth = 2, alpha = 0.3, label = '$\delta^{18}O$ fft filtered')

ax.plot(mean_time_base_iso, dD_filt_filt_orig, color = color_dD, linewidth = 1.5, label = '$\delta$D')
#ax.plot(mean_time_base_iso, new_sig, color = 'r', linewidth = 1.5, label = '$\delta^{18}$ fft filtered + BW LP')
ax.plot(mean_time_base_iso, dD_filt_filt, color = color_dD, linestyle = '--', linewidth = 2, alpha = 0.3, label = '$\delta$D fft filtered')

ax.legend()
ax.set_ylim([-0.2, 2])
ax.set_xlim([0, 60])

# indexOI = np.where(f_d18O<f_cut)[0]
# parameters, covariance = curve_fit(mymod, f_d18O[indexOI], P_d18O[indexOI], [0, 0, 0])
# spectrum_d18O_fitted = mymod(f_d18O[indexOI], parameters[0], parameters[1], parameters[2])
# ax.plot(f_d18O[indexOI], spectrum_d18O_fitted, color = color_d18O)

# indexOI = np.where(f_dD<f_cut)[0]
# parameters, covariance = curve_fit(mymod, f_dD[indexOI], P_dD[indexOI], [0, 0, 0])
# spectrum_dD_fitted = mymod(f_dD[indexOI], parameters[0], parameters[1], parameters[2])
# ax.plot(f_dD[indexOI], spectrum_dD_fitted, color = color_dD)



