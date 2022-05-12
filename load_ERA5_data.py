#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  9 11:15:51 2022

@author: daniele
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
from scipy import constants


#%% Configuration
#ERA5_filename               = '../ERA5 data/Sept2021_BLH_values.nc'
ERA5_filename               = '../ERA5 data/Sept2021_Surf_values_test.nc'

start_date_str              = '2021-09-18 12:00:00'
stop_date_str               = '2021-09-18 15:00:00'

latOI                       = 44.5393
lonOI                       = 4.3679

#%% Import ERA5 data
file2read = nc.Dataset(ERA5_filename)
for dim in file2read.dimensions.values():
    print(dim)

for var in file2read.variables:
#    print(var)
    str_buff = var+" = file2read['"+var+"'][:]"
    exec(str_buff)
file2read.close()
# Convert NetCDF dates into a datetime vector
ncdate_ERA5 = nc.num2date(time, 'hours since 1900-01-01 00:00:00.0', 
                          only_use_cftime_datetimes = False, 
                          only_use_python_datetimes=True)
ncdate_ERA5 = pd.to_datetime(ncdate_ERA5)

#%% Extract timeseries for point of interest
# netCDF format [time, latitude, longitude]
lat_idx = np.where(abs(latitude - latOI) == min(abs(latitude - latOI)))[0][0]
lon_idx = np.where(abs(longitude - lonOI) == min(abs(longitude - lonOI)))[0][0]
print("For latitude, the distance from point of interest is: %.2f" % (latitude[lat_idx] - latOI))
print("For longitude, the distance from point of interest is: %.2f" % (longitude[lon_idx] - lonOI))
# Distance is ~ 10 km
blh_TS = blh[:, lat_idx, lon_idx]
z_TS = z[:, lat_idx, lon_idx]

#%% Build dataframe for easy handling
ERA5_data = pd.DataFrame(data = {
    'blh':blh_TS,
    'z':z_TS/constants.g},
    index = ncdate_ERA5)

#%% Subset data only to extract diurnal PBLH min and max
# Define time region
start_date_str      = '18-09-2021 00:00:00'
stop_date_str       = '23-09-2021 23:00:00'

# Subset data 
start_winOI = pd.to_datetime(start_date_str, dayfirst = True)
stop_winOI  = pd.to_datetime(stop_date_str, dayfirst = True)
ERA5_date_mask = (ERA5_data.index > start_winOI) & (ERA5_data.index < stop_winOI)

#%% Plot data
fig, ax = plt.subplots(figsize=(10,10))
ax.plot(ERA5_data.index[ERA5_date_mask], ERA5_data['blh'][ERA5_date_mask] + ERA5_data['z'][0])

#%% Calculate day by day max PBLH
for day in range(18, 24):
    start_date_str      = '%d-09-2021 10:00:00' % day
    stop_date_str       = '%d-09-2021 18:00:00' % day
    start_winOI = pd.to_datetime(start_date_str, dayfirst = True)
    stop_winOI  = pd.to_datetime(stop_date_str, dayfirst = True)
    ERA5_date_mask = (ERA5_data.index > start_winOI) & (ERA5_data.index < stop_winOI)
    print(ERA5_data['blh'][ERA5_date_mask].max() + ERA5_data['z'][0]) # Add height to gound elevation (from geopotential)
