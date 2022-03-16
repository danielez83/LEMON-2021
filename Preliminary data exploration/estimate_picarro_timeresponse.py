#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 15:10:16 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
#from scipy.stats import linregress

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

#%% Configuration
Picarro_filename            = '../../Picarro_HIDS2254/2021/09/HIDS2254-20210918-DataLog_User.nc'
Variable_name               = 'Delta_D_H'#'H2O'#'Delta_D_H'
Edge                        = 'rising' # 'rising' or 'falling'

# Comment/Uncomment the step change of interest
# Calibration 2.1 RISING iso
start_date_str              = '2021-09-18 13:38:00'
stop_date_str               = '2021-09-18 13:42:00'
# # Calibration 2.1 FALLING iso
#start_date_str              = '2021-09-18 14:02:00'
#stop_date_str               = '2021-09-18 14:06:00'
# # Calibration 3.1 RISING iso
#start_date_str              = '2021-09-19 06:50:00'
#stop_date_str               = '2021-09-19 06:54:00'
# # Calibration 3.2 FALLING iso
# start_date_str              = '2021-09-19 07:12:00'
# stop_date_str               = '2021-09-19 07:16:00'
# # Calibration 4.6 RISING humidity
#start_date_str              = '2021-09-20 15:52:00'
#stop_date_str               = '2021-09-20 15:56:00'
# # Calibration 7.1 RISING iso
#start_date_str              = '2021-09-23 06:35:00'
#stop_date_str               = '2021-09-23 06:39:00'
# # Calibration 7.2 FALLING humidity
# start_date_str              = '2021-09-23 07:09:00'
# stop_date_str               = '2021-09-23 07:13:00'
# # Calibration 7.2 RISING humidity
#start_date_str              = '2021-09-23 07:15:00'
#stop_date_str               = '2021-09-23 07:19:00'
# # Calibraiton 7.3 FALLING iso
# start_date_str              = '2021-09-23 07:19:00'
# stop_date_str               = '2021-09-23 07:23:00'

#%% Import PICARRO data
file2read = nc.Dataset(Picarro_filename)
for dim in file2read.dimensions.values():
    print(dim)

for var in file2read.variables:
#    print(var)
    str_buff = var+" = file2read['"+var+"'][:]"
    exec(str_buff)
file2read.close()
# Convert NetCDF dates into a datetime vector
ncdate_picarro = nc.num2date(time, 'days since 1970-01-01 00:00:00.0', 
                             only_use_cftime_datetimes = False, 
                             only_use_python_datetimes=True)
ncdate_pd_picarro = pd.to_datetime(ncdate_picarro)

#%% Save data as pandas df
df_Picarro = pd.DataFrame(data = {'H2O':H2O,
                                  'Delta_18_16':Delta_18_16,
                                  'Delta_D_H': Delta_D_H,
                                  'AmbientPressure':AmbientPressure,
                                  'CavityPressure': CavityPressure,
                                  'CavityTemp':CavityTemp,
                                  'DasTemp':DasTemp,
                                  'WarmBoxTemp':WarmBoxTemp,
                                  'ValveMask':ValveMask}, index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
#df_Picarro = df_Picarro.resample("1S").mean()

#%% Susbset time series for specified interval
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

df_Picarro_subset = df_Picarro[(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)]

#%% Calculate delays between switching valve and signal
# NOW WORKING ONLY FOR RISING EDGE

# Find when the valve status switches/changes
index_switch = np.where(np.diff(df_Picarro_subset['ValveMask']) != 0)[0][0]

# Find the ~middle of risingin/falling edge
win_segment = [100, 50]
if Variable_name == 'Delta_D_H':
    #plt.plot(np.diff(df_Picarro_subset['Delta_D_H']))
    if Edge == 'falling':
        index_max = np.where(np.diff(df_Picarro_subset['Delta_D_H']) == np.min(np.diff(df_Picarro_subset['Delta_D_H'])))[0][0]
    elif Edge == 'rising':
        index_max = np.where(np.diff(df_Picarro_subset['Delta_D_H']) == np.max(np.diff(df_Picarro_subset['Delta_D_H'])))[0][0]
        # d18O
        segment_of_interest = df_Picarro_subset['Delta_18_16'].iloc[index_max-100:index_max-50]
        #segment_of_interest_d18O = segment_of_interest
        val_threshold = np.mean(segment_of_interest) + 2* np.std(segment_of_interest)
        index_start = index_max
        curr_val = df_Picarro_subset['Delta_18_16'].iloc[index_start]
        while curr_val > val_threshold:
            curr_val =  df_Picarro_subset['Delta_18_16'].iloc[index_start]
            index_start-=1
        d18O_rising_start = df_Picarro_subset.index[index_start]
        # dD
        segment_of_interest = df_Picarro_subset['Delta_D_H'].iloc[index_max-win_segment[0]:index_max-win_segment[1]]
        #segment_of_interest_dD = segment_of_interest
        val_threshold = np.mean(segment_of_interest) + 2* np.std(segment_of_interest)
        index_start = index_max
        curr_val = df_Picarro_subset['Delta_D_H'].iloc[index_start]
        while curr_val > val_threshold:
            curr_val =  df_Picarro_subset['Delta_D_H'].iloc[index_start]
            index_start-=1
        dD_rising_start = df_Picarro_subset.index[index_start]
        # Save switch time
        switch_time = df_Picarro_subset.index[index_switch]
        # Calculate delays in seconds
        d18O_delay  = d18O_rising_start - df_Picarro_subset.index[index_switch]
        d18O_delay  = d18O_delay.seconds + (d18O_delay.microseconds*1e-6)
        dD_delay    = dD_rising_start - df_Picarro_subset.index[index_switch]
        dD_delay    = dD_delay.seconds + (dD_delay.microseconds*1e-6)
        
elif Variable_name == 'H2O':
    #plt.plot(np.diff(df_Picarro_subset['H2O']))
    if Edge == 'falling':
        index_max = np.where(np.diff(df_Picarro_subset['H2O']) == np.min(np.diff(df_Picarro_subset['H2O'])))[0][0]
    elif Edge == 'rising':
        index_max = np.where(np.diff(df_Picarro_subset['H2O']) == np.max(np.diff(df_Picarro_subset['H2O'])))[0][0]
        segment_of_interest = df_Picarro_subset['H2O'].iloc[index_max-100:index_max-50]
        val_threshold = np.mean(segment_of_interest) + 2* np.std(segment_of_interest)
        index_start = index_max
        curr_val = df_Picarro_subset['H2O'].iloc[index_start]
        while curr_val > val_threshold:
            curr_val =  df_Picarro_subset['H2O'].iloc[index_start]
            index_start-=1
        H2O_rising_start = df_Picarro_subset.index[index_start]
        # Save switch time
        switch_time = df_Picarro_subset.index[index_switch]
        # Calculate delays in seconds
        H2O_delay  = H2O_rising_start - df_Picarro_subset.index[index_switch]
        H2O_delay  = H2O_delay.seconds + (H2O_delay.microseconds*1e-6)

#%% Calculate response time t(63.2%)
# Assuming a first-order system, see equation 11.21 in
# https://folk.ntnu.no/skoge/prosessregulering_lynkurs/literature/3.Skogestad_pages_from_Process-engineering_ch11.pdf
val_to_reach_scale = 0.632
win_segment_backward = [50, 0]
win_segment_forward = [400, 450]
d18O_segment_of_interest = df_Picarro_subset['Delta_18_16'].iloc[index_switch - win_segment_backward[0] : index_switch + win_segment_forward[1]]
dD_segment_of_interest = df_Picarro_subset['Delta_D_H'].iloc[index_switch - win_segment_backward[0] : index_switch + win_segment_forward[1]]
dex_segment_of_interest = dD_segment_of_interest-8*d18O_segment_of_interest
H2O_segment_of_interest = df_Picarro_subset['H2O'].iloc[index_switch - win_segment_backward[0] : index_switch + win_segment_forward[1]]
# Normalize segments
d18O_range = [np.mean(d18O_segment_of_interest[0:50]), np.mean(d18O_segment_of_interest[-50:-1])]
dD_range = [np.mean(dD_segment_of_interest[0:50]), np.mean(dD_segment_of_interest[-50:-1])]
H2O_range = [np.mean(H2O_segment_of_interest[0:50]), np.mean(H2O_segment_of_interest[-50:-1])]
#dex_range = [np.mean(dex_segment_of_interest[0:50]), np.mean(dex_segment_of_interest[-50:-1])]
 
d18O_segment_of_interest = (d18O_segment_of_interest + abs(np.min(d18O_range)))/abs(np.diff(d18O_range)[0])
dD_segment_of_interest = (dD_segment_of_interest + abs(np.min(dD_range)))/abs(np.diff(dD_range)[0])
H2O_segment_of_interest = (H2O_segment_of_interest + abs(np.min(H2O_range)))/abs(np.diff(H2O_range)[0])
#dex_segment_of_interest = (dex_segment_of_interest + abs(np.min(dex_range)))/abs(np.diff(dex_range)[0])


# Find when the step change is above the threshold
if Variable_name == 'Delta_D_H':
    #plt.plot(np.diff(df_Picarro_subset['Delta_D_H']))
    if Edge == 'falling':
        print("Nothing")
    elif Edge == 'rising':
        index_tau_d18O = np.where(d18O_segment_of_interest > val_to_reach_scale)[0][0]
        d18O_rising_tau = d18O_segment_of_interest.index[index_tau_d18O]
        index_tau_dD = np.where(dD_segment_of_interest > val_to_reach_scale)[0][0]
        dD_rising_tau = dD_segment_of_interest.index[index_tau_dD]
    d18O_tau = (d18O_rising_tau - d18O_rising_start).seconds + ((d18O_rising_tau - d18O_rising_start).microseconds*1e-6)
    dD_tau = (dD_rising_tau - dD_rising_start).seconds + ((dD_rising_tau - dD_rising_start).microseconds*1e-6)
    # Export time base vector
    time_base = np.cumsum(np.diff(d18O_segment_of_interest.index))
    time_base = np.concatenate([np.array([np.timedelta64(0, 'ns')]), time_base], axis = 0)
elif Variable_name == 'H2O':
    if Edge == 'falling':
        print("Nothing")
    elif Edge == 'rising':
        index_tau_H2O = np.where(H2O_segment_of_interest > val_to_reach_scale)[0][0]
    H2O_rising_tau = H2O_segment_of_interest.index[index_tau_H2O]
    H2O_tau = (H2O_rising_tau - H2O_rising_start).seconds + ((H2O_rising_tau - H2O_rising_start).microseconds*1e-6)
    # Export time base vector
    time_base = np.cumsum(np.diff(H2O_segment_of_interest.index))
    time_base = np.concatenate([np.array([np.timedelta64(0, 'ns')]), time_base], axis = 0)
time_base = time_base.astype(int)/1e9
    
#%% Print statistics
# https://www.baranidesign.com/faq-articles/2019/5/6/difference-between-sensor-response-time-and-sensor-time-constant-tau
response_scaling_factor = 5 # Assuming the response time is 5 times the time constant, see link above
# https://www.researchgate.net/post/Are_the_terms_Time_constant_and_Reponse_time_of_a_sensor_the_same

if Variable_name == 'Delta_D_H':
    print("Timing statistics for isotopes")
    print("d18O delay: %.2f s" % d18O_delay)
    print("d18O time constant (tau): %.2f s" % d18O_tau)
    print("d18O response timeL %.2f s" % (5*d18O_tau))
    print("")
    print("dD delay: %.2f s" % dD_delay)
    print("dD time constant (tau): %.2f s" % dD_tau)
    print("dD response timeL %.2f s" % (dD_tau*5))
elif Variable_name == 'H2O':
    print("Timing statistics for humidity")
    print("H2O delay: %.2f s" % H2O_delay)
    print("H2O time constant (tau): %.2f s" % H2O_tau)
    print("H2O response timeL %.2f s" % (5*H2O_tau))
    print("")
        

#%% Plot curves
fig, ax = plt.subplots(nrows = 4, figsize = (15,10), sharex = True)
# Humidity
ax[0].plot(H2O_segment_of_interest)
ax[0].set_ylabel('Norm. humidity')
ax[0].grid()
if Variable_name == 'H2O':
    ax[0].scatter(H2O_segment_of_interest.index[index_tau_H2O], 
                  H2O_segment_of_interest.iloc[index_tau_H2O], color = 'k')
    ax[0].text(H2O_segment_of_interest.index[index_tau_H2O], 
               H2O_segment_of_interest.iloc[index_tau_H2O], ('$\\tau_{63}$ = %.2f s' % H2O_tau))
    # ---
    ax[0].scatter(switch_time,
                  H2O_segment_of_interest[H2O_segment_of_interest.index == switch_time], color = 'k')
    ax[0].text(switch_time, 
               H2O_segment_of_interest[H2O_segment_of_interest.index == switch_time], 'Switch Valve')
    # ---
    ax[0].scatter(H2O_rising_start, 
                  H2O_segment_of_interest[H2O_segment_of_interest.index == H2O_rising_start], color = 'k')
    ax[0].text(H2O_rising_start, 
               H2O_segment_of_interest[H2O_segment_of_interest.index == H2O_rising_start], 'Step detected')

# d18O
ax[1].plot(d18O_segment_of_interest)
ax[1].set_ylabel('Norm. $\delta^{18}$O')
ax[1].grid()
if Variable_name == 'Delta_D_H':
    ax[1].scatter(d18O_segment_of_interest.index[index_tau_d18O], 
                  d18O_segment_of_interest.iloc[index_tau_d18O], color = 'k')
    ax[1].text(d18O_segment_of_interest.index[index_tau_d18O], 
               d18O_segment_of_interest.iloc[index_tau_d18O], ('$\\tau_{63}$ = %.2f s' % d18O_tau))
    # ---
    ax[1].scatter(switch_time,
                  d18O_segment_of_interest[d18O_segment_of_interest.index == switch_time], color = 'k')
    ax[1].text(switch_time, 
               d18O_segment_of_interest[d18O_segment_of_interest.index == switch_time], 'Switch Valve')
    # ---
    ax[1].scatter(d18O_rising_start, 
                  d18O_segment_of_interest[d18O_segment_of_interest.index == d18O_rising_start], color = 'k')
    ax[1].text(d18O_rising_start, 
               d18O_segment_of_interest[d18O_segment_of_interest.index == d18O_rising_start], 'Step detected')

# dD
ax[2].plot(dD_segment_of_interest)
ax[2].set_ylabel('Norm. $\delta$D')
ax[2].grid()
if Variable_name == 'Delta_D_H':
    ax[2].scatter(dD_segment_of_interest.index[index_tau_dD], 
                  dD_segment_of_interest.iloc[index_tau_dD])
    ax[2].text(dD_segment_of_interest.index[index_tau_dD], 
               dD_segment_of_interest.iloc[index_tau_dD], ('$\\tau_{63}$ = %.2f s' % dD_tau))
    # ---
    ax[2].scatter(switch_time,
                  dD_segment_of_interest[dD_segment_of_interest.index == switch_time], color = 'k')
    ax[2].text(switch_time, 
               dD_segment_of_interest[dD_segment_of_interest.index == switch_time], 'Switch Valve')
    # ---
    ax[2].scatter(dD_rising_start, 
                  dD_segment_of_interest[dD_segment_of_interest.index == dD_rising_start], color = 'k')
    ax[2].text(dD_rising_start, 
               dD_segment_of_interest[dD_segment_of_interest.index == dD_rising_start], 'Step detected')

# d-excess
ax[3].plot(dex_segment_of_interest)
ax[3].set_ylabel('d-excess')
ax[3].grid()