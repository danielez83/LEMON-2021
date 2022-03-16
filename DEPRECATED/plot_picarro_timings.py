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
from scipy import signal
from scipy.fft import rfft, rfftfreq
from scipy.stats import norm
from scipy.optimize import curve_fit
from scipy.special import erfc


#%% Configuration
filename_step_data      = '../Excel/step_change_tests.csv'
filename_step_timings   = '../Excel/step_change_timings.csv'

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

#%% Try to filter dat
#n = 1                    # butterworth order
#Omega_c = 0.026525823848649224
#b, a = signal.butter(n, Omega_c, 'low') # Build butterworth filter
#mean_H2O = signal.filtfilt(b, a, mean_H2O)
#mean_d18O = signal.filtfilt(b, a, mean_d18O)
#mean_dD = signal.filtfilt(b, a, mean_dD)

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

# Fit H2O
parameters, covariance = curve_fit(EMG, mean_time_base_H2O, impulse_H2O, [30, 1, 1, 1])
impulse_H2O_fitted = EMG(mean_time_base_H2O,
                         parameters[0], # mu
                         parameters[1], # tau
                         parameters[2], # sigma
                         parameters[3]) # h
# Calculate residuals
residuals_H2O_fitted = impulse_H2O - impulse_H2O_fitted
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
# Print outbest-fit values
print('dD EMG best fit ------------------------------')
print('mu = %.2f s' % parameters[0])
print('tau = %.2f' % parameters[1])
print('sigma = %.2f s' % parameters[2])
print('h = %.2f' % parameters[3])

# Plot normalized curve and standardized residuals
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
#ax.plot(mean_time_base_H2O, impulse_H2O, color = color_H2O, label = 'H$_2$O')
ax.plot(mean_time_base_H2O, impulse_H2O_fitted/max(impulse_H2O_fitted), color = color_H2O, label = 'H$_2$O')
#ax.scatter(mean_time_base_H2O, residuals_H2O_fitted/np.std(residuals_H2O_fitted), marker = 'x', color = color_H2O, alpha = 0.3)
#ax.scatter(mean_time_base_H2O, impulse_H2O,  marker = 'o', color = color_H2O, alpha = 0.3)

#ax.plot(mean_time_base_iso, impulse_d18O, color = color_d18O, label = '$\delta^{18}$O')
ax.plot(mean_time_base_iso, impulse_d18O_fitted/max(impulse_d18O_fitted), color = color_d18O, label = '$\delta^{18}$O')
#ax.scatter(mean_time_base_iso, residuals_d18O_fitted/np.std(residuals_d18O_fitted), marker = 'x', color = color_d18O, alpha = 0.3)
#ax.scatter(mean_time_base_iso, impulse_d18O,  marker = 'o', color = color_d18O, alpha = 0.3)

#ax.plot(mean_time_base_iso, impulse_dD, color = color_dD, label = '$\delta$D')
ax.plot(mean_time_base_iso, impulse_dD_fitted/max(impulse_dD_fitted), color = color_dD, label = '$\delta$D')
#ax.scatter(mean_time_base_iso, residuals_dD_fitted/np.std(residuals_dD_fitted), marker = 'x', color = color_dD, alpha = 0.3)
#ax.scatter(mean_time_base_iso, impulse_dD,  marker = 'o', color = color_dD, alpha = 0.3)

ax.set_xlim([0, 70])
ax.set_ylim([0, 1.1])
ax.set_xlabel('Time (s)', size=18)
ax.set_ylabel('Normalized Impulse Response (AU)', size=18)

ax.legend(fontsize = 18)

ax.grid()

ax.tick_params(axis='both', which='major', labelsize=18)


#%% Calculate spectra for step changes with fft
fs_H2O = 1/round(np.mean(np.diff(mean_time_base_H2O)), 3)
#P_H2O = rfft(np.gradient(mean_H2O))
P_H2O = rfft(impulse_H2O_fitted)
P_H2O = 20*np.log10(np.abs(P_H2O)/np.abs(P_H2O[1])) # convert do dB
f_H2O = rfftfreq(len(mean_H2O), 1/fs_H2O)

fs_iso = 1/round(np.mean(np.diff(mean_time_base_iso)), 3)
#P_d18O = rfft(np.gradient(mean_d18O))
P_d18O = rfft(impulse_d18O_fitted)
P_d18O = 20*np.log10(np.abs(P_d18O)/np.abs(P_d18O[1])) # convert do dB
f_d18O = rfftfreq(len(mean_d18O), 1/fs_iso)

#P_dD = rfft(np.gradient(mean_dD))
P_dD = rfft(impulse_dD_fitted)
P_dD = 20*np.log10(np.abs(P_dD)/np.abs(P_dD[1])) # convert do dB
f_dD = rfftfreq(len(mean_dD), 1/fs_iso)


#%% Build 1st order butt. filter
# https://en.wikipedia.org/wiki/Time_constant#:~:text=In%20physics%20and%20engineering%2C%20the,a%20first%2Dorder%20LTI%20system.
# Relation of time constant to bandwidth
cutoff_H2O = 1/(2*np.pi*H2O_tau[0])
cutoff_d18O = 1/(2*np.pi*d18O_tau[0])
cutoff_dD = 1/(2*np.pi*dD_tau[0])
# butterworth order
n = 1
#% Build ideal filter
Omegas = np.linspace(np.min(f_H2O), np.max(f_H2O), len(f_H2O), endpoint = True)
G_squared_H2O = 1/(1+(Omegas/cutoff_H2O)**(2*n))
G_squared_d18O = 1/(1+(Omegas/cutoff_d18O)**(2*n))
G_squared_dD = 1/(1+(Omegas/cutoff_dD)**(2*n))

#%% Plot spectra
# https://dspillustrations.com/pages/posts/misc/decibel-conversion-factor-10-or-factor-20.html#:~:text=The%20dB%20scale%20is%20a,energy%2C%20the%20factor%20is%2010.
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)

ax.plot(f_H2O, P_H2O, color = color_H2O, label = 'H$_2$O impulse fft')
ax.plot(f_d18O, P_d18O, color = color_d18O, label = '$\delta^{18}$O impulse fft')
ax.plot(f_dD, P_dD, color = color_dD, label = '$\delta$D impulse fft')

#ax.plot(omega, 10*np.log10(mag**2), color = [1,0,1], label = "1$^{st}$ ord. low-pass")

#ax.plot(omega1, 10*np.log10(mag1**2), color = [1,0,1])

ax.plot(f_H2O, 10*np.log10(G_squared_H2O), '--', color = color_H2O, label = "H$_2$O 1$^{st}$ ord. LP")
ax.plot(f_d18O, 10*np.log10(G_squared_d18O), '--', color = color_d18O, label = "$\delta^{18}$O1$^{st}$ ord. LP")
ax.plot(f_dD, 10*np.log10(G_squared_dD), '--', color = color_dD, label = "$\delta$D1$^{st}$ ord. LP")

#ax.plot([0.001, 1], [-3, -3], 'k--', label = "-3 dB passband")
ax.fill_betweenx([-3, 0], 0.001, 1, color = 'grey', alpha = 0.3)



ax.set_xscale('log')
ax.set_xlim([5e-3, 0.5])
ax.set_ylim([-20, 1])
ax.set_xlabel('Frequency (Hz)', size=18)
ax.set_ylabel('Magnitude (dB)', size=18)

ax.legend(fontsize = 18)

ax.grid()

ax.tick_params(axis='both', which='major', labelsize=18)

#%% Create windows for convolving the orginal signal with the impulse response function
win_length = 200
x = np.linspace(1,win_length, win_length)

# Fit H2O
parameters, covariance = curve_fit(EMG, np.linspace(1, len(impulse_H2O), len(impulse_H2O)), 
                                   impulse_H2O, [120, 1, 1, 1])
y = EMG(x,
        win_length/2-3, # mu
        parameters[1], # tau
        parameters[2], # sigma
        parameters[3]) # h
win_H2O = y/max(y)
#%%Fit d18O
parameters, covariance = curve_fit(EMG, np.linspace(1, len(impulse_d18O), len(impulse_d18O)),
                                   impulse_d18O, [120, 1, 1, 1])
y = EMG(x,
        win_length/2-4, # mu
        parameters[1], # tau
        parameters[2], # sigma
        parameters[3]) # h
win_d18O = y/max(y)
#%%Fit dD
parameters, covariance = curve_fit(EMG, np.linspace(1, len(impulse_dD), len(impulse_dD)), 
                                   impulse_dD, [120, 1, 1, 1])
x = np.linspace(1,win_length, win_length)
y = EMG(x,
        win_length/2-5, # mu
        parameters[1], # tau
        parameters[2], # sigma
        parameters[3]) # h
win_dD = y/max(y)

#%% Convolve signal H2O
mean_H2O_filt = signal.convolve(mean_H2O, win_H2O, mode='same')/sum(win_H2O)

fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
ax.plot(mean_time_base_H2O, mean_H2O, color = color_H2O, linewidth = 1.5, label = 'H$_2$O')
ax.plot(mean_time_base_H2O, mean_H2O_filt, label = 'H$_2$O filtered')
ax.legend()
#%% Convolve signal d18O
mean_d18O_filt = signal.convolve(mean_d18O, win_d18O, mode='same')/sum(win_d18O)
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
ax.plot(mean_time_base_iso, mean_d18O, color = color_d18O, linewidth = 1.5, label = '$\delta^{18}$O')
ax.plot(mean_time_base_iso, mean_d18O_filt, label = '$\delta^{18}$O filtered')
ax.legend()
#%% Convolve signal dD
mean_dD_filt = signal.convolve(mean_dD, win_dD, mode='same')/sum(win_dD)
fig, ax = plt.subplots(figsize=(10 , 10), dpi=150)
ax.plot(mean_time_base_iso, mean_dD, color = color_dD, linewidth = 1.5, label = '$\delta$D')
ax.plot(mean_time_base_iso, mean_dD_filt, label = '$\delta$D filtered')
ax.legend()



#%%
F, P = signal.welch(np.gradient(mean_H2O), fs = fs_H2O)                          # Use default parameters for welch function (hann window, win length 256)
fig_SP, ax_SP = plt.subplots(figsize = (15,5))
ax_SP.loglog(F, P, color = 'k', linewidth = 2, label = "Original TS")

F, P = signal.welch(np.gradient(mean_H2O_filt), fs = fs_iso)                          # Use default parameters for welch function (hann window, win length 256)
ax_SP.loglog(F, P, color = 'r', linewidth = 2, label = "Filtered TS")

