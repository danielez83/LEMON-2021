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
#iMet_filename               = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210919-DataLog_User.nc'
Flight_table_filename       = '../Excel/Flights_Table.csv'
Flight_OI                   =  8#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
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
df_Picarro = df_Picarro.resample("1S").mean()

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

#%% Visualization of single data points
fig, ax = plt.subplots(figsize=(6,6))

ax.scatter(Picarro_data_calibrated['H2O'], Picarro_data_calibrated['dD'],
           s = 16, marker = 'o', facecolors='none',
           c = Picarro_data_calibrated.index, cmap = 'jet') #edgecolors='k')edgecolors='b'))
ax.grid()
ax.set(xlabel = 'H$_{2}$O (ppm)', ylabel = '$\delta$D (‰)')

buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
fig.suptitle(buff_text)

fig.tight_layout()
fig.subplots_adjust(top=0.95)
# =============================================================================
# #%% Visualization of single data points
# fig, ax = plt.subplots(figsize=(6,6))
# 
# ax.scatter(Picarro_data_calibrated['H2O'], Picarro_data_calibrated['dD'],
#            s = 16, marker = 'o', facecolors='none',
#            c = Torr2meters(Picarro_data_calibrated['AmbientPressure']),
#            cmap = 'jet') #edgecolors='k')edgecolors='b'))
# ax.grid()
# ax.set(xlabel = 'H$_{2}$O (ppm)', ylabel = '$\delta$D (‰)')
# =============================================================================

 