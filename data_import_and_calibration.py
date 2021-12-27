#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 15:10:16 2021

Import netcdf data of Picarro and iMet and produce 
1 DataFrame for calibrated Picarro readings
1 DataFrame for iMet readings

Output is saved as pkl files in the following format
FLxx_HIDS2254_yy_zz_kk.pkl
FLxx_iMetXQ2_yy_zz_kk.pkl
where
xx is the flight number
yy is the day of month
zz is the starting hour
kk is the ending hour

@author: daniele
"""
%matplotlib qt5

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
#from scipy.stats import linregress

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

#%% Configuration
# iMet
iMet_filename               = '../iMet/44508/iMet-XQ2-44508_20210917.nc'

# Picaro
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210917-DataLog_User.nc'
Calibration_param_filename  = 'Standard_reg_param_STD_corr.pkl'
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

# General
Flight_table_filename       = '../Excel/Flights_Table.csv'
Flight_OI                   =  2#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
#start_date_str              = '2021-09-23 8:05:00'
#stop_date_str               = '2021-09-23 9:45:00'
output_dir                  = '../PKL intermediate data/'

#%% Import PICARRO data
file2read = nc.Dataset(Picarro_filename)
for dim in file2read.dimensions.values():
    print(dim)

var_names = file2read.variables.keys()
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

#%% Store Picarro data as pandas df
df_Picarro = pd.DataFrame()

for j in var_names:
    str_buff="df_Picarro['%s'] = %s" % (j, j)
    exec(str_buff)
    
df_Picarro.index = ncdate_pd_picarro
#df_Picarro = df_Picarro.resample("1S").mean()

#%% Calibrate Picarro data
calibration_paramters = pd.read_pickle(Calibration_param_filename)
DOI = df_Picarro.index[1000].day
tot = calibration_paramters.index.day == DOI
IOI = np.where(tot==True)
IOI = IOI[0][0]

df_Picarro_data_calibrated = df_Picarro.copy()
# Humidity-isotope correction
df_Picarro_data_calibrated['Delta_18_16'] = hum_corr_fun(df_Picarro['H2O'], 
                                                         df_Picarro['Delta_18_16'], 
                                                         18, 17000, 'mean')
df_Picarro_data_calibrated['Delta_D_H'] = hum_corr_fun(df_Picarro['H2O'], 
                                                       df_Picarro['Delta_D_H'], 
                                                       2, 17000, 'mean')
# Isotope calibration
if calibrate_isotopes == 'yes':
    df_Picarro_data_calibrated['Delta_18_16'] = df_Picarro_data_calibrated['Delta_18_16']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
    df_Picarro_data_calibrated['Delta_D_H'] = df_Picarro_data_calibrated['Delta_D_H']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]
else:
    df_Picarro_data_calibrated['Delta_18_16'] = df_Picarro_subset['d18O']
    df_Picarro_data_calibrated['Delta_D_H'] = df_Picarro_subset['Delta_D_H']

# Humidity calibration, using OPTISONDE relationship
if calibrate_humidity == 'yes':
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']*0.957 - 6.431
else:
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']

#%% Import iMet data
file2read = nc.Dataset(iMet_filename)
for dim in file2read.dimensions.values():
    print(dim)

var_names = file2read.variables.keys()
for var in file2read.variables:
#    print(var)
    str_buff = var+" = file2read['"+var+"'][:]"
    exec(str_buff)
file2read.close()
# Convert NetCDF dates into a datetime vector
ncdate_imet = nc.num2date(time, 'days since 1970-01-01 00:00:00.0', 
                          only_use_cftime_datetimes = False, 
                          only_use_python_datetimes=True)
ncdate_pd_imet = pd.to_datetime(ncdate_imet)

#%% Store iMet data as pandas df
df_iMet = pd.DataFrame()

for j in var_names:
    str_buff="df_iMet['%s'] = %s" % (j, j)
    exec(str_buff)
    
df_iMet.index = ncdate_pd_imet
#df_Picarro = df_Picarro.resample("1S").mean()
