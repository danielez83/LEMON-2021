#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 10:39:39 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc

from calibrate_picarro_data import calibrate_picarro_data

# Time references indentified


#Fligh 11 Engine ON, Acc_time = 2021-09-20 15:59:23.500000, Picarro_time = 2021-09-20 15:59:20.500000
#Fligh 11 Engine OFF, Acc_time = 2021-09-20 17:47:27.500000, Picarro_time = 2021-09-20 17:47:24.00000

#%% Configuration
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210920-DataLog_User (1).nc'
acc_filename                = '../Accelerometer/2021-09-2008.38.09.csv'
ref_date_for_acc            = '2021-09-20'

resample_T                  = 0.5 # seconds, 2Hz is ok for comparison

start_date_str              = '2021-09-20 6:35:00'
stop_date_str               = '2021-09-20 6:41:00'

#%% Import Netcf as df 
# Import NETCDF --------------------------------------------------------------
file2read = nc.Dataset(Picarro_filename)
for dim in file2read.dimensions.values():
    print(dim)
    
my_vars = file2read.variables

for var in my_vars:
#    print(var)
    str_buff = var+" = file2read['"+var+"'][:]"
    exec(str_buff)

# Convert NetCDF dates into a datetime vector
ncdate_picarro = nc.num2date(time, 'days since 1970-01-01 00:00:00.0', 
                             only_use_cftime_datetimes = False, 
                             only_use_python_datetimes=True)
ncdate_pd_picarro = pd.to_datetime(ncdate_picarro)

# Save Picarro data as pandas df ---------------------------------------------
df_Picarro = pd.DataFrame(data = {'H2O':H2O,
                                  'd18O':Delta_18_16,
                                  'dD': Delta_D_H,
                                  'AmbientPressure':AmbientPressure,
                                  'CavityPressure': CavityPressure,
                                  'CavityTemp':CavityTemp,
                                  'DasTemp':DasTemp,
                                  'WarmBoxTemp':WarmBoxTemp,
                                  'ValveMask':ValveMask}, index = ncdate_pd_picarro)
# Remove unwanted variables --------------------------------------------------
for var in my_vars.keys():
    str_buff = ('del ' + var)
    exec(str_buff)
    #if not name.startswith('_'):
    #del globals()[var]      
file2read.close()    
del dim, ncdate_pd_picarro, ncdate_picarro

#%% Calibrate picarro data and resample
df_Picarro_calib = calibrate_picarro_data(df_Picarro_raw = df_Picarro, 
                       Calibration_param_filename = 'Standard_reg_param_STD_corr.pkl', 
                       calibrate_isotopes = 'yes', 
                       calibrate_humidity = 'yes', 
                       ref_val_humidity = 17000)



#%% Load accelerometer data and adjust datetime
df_acc_data = pd.read_csv(acc_filename)
time = pd.to_datetime(df_acc_data['time'], format = '%H:%M:%S:%f')
time_ref = pd.to_datetime(datetime.datetime.strptime(ref_date_for_acc, '%Y-%m-%d'))
acc_ref_date = pd.to_datetime(time[0].date())
delta_days = time_ref - acc_ref_date
df_acc_data.index = time  + delta_days
df_acc_data.index = df_acc_data.index  + datetime.timedelta(hours = -2)
#df_acc_data.drop('time', axis = 1, inplace = True)

#%% Resample data
if resample_T < 1:
    buff_txt = "%.1fS" % resample_T         # 1 digit resolution
else:
    buff_txt = "%dS" % resample_T           # floor to decimal
    
df_Picarro_calib = df_Picarro_calib.resample(buff_txt).mean()
df_acc_data = df_acc_data.resample(buff_txt).mean()

#%% Plot time series of specified intervals
start_date_str              = '2021-09-20 8:27:00'
stop_date_str               = '2021-09-20 8:27:30'


start_date = pd.to_datetime(datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S'))
stop_date = pd.to_datetime(datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S'))

fig, ax = plt.subplots(nrows = 2, figsize = (15,10))

# Plot cavity pressuire
df_Picarro_calib['CavityPressure'][(df_Picarro_calib.index > start_date) & (df_Picarro_calib.index < stop_date)].plot(ax = ax[0])
ax[0].grid(which = 'both')
ax[0].set_ylabel('Cavity Pressure (Torr)')

#df_acc_data['aT (m/s^2)'][(df_acc_data.index > start_date) & (df_acc_data.index < stop_date)].plot(ax = ax[1])
df_acc_data['aT (m/s^2)'][(df_acc_data.index > start_date) & (df_acc_data.index < stop_date)].plot(ax = ax[1])
ax[1].grid(which = 'both')
ax[1].set_ylabel('aT (m/s^2)')
ax[1].set_xlim(ax[0].get_xlim())

