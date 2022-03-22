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

import pickle

import gpxpy
import gpxpy.gpx

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

from filter_picarro_data import filter_picarro_data
from filter_picarro_data import delay_picarro_data

#%% Configuration
# Input files ----------------------------------------------------------------
gpx_filename                    = '../AirNav Data/2021-9-17_14_28.gpx'
Picarro_filename                = '../Picarro_HIDS2254/2021/09/HIDS2254-20210917-DataLog_User.nc'
Calibration_param_filename      = 'Standard_reg_param_STD_corr.pkl'

# Output files ----------------------------------------------------------------
pkl_output_filename             = '../PKL final data/flight_03_nofilt.pkl'
save_pkl                        = False
csv_output_filename             = '../CSV final data/flight_03.csv'
save_csv                        = False

# Date - time of interest
start_date_str                  = '2021-09-17 15:28:00'
stop_date_str                   = '2021-09-17 16:45:00'

# Other Settings
calibrate_isotopes              = True
calibrate_humidity              = True
filter_data                     = False

display_plots                   = True

variables_to_include_Picarro    = ['H2O', 'd18O', 'dD'] # Picarro time will be included as the index
variables_to_include_AirNav     = ['LAT', 'LON', 'ALT']
#%% Metadata
metadata = {"Flight ID"     : 3}#,
            #"Other info"    : "Test"}

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
                                  'AmbientPressure':AmbientPressure*1.3332236842,   #Converted to hPa
                                  'CavityPressure': CavityPressure,
                                  'CavityTemp':CavityTemp,
                                  'DasTemp':DasTemp,
                                  'WarmBoxTemp':WarmBoxTemp,
                                  'ValveMask':ValveMask}, index = ncdate_pd_picarro)

if ncdate_pd_picarro[0].day == 22:
    df_Picarro = df_Picarro.drop(df_Picarro.index[0:1000])    
    df_Picarro = df_Picarro.drop(df_Picarro.index[-1000])

#%% Filter data
if filter_data:
    df_Picarro['H2O'] = filter_picarro_data(df_Picarro['H2O'], df_Picarro.index, 'H2O')
    df_Picarro['d18O'] = filter_picarro_data(df_Picarro['d18O'], df_Picarro.index, 'd18O')
    df_Picarro['dD'] = filter_picarro_data(df_Picarro['dD'], df_Picarro.index, 'dD')

#%% Resample and center at 1 sec freq
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
if calibrate_isotopes:
    df_Picarro_data_calibrated['d18O'] = df_Picarro_data_calibrated['d18O']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
    df_Picarro_data_calibrated['dD'] = df_Picarro_data_calibrated['dD']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]
else:
    df_Picarro_data_calibrated['d18O'] = df_Picarro_data_calibrated['d18O']
    df_Picarro_data_calibrated['dD'] = df_Picarro_data_calibrated['dD']

# Humidity calibration, using OPTISONDE relationship
if calibrate_humidity:
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']*0.957 - 6.431
else:
    df_Picarro_data_calibrated['H2O'] = df_Picarro_data_calibrated['H2O']

#%% Import AirNav data
gpx_file = open(gpx_filename, 'r')

gpx = gpxpy.parse(gpx_file)

def get_timestamp(pointOI):
    for extension in pointOI.extensions:
        if extension.tag == 'timestamp':
            return extension.text
ALT = []
LAT = []
LON = []
airnav_timestamp = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            ALT.append(point.geoid_height)
            LAT.append(point.latitude)
            LON.append(point.longitude)
            timestamp = get_timestamp(point)
            ts = datetime.datetime.fromtimestamp(float(timestamp))
            airnav_timestamp.append(ts)
            #print(f'Point at ({timestamp}, {point.latitude},{point.longitude}), {point.geoid_height}')
            
#%% Same AirNav data as dataframe
df_AirNav = pd.DataFrame(data = {'ALT':ALT,
                                 'LAT':LAT,
                                 'LON': LON}, index = airnav_timestamp)
# Convert Daylight Saving time to UTC 
df_AirNav.index = df_AirNav.index - datetime.timedelta(hours = 2)

#%% Resample and center at 1 sec freq
df_AirNav = df_AirNav.resample("1S").mean()
# Interpolate Nans
df_AirNav = df_AirNav.interpolate()

#%% Subset dataframes
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

df_Picarro_subset = df_Picarro_data_calibrated[(df_Picarro_data_calibrated.index >= start_date) & (df_Picarro_data_calibrated.index <= stop_date)]
df_AirNav_subset  = df_AirNav[(df_AirNav.index >= start_date) & (df_AirNav.index <= stop_date)]

#%% Create new dataframe
flight_data = pd.DataFrame()

for var in variables_to_include_AirNav:
    str_buff = "flight_data['"+var+"'] = "+"df_AirNav_subset['"+var+"']"
    exec(str_buff)
    
for var in variables_to_include_Picarro:
    str_buff = "flight_data['"+var+"'] = "+"df_Picarro_subset['"+var+"']"
    exec(str_buff)
# Add d-excess
flight_data['dexcess'] = flight_data['dD'] - 8*flight_data['d18O']
# Add index
flight_data.index = df_Picarro_subset.index

#%% Plot
if display_plots:
    fig, ax = plt.subplots(nrows=len(flight_data.columns), sharex=True)
    for var,ax_num in zip(flight_data.columns, range(len(flight_data.columns))):
        ax[ax_num].plot(flight_data.index, flight_data[var])
        ax[ax_num].set_ylabel(var)
        ax[ax_num].grid()
        
    plt.tight_layout
#%% Save PKL
if save_pkl:
    with open(pkl_output_filename, 'wb') as f:
        pickle.dump([flight_data, metadata], f)
    print('Flight data saved into ' + pkl_output_filename)    
#%% Save CSV
if save_csv:
    flight_data.to_csv(csv_output_filename)
    print('Flight data saved into ' + csv_output_filename)
    