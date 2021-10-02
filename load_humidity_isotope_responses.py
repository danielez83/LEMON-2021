#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:52:37 2021

@author: daniele
"""
#%% Import section
import pandas as pd
import numpy as np
import netCDF4 as nc
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#%% Import NetCDF data
file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210919-DataLog_User.nc')
#print(file2read)
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

#%% Make a pandas dataframe 
d = {'Time': ncdate,
     'H2O': H2O,
     'd18O': Delta_18_16,
     'dD': Delta_D_H}
Picarro_data = pd.DataFrame(data = d)
Picarro_data.index = Picarro_data['Time']
Picarro_data = Picarro_data.drop(columns = 'Time')

#%% Subset data by dates BERMUDA
date_start      = datetime.datetime(year=2021,month=9,day=19,hour=10,minute=20)
date_stop       = datetime.datetime(year=2021,month=9,day=19,hour=13,minute=37)
good_indexes    = [Picarro_data.index > date_start, Picarro_data.index < date_stop] # Select by dates
good_indexes    = good_indexes[0] & good_indexes[1]                                 # Make an array of logicals

Picarro_data_subset = Picarro_data[good_indexes]
#%% Plot H2O timeseries
fig, ax = plt.subplots(nrows = 3, figsize = (10, 8))
# date_format = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
date_format = mdates.DateFormatter("%H:%M:%S")
ax[0].plot(Picarro_data.index[good_indexes], Picarro_data.H2O[good_indexes])
ax[0].xaxis.set_major_formatter(date_format)
ax[0].set(ylabel = 'H$_{2}$O [ppm]')
ax[0].grid()

ax[1].plot(Picarro_data.index[good_indexes], Picarro_data.d18O[good_indexes])
ax[1].xaxis.set_major_formatter(date_format)
ax[1].set(ylabel = '$\delta^{18}$O [‰]')
ax[1].grid()

ax[2].plot(Picarro_data.index[good_indexes], Picarro_data.dD[good_indexes])
ax[2].xaxis.set_major_formatter(date_format)
ax[2].set(ylabel = '$\delta$D [‰]')
ax[2].grid()



#%% Bin data based on H2O levels
levels          = np.histogram_bin_edges(Picarro_data_subset['H2O'], bins = 20)
level_window    = 300

# Preallocate memory for level values
H2O_level   = np.zeros((len(levels)-1, 1))
d18O_means  = np.zeros((len(levels)-1, 1))
d18O_stds   = np.zeros((len(levels)-1, 1))
dD_means    = np.zeros((len(levels)-1, 1))
dD_stds     = np.zeros((len(levels)-1, 1))
idx = 0

for level in levels[1:]:
    good_indexes    = [Picarro_data_subset['H2O'] > (level - level_window), Picarro_data_subset['H2O'] < (level + level_window)]
    good_indexes    = good_indexes[0] & good_indexes[1] # Make an array of logicals
    # ---
    H2O_level[idx]  = Picarro_data_subset.H2O[good_indexes].mean()
    d18O_means[idx] = Picarro_data_subset.d18O[good_indexes].mean()
    dD_means[idx]   = Picarro_data_subset.dD[good_indexes].mean()
    # ---
    d18O_stds[idx] = Picarro_data_subset.d18O[good_indexes].std()
    dD_stds[idx]   = Picarro_data_subset.dD[good_indexes].std()
    # ---
    idx+=1
# Save as DataFrame
d = {'H2O':         H2O_level,
     'd18O':        d18O_means,
     'd18O_err':    d18O_stds,
     'dD':          dD_means,
     'dD_err':      dD_stds}
BER20210919 = pd.DataFrame(data = d)