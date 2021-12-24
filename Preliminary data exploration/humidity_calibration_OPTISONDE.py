#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 21:33:40 2021

@author:        Daniele Zannoni

Description:    compare H2O observations from Optisonde and Picarro to estimate
                calibration parameters for humidity. 
                Measurements performed on 21/09/2021 between 9:18 and 13:30 (UTC)
Notes:          Optisonde = 0.957*Picarro - 6.431 (R^2=0.999)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
from scipy.stats import linregress

#%% Import OPTISONDE data
filename = '../Picarro_HIDS2254/OPTISONDE_readings.txt'
OPTISONDE = pd.read_csv(filename, delimiter=',')
OPTISONDE.index = pd.to_datetime(OPTISONDE['Time'], 
                                 format= '%d/%m/%Y %H:%M')
OPTISONDE.drop(columns=['Time'], inplace = True)

#%% Import PICARRO data
file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210921-DataLog_User.nc')
for dim in file2read.dimensions.values():
    print(dim)

for var in file2read.variables:
#    print(var)
    str_buff = var+" = file2read['"+var+"'][:]"
    exec(str_buff)
file2read.close()
#%% Convert NetCDF dates into a datetime vector
ncdate = nc.num2date(time, 'days since 1970-01-01 00:00:00.0', 
                     only_use_cftime_datetimes = False, 
                     only_use_python_datetimes=True)
ncdate_pd = pd.to_datetime(ncdate)

#%% Sample Picarro H2O observation based on dates of OPTISONDE
# Create a new dataframe based on OPTISONDE
PICARRO = OPTISONDE.copy()
PICARRO.drop(columns=[' Td'], inplace = True)

averaging_window = 30*4 # ~30 seconds per side --> 1 minute averaging window
for date in OPTISONDE.index:
    val_to_check = np.min(np.abs(ncdate_pd - date))
    idx = np.where(np.abs(ncdate_pd - date) == val_to_check)
    idx = idx[0][0]
    PICARRO[' H2O'][date] = np.mean(H2O[idx-averaging_window:idx+averaging_window])

#%% Fit a model to estimate PICARRO's calibration parameters
slope, intercept, r_value, p_value, std_err = linregress(PICARRO[' H2O'],
                                                         OPTISONDE[' H2O'])
XVals = np.linspace(PICARRO[' H2O'].min(), PICARRO[' H2O'].max(), 100)
YVals = XVals*slope + intercept

#%% Plot OPTISONDE vs PICARRO and model
fig, ax = plt.subplots(figsize=(10,10))
ax.scatter(PICARRO[' H2O'], OPTISONDE[' H2O'], 
           s = 256, marker = 'o', facecolors='none', edgecolors='k')
ax.plot(XVals, YVals, 'r--')

ax.set_xlabel('Picarro H$_2$O [ppm]', fontsize=18)
ax.set_ylabel('Optisonde H$_2$O [ppm]', fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=20)
ax.grid()

ax.text(5000, 17500, "y = %.3f*x%.3f" % (slope, intercept), size=20)
ax.text(5000, 16500, "R$^2$=%.3f" % r_value**2, size=20)

