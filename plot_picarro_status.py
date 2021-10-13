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
#iMet_filename      = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename   = '../Picarro_HIDS2254/2021/09/HIDS2254-20210917-DataLog_User.nc'
Flight_table_filename = '../Excel/Flights_Table.csv'
Flight_OI =  3#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
Calibration_param_filename = 'Standard_reg_param.pkl'

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

# Flight data    
df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]

# Before Flight 45 min
start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
start_date = start_date - datetime.timedelta(minutes = 50)
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = stop_date - datetime.timedelta(minutes = 5)
df_Picarro_before_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_before_subset = df_Picarro.loc[df_Picarro_before_mask]

# After Flight 45 min
start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
start_date = start_date + datetime.timedelta(minutes = 5)
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = stop_date + datetime.timedelta(minutes = 50)
df_Picarro_after_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_after_subset = df_Picarro.loc[df_Picarro_after_mask]

#%% PLot timeseries

fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(nrows = 3, ncols=3, figsize=(15,10))
#plt.subplots_adjust(wspace = .05) 
ax1.scatter(df_Picarro_subset['d18O'], df_Picarro_subset['d18O'])
ax5.scatter(df_Picarro_subset['d18O'], df_Picarro_subset['d18O'])
ax9.scatter(df_Picarro_subset['d18O'], df_Picarro_subset['d18O'])