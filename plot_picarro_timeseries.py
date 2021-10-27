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

from hum_corr_fun import hum_corr_fun

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

start_date_str              = '2021-09-18 13:38:00'
stop_date_str               = '2021-09-18 13:40:00'

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
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']*0.857 - 6.431
else:
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']

#%% Add altitude to df_Picarro_data_calibrated
altitude = Torr2meters(df_Picarro_data_calibrated['AmbientPressure'])
df_Picarro_data_calibrated['Altitude'] = altitude

#%% Plot time series of specified interval
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

fig, ax = plt.subplots(nrows = 3, figsize = (15,10))

# Plot isotopes
df_Picarro['H2O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[0])
ax[0].grid(which = 'both')
ax[0].set_ylabel('H$_2$O (ppm)')

df_Picarro['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O raw')
df_Picarro_data_calibrated['d18O'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[1], label = 'd18O calibrated')
ax[1].legend()
ax[1].set_ylabel('$\delta^{18}$O (‰)')
ax[1].grid(which = 'both')

df_Picarro['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD raw')
df_Picarro_data_calibrated['dD'][(df_Picarro.index > start_date) & (df_Picarro.index < stop_date)].plot(ax = ax[2], label = 'dD calibrated')
ax[2].legend
ax[2].set_ylabel('$\delta$D [‰]')
ax[2].grid(which = 'both')

#%% Plot time series of specified interval
fig, ax = plt.subplots(nrows = 3, figsize = (15,10))

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