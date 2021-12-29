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
Variable_name               = 'Delta_D_H'
Edge                        = 'rising' # 'rising' or 'falling'

# Comment/Uncomment the step change of interest
# Calibration 2.1 RISING iso
start_date_str              = '2021-09-18 13:38:00'
stop_date_str               = '2021-09-18 13:42:00'
# # Calibration 2.1 FALLING iso
# start_date_str              = '2021-09-18 14:02:00'
# stop_date_str               = '2021-09-18 14:06:00'
# # Calibration 3.1 RISING iso
# start_date_str              = '2021-09-19 06:50:00'
# stop_date_str               = '2021-09-19 06:54:00'
# # Calibration 3.2 FALLING iso
# start_date_str              = '2021-09-19 07:12:00'
# stop_date_str               = '2021-09-19 07:16:00'
# # Calibration 4.6 RISING humidity
# start_date_str              = '2021-09-20 15:52:00'
# stop_date_str               = '2021-09-20 15:56:00'
# # Calibration 7.1 RISING iso
# start_date_str              = '2021-09-23 06:35:00'
# stop_date_str               = '2021-09-23 06:39:00'
# # Calibration 7.2 FALLING humidity
# start_date_str              = '2021-09-23 07:09:00'
# stop_date_str               = '2021-09-23 07:13:00'
# # Calibration 7.2 RISING humidity
# start_date_str              = '2021-09-23 07:15:00'
# stop_date_str               = '2021-09-23 07:19:00'
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

#%% Find locations of interest in timeseries
# Valve switch
index_switch = np.where(np.diff(df_Picarro_subset['ValveMask']) != 0)[0][0]
if Variable_name == 'Delta_D_H':
    #plt.plot(np.diff(df_Picarro_subset['Delta_D_H']))
    if Edge == 'falling':
        index_max = np.where(np.diff(df_Picarro_subset['Delta_D_H']) == np.min(np.diff(df_Picarro_subset['Delta_D_H'])))[0][0]
    elif Edge == 'rising':
        index_max = np.where(np.diff(df_Picarro_subset['Delta_D_H']) == np.max(np.diff(df_Picarro_subset['Delta_D_H'])))[0][0]
else:
    plt.plot(np.diff(df_Picarro_subset['H2O']))

#%%
fig, ax = plt.subplots(nrows = 4, figsize = (15,10))

# Plot isotopes
df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0])
ax[0].grid(which = 'both')
ax[0].set_ylabel('H$_2$O (ppm)')
#ax[0].set_ylim([10000, 20000])

#df_Picarro['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O raw')
df_Picarro['Delta_18_16'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O calibrated')
ax[1].legend()
ax[1].set_ylabel('$\delta^{18}$O (‰)')
ax[1].grid(which = 'both')

#df_Picarro['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD raw')
df_Picarro['Delta_D_H'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD calibrated')
ax[2].scatter(df_Picarro_subset.index[index_max], df_Picarro_subset['Delta_D_H'].iloc[index_max])
ax[2].legend()
ax[2].set_ylabel('$\delta$D [‰]')
ax[2].grid(which = 'both')


df_Picarro['ValveMask'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[3], label = 'd calibrated')
ax[3].legend()
ax[3].set_ylabel('Valve Mask []')
ax[3].grid(which = 'both')
