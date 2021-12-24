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
iMet_filename               = '../iMet/44508/iMet-XQ2-44508_20210923.nc'
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210923-DataLog_User.nc'
Flight_table_filename       = '../Excel/Flights_Table.csv'
Flight_OI                   =  16#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
Calibration_param_filename  = 'Standard_reg_param_STD_corr.pkl'
display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'auto' #'auto', 'manual'
bins                        = np.arange(400, 20000, 400)
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

start_date_str                   = '2021-09-23 9:15:00'
stop_date_str                    = '2021-09-23 9:45:00'

#%% Pressure to alitude conversion
# https://www.weather.gov/epz/wxcalc_pressurealtitude
Torr2feet = lambda p:(1-((p*1.33322)/1013.25)**(0.190284))*145366.45
Torr2meters = lambda p: ((1-((p*1.33322)/1013.25)**(0.190284))*145366.45)*0.3048

#%% Import iMet data
file2read = nc.Dataset(iMet_filename)
for dim in file2read.dimensions.values():
    print(dim)

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

#%% Calculate ppm from RH,T, P and save iMet data as pandas df
# https://www.eas.ualberta.ca/jdwilson/EAS372_13/Vomel_CIRES_satvpformulae.html
# Guide to Meteorological Instruments and Methods of Observation (CIMO Guide) (WMO, 2008)
# ew = 6.112 e(17.62 t/(243.12 + t))
# https://www.hatchability.com/Vaisala.pdf
# eq. 18
ew = lambda t: 6.112*np.exp(17.62*(t/(243.12 + t)))
Pw = (UU/100)*ew(TA) # hPa
H2O_imet = 1e6 * Pw/(P-Pw)

df_iMet = pd.DataFrame(data = {'H2O':H2O_imet,
                               'altitude':ALT,
                               'latitude':LAT,
                               'longitude':LON}, index = ncdate_pd_imet)
# Resample 
df_iMet = df_iMet.resample("1S").mean()

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

# start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]  # works with flight table
# stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]  # works with flight table
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S') # works with region of interest
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S') # works with region of interest
if Flight_OI == 1:
    start_date = start_date + datetime.timedelta(minutes = 5)
    #stop_date = stop_date - datetime.timedelta(minutes = 5)   
# Adjust time for comparison. It is flight dependent
if Flight_OI == 7:
    start_date = start_date + datetime.timedelta(minutes = 5)
    stop_date = stop_date - datetime.timedelta(minutes = 5)   
    

#df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0]) # works with flight table
df_Picarro_mask = (df_Picarro.index > start_date) & (df_Picarro.index < stop_date) # works with region of interest
df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]
# df_iMet_mask = (df_iMet.index > start_date.iloc[0]) & (df_iMet.index < stop_date.iloc[0])# works with flight table
df_iMet_mask = (df_iMet.index > start_date) & (df_iMet.index < stop_date) # works with region of interest
df_iMet_subset = df_iMet.loc[df_iMet_mask]

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

#%% 


fig, ax = plt.subplots(figsize = [10,10], dpi = 150)
ax.scatter(df_iMet_subset['longitude'], df_iMet_subset['latitude'], c = Picarro_data_calibrated['dD'], cmap = 'jet')
ax.set_ylim([44.53, 44.56])
ax.set_xlim([4.32, 4.40])
plt.savefig('demo.png', transparent=True)

plt.scatter(df_iMet_subset['longitude'], df_iMet_subset['latitude'], c = Picarro_data_calibrated['dD'], cmap = 'jet')
plt.colorbar(orientation = 'horizontal')
