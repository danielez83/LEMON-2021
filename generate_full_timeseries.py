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

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

from filter_picarro_data import filter_picarro_data
from filter_picarro_data import delay_picarro_data

#%% Configuration
# Input files ----------------------------------------------------------------
iMet_filename                   = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename                = '../Picarro_HIDS2254/2021/09/HIDS2254-20210918-DataLog_User.nc'
Calibration_param_filename      = 'Standard_reg_param_STD_corr.pkl'

# Output files ----------------------------------------------------------------
pkl_output_filename             = '../PKL final data/flight_04.pkl'
save_pkl                        = True
csv_output_filename             = '../CSV final data/flight_04.csv'
save_csv                        = True

# Other Settings
calibrate_isotopes              = False
calibrate_humidity              = False
filter_data                     = True
check_humidity                  = False
display_plots                   = True
start_date_str                  = '2021-09-18 05:13:00'
stop_date_str                   = '2021-09-18 06:06:00'
variables_to_include_iMet       = ['LAT', 'LON', 'ALT',
                                   'TA', 'TD', 'UU', 'P']
variables_to_include_Picarro    = ['H2O', 'd18O', 'dD'] # Picarro time will be included as the index

#%% Metadata
metadata = {"Flight ID"     : "F4",
            "Other info"    : "Test"}

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

#%% Same iMet data as dataframe
df_iMet = pd.DataFrame(data = {'ALT':ALT,
                               'LAT':LAT,
                               'LON': LON,
                               'TA':TA,
                               'TD': TD,
                               'UU':UU,
                               'P':P}, index = ncdate_pd_imet)

#%% Resample and center at 1 sec freq
df_iMet = df_iMet.resample("1S").mean()
# Notes
print("There is a ", np.nanmean(df_iMet['P'] - df_Picarro_data_calibrated['AmbientPressure']), "hPa difference between Picarro and iMet")

#%% Check humidity ?
if check_humidity:
    ew = lambda t: 6.112*np.exp(17.62*(t/(243.12 + t)))
    Pw = (df_iMet['UU']/100)*ew(df_iMet['TA']) # hPa
    H2O_imet = 1e6 * Pw/(df_iMet['P']-Pw)
    
    fig, ax = plt.subplots(dpi = 300)
    ax.plot(H2O_imet.index, H2O_imet)
    ax.plot(df_Picarro_data_calibrated.index, df_Picarro_data_calibrated['H2O'] + 514.3309326171875)

#%% Subset dataframes
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

df_Picarro_subset   = df_Picarro[(df_Picarro.index >= start_date) & (df_Picarro.index <= stop_date)]
df_iMet_subset      = df_iMet[(df_iMet.index >= start_date) & (df_iMet.index <= stop_date)]

#%% Create new dataframe
flight_data = pd.DataFrame()

for var in variables_to_include_iMet:
    str_buff = "flight_data['"+var+"'] = "+"df_iMet_subset['"+var+"']"
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
    