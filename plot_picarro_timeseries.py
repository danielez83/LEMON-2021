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
import pickle

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun
from filter_picarro_data import filter_picarro_data

#%% Configuration
#iMet_filename               = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210918-DataLog_User.nc'
#Flight_table_filename       = '../Excel/Flights_Table.csv'
#Flight_OI                   =  3#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
Calibration_param_filename  = 'Standard_reg_param_STD_corr.pkl'
#display                     = 'binned' #'raw', 'binned'
#bin_mode                    = 'auto' #'auto', 'manual'
#bins                        = np.arange(400, 20000, 400)
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

filter_data                 = 'no'

start_date_str              = '2021-09-18 12:00:00'
stop_date_str               = '2021-09-18 15:00:00'

#%% Highlight section --------------------------------------------------------
SOI = 0
# Calibrations ---------------------------------------------------------------
# start_SOI                   = ['2021-09-17 17:55:00', '2021-09-17 18:09:00']
# stop_SOI                    = ['2021-09-17 18:02:00', '2021-09-17 18:16:00']
# start_SOI                   = ['2021-09-18 13:44:00', '2021-09-18 14:10:00']
# stop_SOI                    = ['2021-09-18 13:54:00', '2021-09-18 14:18:00']
# start_SOI                   = ['2021-09-19 6:56:00', '2021-09-19 7:15:00']
# stop_SOI                    = ['2021-09-19 7:06:00', '2021-09-19 7:25:00']
# start_SOI                   = ['2021-09-20 11:45:00', '2021-09-20 12:15:00']
# stop_SOI                    = ['2021-09-20 11:55:00', '2021-09-20 12:25:00']
#start_SOI                   = ['2021-09-20 10:30:00']
#stop_SOI                    = ['2021-09-20 10:45:00']
# start_SOI                   = ['2021-09-21 14:11:00', '2021-09-21 14:45:00']
# stop_SOI                    = ['2021-09-21 14:26:00', '2021-09-21 15:00:00']
# start_SOI                   = ['2021-09-22 12:02:00', '2021-09-22 12:34:00']
# stop_SOI                    = ['2021-09-22 12:14:00', '2021-09-22 12:43:00']
# start_SOI                   = ['2021-09-23 6:55:00', '2021-09-23 7:31:00']
# stop_SOI                    = ['2021-09-23 7:05:00', '2021-09-23 7:41:00']
start_SOI                   = ['2021-09-23 9:15:00']
stop_SOI                    = ['2021-09-23 9:45:00']


#%% Pressure to alitude conversion
# https://www.weather.gov/epz/wxcalc_pressurealtitude
Torr2feet = lambda p:(1-((p*1.33322)/1013.25)**(0.190284))*145366.45
Torr2meters = lambda p: ((1-((p*1.33322)/1013.25)**(0.190284))*145366.45)*0.3048

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
                                  'd18O':Delta_18_16,
                                  'dD': Delta_D_H,
                                  'AmbientPressure':AmbientPressure,
                                  'CavityPressure': CavityPressure,
                                  'CavityTemp':CavityTemp,
                                  'DasTemp':DasTemp,
                                  'WarmBoxTemp':WarmBoxTemp,
                                  'ValveMask':ValveMask}, index = ncdate_pd_picarro)

# Save data (temporary) ------------------------------------------------------
#with open('picarro_data_20210918_1200_1500.pkl', 'wb') as f:
#    pickle.dump(df_Picarro, f)
# ----------------------------------------------------------------------------

# Filter data
if filter_data == 'yes':
    df_Picarro['H2O'] = filter_picarro_data(df_Picarro['H2O'], df_Picarro.index, 'H2O')
    df_Picarro['d18O'] = filter_picarro_data(df_Picarro['d18O'], df_Picarro.index, 'd18O')
    df_Picarro['dD'] = filter_picarro_data(df_Picarro['dD'], df_Picarro.index, 'dD')

# Resample and center at 1 sec freq
df_Picarro = df_Picarro.resample("1S").mean()

#%% Calibrate Picarro data
calibration_paramters = pd.read_pickle(Calibration_param_filename)
DOI = df_Picarro.index[1000].day
tot = calibration_paramters.index.day == DOI
IOI = np.where(tot==True)
IOI = IOI[0][0]

df_Picarro_data_calibrated = df_Picarro.copy()
# Humidity-isotope correction
df_Picarro_data_calibrated['d18O'] = hum_corr_fun(df_Picarro['H2O'], 
                                               df_Picarro['d18O'], 
                                               18, 17000, 'mean')
df_Picarro_data_calibrated['dD'] = hum_corr_fun(df_Picarro['H2O'], 
                                               df_Picarro['dD'], 
                                               2, 17000, 'mean')
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

#%% Add altitude to df_Picarro_data_calibrated
altitude = Torr2meters(df_Picarro_data_calibrated['AmbientPressure'])
df_Picarro_data_calibrated['Altitude'] = altitude

#%% Plot time series of specified interval
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

fig, ax = plt.subplots(nrows = 4, figsize = (15,10))

# Plot isotopes
df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0])
ax[0].grid(which = 'both')
ax[0].set_ylabel('H$_2$O (ppm)')
#ax[0].set_ylim([10000, 20000])

#df_Picarro['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O raw')
df_Picarro_data_calibrated['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O calibrated')
ax[1].legend()
ax[1].set_ylabel('$\delta^{18}$O (‰)')
ax[1].grid(which = 'both')

#df_Picarro['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD raw')
df_Picarro_data_calibrated['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD calibrated')
ax[2].legend()
ax[2].set_ylabel('$\delta$D [‰]')
ax[2].grid(which = 'both')

df_Picarro_data_calibrated['dexcess'] = df_Picarro_data_calibrated['dD'] - 8*df_Picarro_data_calibrated['d18O']

df_Picarro_data_calibrated['dexcess'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[3], label = 'd calibrated')
ax[3].legend()
ax[3].set_ylabel('d-excess [‰]')
ax[3].grid(which = 'both')

print("Mean H2O = %d ± %d ‰" % (
    df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean(),
    df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()))

print("Mean d18O = %.2f ± %.2f ‰" % (
    df_Picarro['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean(),
    df_Picarro['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()))

print("Mean dD = %.2f ± %.2f ‰" % (
    df_Picarro['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean(),
    df_Picarro['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()))

# PLOT SOI?
if SOI>0:
    for curr_SOI_start, curr_SOI_stop in zip(start_SOI, stop_SOI):
        start_date = datetime.datetime.strptime(curr_SOI_start, '%Y-%m-%d %H:%M:%S')
        stop_date = datetime.datetime.strptime(curr_SOI_stop, '%Y-%m-%d %H:%M:%S')
        # H2O
        df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0], color = 'r')
        curr_mean = df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean()
        curr_std = df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()
        buff_text = ("H2O = %d ± %d pppm" % (curr_mean, curr_std))
        ax[0].text(start_date, curr_mean + 5*curr_std, buff_text, color = 'r')

        # d18O
        df_Picarro_data_calibrated['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O SOI', color = 'r')
        curr_mean = df_Picarro_data_calibrated['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean()
        curr_std = df_Picarro_data_calibrated['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()
        buff_text = ("d18O = %.2f ± %.2f ‰" % (curr_mean, curr_std))
        ax[1].text(start_date, curr_mean + 5*curr_std, buff_text, color = 'r')        
        
        # dD
        df_Picarro_data_calibrated['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD SOI', color = 'r')
        curr_mean = df_Picarro_data_calibrated['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean()
        curr_std = df_Picarro_data_calibrated['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()
        buff_text = ("dD = %.2f ± %.2f ‰" % (curr_mean, curr_std))
        ax[2].text(start_date, curr_mean + 2*curr_std, buff_text, color = 'r')

#%% Plot time series of specified interval
fig, ax = plt.subplots(nrows = 3, figsize = (15,10))
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

# Plot altitude and instrument status
df_Picarro_data_calibrated['Altitude'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0])
ax[0].grid(which = 'both')
ax[0].set_ylabel('Altitude (m AMSL)')

df_Picarro['ValveMask'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1])
ax[1].set_ylabel('Valve Mask (-)')
ax[1].grid(which = 'both')

df_Picarro['CavityPressure'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2])
ax[2].legend
ax[2].set_ylabel('Cavity Pressure [Torr]')
ax[2].grid(which = 'both')

if SOI>0:
    for curr_SOI_start, curr_SOI_stop in zip(start_SOI, stop_SOI):
        start_date = datetime.datetime.strptime(curr_SOI_start, '%Y-%m-%d %H:%M:%S')
        stop_date = datetime.datetime.strptime(curr_SOI_stop, '%Y-%m-%d %H:%M:%S')
        df_Picarro_data_calibrated['Altitude'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0], color = 'r')      
        df_Picarro['ValveMask'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], color = 'r')
        df_Picarro['CavityPressure'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], color = 'r')    


print("Mean cavity pressure = %.3f ± %.3f ‰" % (
    df_Picarro['CavityPressure'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].mean(),
    df_Picarro['CavityPressure'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].std()))