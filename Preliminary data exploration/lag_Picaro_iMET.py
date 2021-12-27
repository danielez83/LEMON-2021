#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:00:00 2021

@author:        Daniele Zannoni

Description:    compare H2O observations from iMet and Picarro to estimate
                1) calibration parameters for humidity
                2) delay between iMet and Picarro
                
Notes:          calibration
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
from scipy.stats import linregress

#%% Configuration
iMet_filename           = '../../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename        = '../../Picarro_HIDS2254/2021/09/HIDS2254-20210918-DataLog_User.nc'
Flight_table_filename   = '../../Excel/Flights_Table.csv'
Flights_OI =  [4] #[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]

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

df_iMet = pd.DataFrame(data = {'H2O':H2O_imet, 'P':P}, index = ncdate_pd_imet)
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

# Save data as pandas df
df_Picarro = pd.DataFrame(data = {'H2O':H2O, 'P':AmbientPressure*1.3332236842}, 
                          index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
df_Picarro = df_Picarro.resample("1S").mean()

#%% Import Flights table to filter only flight time
df_Flight_table = pd.read_csv(Flight_table_filename)
df_Flight_table['Takeoff_fulldate'] = pd.to_datetime(df_Flight_table['Takeoff_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')
df_Flight_table['Landing_fulldate'] = pd.to_datetime(df_Flight_table['Landing_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')

#%% Find best time delay between instrument by moving correlation
# Extract column names into a list
df_Picarro_flights = df_Picarro.copy()
df_Picarro_flights.drop(df_Picarro_flights.index, inplace=True)
df_iMet_flights = df_iMet.copy()
df_iMet_flights.drop(df_iMet_flights.index, inplace=True)


for flight in Flights_OI:
    start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == flight]
    stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == flight]
    if flight == 1:
        start_date = start_date + datetime.timedelta(minutes = 5)
        #stop_date = stop_date - datetime.timedelta(minutes = 5)   
    # Adjust time for comparison. It is flight dependent
    if flight == 7:
        start_date = start_date + datetime.timedelta(minutes = 5)
        stop_date = stop_date - datetime.timedelta(minutes = 5)     
        
    df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
    df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]
    df_iMet_mask = (df_iMet.index > start_date.iloc[0]) & (df_iMet.index < stop_date.iloc[0])
    df_iMet_subset = df_iMet.loc[df_iMet_mask]
    # Concatenate Data Frames
    df_Picarro_flights = df_Picarro_flights.append(df_Picarro_subset)
    df_iMet_flights = df_iMet_flights.append(df_iMet_subset)
    

#%% Fit a model to estimate picarro vs iMet delay
seconds_delay   = np.arange(0, 20)
r_squared_hum   = np.zeros(len(seconds_delay))
r_squared_P     = np.zeros(len(seconds_delay))
idx = 0
for delay in seconds_delay:
    # Add a delay to iMet Probe --> That means Picarro is time-lagged to iMet
    # Humidity
    X_Picarro_hum = df_Picarro_flights.iloc[delay:, 0].to_numpy()
    Y_iMet_hum = df_iMet_flights.iloc[0:len(df_iMet_flights) - delay, 0].to_numpy()
    # Ambient pressure
    X_Picarro_P = df_Picarro_flights.iloc[delay:, 1].to_numpy()
    Y_iMet_P = df_iMet_flights.iloc[0:len(df_iMet_flights) - delay, 1].to_numpy()  
    
    # Remove nans
    X_Picarro_hum = X_Picarro_hum[~np.isnan(Y_iMet_hum)]
    Y_iMet_hum = Y_iMet_hum[~np.isnan(Y_iMet_hum)]
    X_Picarro_P = X_Picarro_P[~np.isnan(Y_iMet_P)]
    Y_iMet_P = Y_iMet_P[~np.isnan(Y_iMet_P)]
    # Fit model
    slope_hum, intercept_hum, r_value_hum, p_value_hum, std_err_hum = linregress(X_Picarro_hum,
                                                             Y_iMet_hum)
    slope_P, intercept_P, r_value_P, p_value_P, std_err_P = linregress(X_Picarro_P,
                                                             Y_iMet_P)
    
    r_squared_hum[idx]  = r_value_hum**2
    r_squared_P[idx]    = r_value_P**2 
    idx+=1
    
best_delay_hum = np.where(r_squared_hum == np.max(r_squared_hum))[0][0]
print("Based on humidity, delay is: ", best_delay_hum, 'seconds')
best_delay_P = np.where(r_squared_P == np.max(r_squared_P))[0][0]
print("Based on pressure, delay is: ", best_delay_P, 'seconds')

#%% Fit best model
X_Picarro = df_Picarro_flights.iloc[best_delay:].to_numpy()
Y_iMet = df_iMet_flights.iloc[0:len(df_iMet_flights) - best_delay].to_numpy()
X_Picarro = X_Picarro[~np.isnan(Y_iMet)]
Y_iMet = Y_iMet[~np.isnan(Y_iMet)]
# Fit model
slope, intercept, r_value, p_value, std_err = linregress(X_Picarro,
                                                         Y_iMet)
XVals = np.linspace(df_Picarro_flights.min(), df_Picarro_flights.max(), 100)
YVals = XVals*slope + intercept


#%% Plot iMet vs PICARRO
fig, ax = plt.subplots(nrows = 2, figsize = (5,10))
ax[0].scatter(df_Picarro_flights, df_iMet_flights, 
           s = 32, marker = 'o', facecolors='none', edgecolors='k')
#ax[0].plot(XVals, YVals, 'r--')

ax[0].set_xlabel('Picarro H$_2$O [ppm]', fontsize=18)
ax[0].set_ylabel('iMet H$_2$O [ppm]', fontsize=18)
ax[0].tick_params(axis='both', which='major', labelsize=20)
ax[0].grid()

ax[1].scatter(df_Picarro_flights['P'], df_iMet_flights['P'], 
           s = 32, marker = 'o', facecolors='none', edgecolors='k')
#ax[1].plot(XVals, YVals, 'r--')

ax[1].set_xlabel('Picarro P [hPa]', fontsize=18)
ax[1].set_ylabel('iMet P [hPa]', fontsize=18)
ax[1].tick_params(axis='both', which='major', labelsize=20)
ax[1].grid()

#ax.text(5000, 17500, "y = %.3f*x+%.3f" % (slope, intercept), size=20)
#ax.text(5000, 16500, "R$^2$=%.3f" % r_value**2, size=20)
#ax.text(5000, 15500, "Delay=%d seconds" % best_delay, size=20)
#ax.text(4000, 13500, "y = %.3f*x+%.3f" % (slope, intercept), size=20)
#ax.text(4000, 13000, "R$^2$=%.3f" % r_value**2, size=20)
#ax.text(4000, 12500, "Delay=%d seconds" % best_delay, size=20)

#%% Plot humidity and pressure time series
fig, ax = plt.subplots(nrows = 2, figsize = (10,5))
ax[0].plot(df_Picarro_flights.index, df_Picarro_flights['H2O']*1.007+85.590, label = 'Picarro')
ax[0].plot(df_iMet_flights.index, df_iMet_flights['H2O'], label = 'iMet XQ2')
ax[0].legend()
ax[0].grid()

ax[1].plot(df_Picarro_flights.index, df_Picarro_flights['P']+20, label = 'Picarro')
ax[1].plot(df_iMet_flights.index, df_iMet_flights['P'], label = 'iMet XQ2')
ax[1].legend()
ax[1].grid()
#%% Plot humidity time series zoom
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(df_Picarro_flights.index - datetime.timedelta(seconds = 12), df_Picarro_flights*1.007+85.590, label = 'Picarro')
ax.plot(df_iMet_flights.index, df_iMet_flights, label = 'iMet XQ2')
ax.legend()
ax.set_xlim([pd.to_datetime('2021-09-18 12:59'), pd.to_datetime('2021-09-18 13:05')])
ax.set_ylim([14000, 17000])
ax.grid()
