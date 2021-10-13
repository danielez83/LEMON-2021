#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 10:00:00 2021

@author:        Daniele Zannoni

Description:    compare H2O observations from iMet and Picarro to estimate
                calibration parameters for humidity. 
                
Notes:          
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
from scipy.stats import linregress

#%% Import iMet data
file2read = nc.Dataset('../iMet/44508/iMet-XQ2-44508_20210920.nc')
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

df_iMet = pd.DataFrame(data = {'H2O':H2O_imet}, index = ncdate_pd_imet)
# Resample 
df_iMet = df_iMet['H2O'].resample("1S").mean()
#%% Import PICARRO data
file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210920-DataLog_User (1).nc')
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
df_Picarro = pd.DataFrame(data = {'H2O':H2O}, index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
df_Picarro = df_Picarro['H2O'].resample("1S").mean()

#%% Import Flights table to filter only flight time
df_Flight_table = pd.read_csv('../Excel/Flights_Table.csv')
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

Flights_OI = [9,10]#[4,5,6,7]
for flight in Flights_OI:
    start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == flight]
    stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == flight]
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
seconds_delay = np.arange(0,20)
r_squared = np.zeros(len(seconds_delay))
idx = 0
for delay in seconds_delay:
    # Add a delay to iMet Probe --> That means Picarro is time-lagged to iMet
    X_Picarro = df_Picarro_flights.iloc[delay:].to_numpy()
    Y_iMet = df_iMet_flights.iloc[0:len(df_iMet_flights) - delay].to_numpy()
    # Fit model
    slope, intercept, r_value, p_value, std_err = linregress(X_Picarro,
                                                             Y_iMet)
    r_squared[idx] = r_value**2
    idx+=1
best_delay = np.where(r_squared == np.max(r_squared))[0][0]
print("Second delay is: ", best_delay)

# Fit best model
X_Picarro = df_Picarro_flights.iloc[best_delay:].to_numpy()
Y_iMet = df_iMet_flights.iloc[0:len(df_iMet_flights) - best_delay].to_numpy()
# Fit model
slope, intercept, r_value, p_value, std_err = linregress(X_Picarro,
                                                         Y_iMet)
XVals = np.linspace(df_Picarro_flights.min(), df_Picarro_flights.max(), 100)
YVals = XVals*slope + intercept

# This part is not necessary, 
# #%% Fit a model to estimate picarro vs iMet delay 
# seconds_delay = np.arange(0,20)
# r_squared = np.zeros(len(seconds_delay))
# idx = 0
# for delay in seconds_delay:
#     # Add a delay to PICARRO
#     X_Picarro = df_Picarro_flights.iloc[0:len(df_iMet_flights) - delay].to_numpy()
#     Y_iMet = df_iMet_flights.iloc[delay:].to_numpy()
#     # Fit model
#     slope, intercept, r_value, p_value, std_err = linregress(X_Picarro,
#                                                              Y_iMet)
#     r_squared[idx] = r_value**2
#     idx+=1
# best_delay = np.where(r_squared == np.max(r_squared))[0][0]
# print("Second delay is: ", best_delay)

# # Fit best model
# X_Picarro = df_Picarro_flights.iloc[best_delay:].to_numpy()
# Y_iMet = df_iMet_flights.iloc[0:len(df_iMet_flights) - best_delay].to_numpy()
# # Fit model
# slope, intercept, r_value, p_value, std_err = linregress(X_Picarro,
#                                                          Y_iMet)
# XVals = np.linspace(df_Picarro_flights.min(), df_Picarro_flights.max(), 100)
# YVals = XVals*slope + intercept

#%% Plot iMet vs PICARRO
fig, ax = plt.subplots(figsize=(10,10))
ax.scatter(df_Picarro_flights, df_iMet_flights, 
           s = 32, marker = 'o', facecolors='none', edgecolors='k')
ax.plot(XVals, YVals, 'r--')

ax.set_xlabel('Picarro H$_2$O [ppm]', fontsize=18)
ax.set_ylabel('iMet H$_2$O [ppm]', fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=20)
ax.grid()

ax.text(5000, 17500, "y = %.3f*x%.3f" % (slope, intercept), size=20)
ax.text(5000, 16500, "R$^2$=%.3f" % r_value**2, size=20)
ax.text(5000, 15500, "Delay=%d seconds" % best_delay, size=20)
    
