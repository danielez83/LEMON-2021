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
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210918-DataLog_User.nc'
Picarro_filename_FARLAB     = '../netcdf_V1/LEMON2021_f07_10s.nc'
Flight_table_filename       = '../Excel/Flights_Table.csv'
Flight_OI                   = 7#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
trim_val                    = 40
Calibration_param_filename  = 'Standard_reg_param_STD_corr.pkl'
display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'auto' #'auto', 'manual'
bins                        = np.arange(400, 20000, 400)
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

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
                                  'WarmBoxTemp':WarmBoxTemp}, index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
df_Picarro = df_Picarro.resample("10S").mean()

#%% Import PICARRO FARLAB data
file2read = nc.Dataset(Picarro_filename_FARLAB)
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
df_Picarro_FARLAB = pd.DataFrame(data = {'H2O':(q*1000)/0.62198,
                                         'd18O':delta_18O,
                                         'dD': delta_D},
                                         #'AmbientPressure':AmbientPressure,
                                         #'CavityPressure': CavityPressure,
                                         #'CavityTemp':CavityTemp,
                                         #'DasTemp':DasTemp,
                                         #'WarmBoxTemp':WarmBoxTemp}, 
                                         index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
#df_Picarro_FARLAB = df_Picarro_FARLAB.resample("1S").interpolate()
#%% Import Flights table to filter only flight time
df_Flight_table = pd.read_csv(Flight_table_filename)
df_Flight_table['Takeoff_fulldate'] = pd.to_datetime(df_Flight_table['Takeoff_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')
df_Flight_table['Landing_fulldate'] = pd.to_datetime(df_Flight_table['Landing_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')

start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
if Flight_OI == 1:
    start_date = start_date + datetime.timedelta(minutes = 5)
    #stop_date = stop_date - datetime.timedelta(minutes = 5)   
# Adjust time for comparison. It is flight dependent
if Flight_OI == 7:
    start_date = start_date + datetime.timedelta(minutes = 5)
    stop_date = stop_date - datetime.timedelta(minutes = 5)     
    
df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]
#df_iMet_mask = (df_iMet.index > start_date.iloc[0]) & (df_iMet.index < stop_date.iloc[0])
#df_iMet_subset = df_iMet.loc[df_iMet_mask]

#%% Calibrate Picarro data
calibration_paramters = pd.read_pickle(Calibration_param_filename)
DOI = df_Picarro_subset.index[100].day
tot = calibration_paramters.index.day == DOI
IOI = np.where(tot==True)
IOI = IOI[0][0]

Picarro_data_calibrated = df_Picarro_subset.copy()
# Humidity-isotope correction
Picarro_data_calibrated['d18O'] = hum_corr_fun(df_Picarro_subset['H2O'], 
                                               df_Picarro_subset['d18O'], 
                                               18, 17000, 'mean')
Picarro_data_calibrated['dD'] = hum_corr_fun(df_Picarro_subset['H2O'], 
                                               df_Picarro_subset['dD'], 
                                               2, 17000, 'mean')
# Isotope calibration
if calibrate_isotopes == 'yes':
    Picarro_data_calibrated['d18O'] = Picarro_data_calibrated['d18O']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
    Picarro_data_calibrated['dD'] = Picarro_data_calibrated['dD']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]
else:
    Picarro_data_calibrated['d18O'] = df_Picarro_subset['d18O']
    Picarro_data_calibrated['dD'] = df_Picarro_subset['dD']

# Humidity calibration, using OPTISONDE relationship
if calibrate_humidity == 'yes':
    Picarro_data_calibrated['H2O'] = Picarro_data_calibrated['H2O']*0.957 - 6.431
else:
    Picarro_data_calibrated['H2O'] = Picarro_data_calibrated['H2O']

#%% Find indexes to match the time series with my calibration and the one with Harald processing
start_match     = df_Picarro_FARLAB.index[trim_val]
stop_match      = df_Picarro_FARLAB.index[-trim_val]
start_match     = np.where(Picarro_data_calibrated.index == start_match)[0]
stop_match      = np.where(Picarro_data_calibrated.index == stop_match)[0]

df_Picarro_FARLAB               = df_Picarro_FARLAB.iloc[trim_val:-trim_val, :]
df_Picarro_calibrated_trimmed   = Picarro_data_calibrated.iloc[start_match[0]:stop_match[0], :]

#%% Visualization of differences, time series
fig, ax = plt.subplots(nrows=4, figsize=(10,15), sharex = True)
plt.subplots_adjust(hspace = .1) 
ax[0].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['d18O'] - df_Picarro_calibrated_trimmed['d18O'])
ax[0].set_ylabel('$\delta{18}$O$_{FaVaCal - NEW}$ (‰)', fontsize=14)
ax[0].grid()
#ax[0].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['d18O'])
#ax[0.plot()]

ax[1].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['dD'] - df_Picarro_calibrated_trimmed['dD'])
ax[1].set_ylabel('$\delta$D$_{FaVaCal - NEW}$ (‰)', fontsize=14)
ax[1].grid()
#ax[1].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['dD'])

ax[2].plot(df_Picarro_FARLAB.index, 
           (df_Picarro_FARLAB['dD'] - 8*df_Picarro_FARLAB['d18O']) - (df_Picarro_calibrated_trimmed['dD']- 8* df_Picarro_calibrated_trimmed['d18O']))
ax[2].set_ylabel('d-excess$_{FaVaCal - NEW}$ (‰)', fontsize=14)
ax[2].grid()

ax[3].plot(df_Picarro_FARLAB.index, (df_Picarro_FARLAB['H2O']))# - df_Picarro_calibrated_trimmed['H2O'])
ax[3].set_ylabel('H$_{2}$O$_{NEW}$ (ppm)', fontsize=14)
ax[3].grid()
#ax[2].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['dD'] - 8*df_Picarro_FARLAB['d18O'])

#ax[3].plot(Picarro_data_calibrated.index, Picarro_data_calibrated['dD'])
#ax[3].plot(df_Picarro_FARLAB.index, df_Picarro_FARLAB['dD'])
print("Avg. d18O diff = %.2f" % (np.mean(df_Picarro_FARLAB['d18O'] - df_Picarro_calibrated_trimmed['d18O'])))
print("Avg. dD diff = %.2f" % (np.mean(df_Picarro_FARLAB['dD'] - df_Picarro_calibrated_trimmed['dD'])))
print("Avg. dex diff = %.2f" % np.mean((df_Picarro_FARLAB['dD'] - 8*df_Picarro_FARLAB['d18O']) - (df_Picarro_calibrated_trimmed['dD']- 8* df_Picarro_calibrated_trimmed['d18O'])))
print("Avg. H2O diff = %.2f" % (np.mean(df_Picarro_FARLAB['H2O'] - df_Picarro_calibrated_trimmed['H2O'])))
#%%
fig, ax = plt.subplots(nrows=3, figsize=(10,15), sharex = True)

ax[0].scatter(((df_Picarro_FARLAB['H2O'])),# - df_Picarro_calibrated_trimmed['H2O']), 
              (df_Picarro_FARLAB['d18O'] - df_Picarro_calibrated_trimmed['d18O']))
ax[0].set_ylabel('$\delta{18}$O$_{FaVaCal - NEW}$ (‰)', fontsize=14)
ax[0].grid()

ax[1].scatter(((df_Picarro_FARLAB['H2O'])),# - df_Picarro_calibrated_trimmed['H2O']), 
              (df_Picarro_FARLAB['dD'] - df_Picarro_calibrated_trimmed['dD']))
ax[1].set_ylabel('$\delta$D$_{FaVaCal - NEW}$ (‰)', fontsize=14)
ax[1].grid()

ax[2].scatter(((df_Picarro_FARLAB['H2O'])),# - df_Picarro_calibrated_trimmed['H2O']), 
              (df_Picarro_FARLAB['dD']-8*df_Picarro_FARLAB['d18O']) - (df_Picarro_calibrated_trimmed['dD']-8*df_Picarro_calibrated_trimmed['d18O']))
ax[2].set_ylabel('d-excess$_{FaVaCal - NEW}$ (‰)')
ax[2].set_xlabel('H$_{2}$O$_{NEW}$ (ppm)', fontsize=14)
ax[2].grid()

#%%
acc = (np.max(df_Picarro_FARLAB['dD'].rolling(window=10).mean() - df_Picarro_calibrated_trimmed['dD'].rolling(window=10).mean()) -
       np.min(df_Picarro_FARLAB['dD'].rolling(window=10).mean() - df_Picarro_calibrated_trimmed['dD'].rolling(window=10).mean()))/2
print("Accuracy: %.2f" % acc)
