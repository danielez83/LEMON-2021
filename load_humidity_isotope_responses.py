#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 14:52:37 2021

@author: Daniele Zannoni
Some modification of stringdoc
"""
#%% Import section
import pandas as pd
import numpy as np
import netCDF4 as nc
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from FARLAB_standards import standard

#%% Configuration
d18O_standard   = standard('GLW', 'd18O')
dD_standard     = standard('GLW', 'dD')

filename_to_save = "GLW_20210919_extended_2.pkl"

# --------------- BERMUDA 19 Sept
date_start      = datetime.datetime(year=2021,month=9,day=19,hour=10,minute=20)
date_stop       = datetime.datetime(year=2021,month=9,day=19,hour=13,minute=37)
# --------------- GLW 19 Sept
#date_start      = datetime.datetime(year=2021,month=9,day=19,hour=14,minute=10)
#date_stop       = datetime.datetime(year=2021,month=9,day=19,hour=16,minute=5)
# --------------- GLW 20 Sept
#date_start      = datetime.datetime(year=2021,month=9,day=20,hour=12,minute=16)
#date_stop       = datetime.datetime(year=2021,month=9,day=20,hour=14,minute=45)
# --------------- FINSE 21 Sept
#date_start      = datetime.datetime(year=2021,month=9,day=21,hour=9,minute=17)
#date_stop       = datetime.datetime(year=2021,month=9,day=21,hour=13,minute=31)
#%% Import NetCDF data
# Ok for BERMUDA and GLW 19.09.2021
file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210919-DataLog_User.nc')
# Ok for GLW 20.09.2021
#file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210920-DataLog_User (1).nc')
# Ok for FINSE
#file2read = nc.Dataset('../Picarro_HIDS2254/2021/09/HIDS2254-20210921-DataLog_User.nc')
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
     'dD': Delta_D_H,
     'baseline_shift': baseline_shift,
     'residuals': residuals,
     'slope_shift': slope_shift}
Picarro_data = pd.DataFrame(data = d)
Picarro_data.index = Picarro_data['Time']
Picarro_data = Picarro_data.drop(columns = 'Time')

#%% Subset data by dates for standard of interest
good_indexes    = [Picarro_data.index > date_start, Picarro_data.index < date_stop] # Select by dates
good_indexes    = good_indexes[0] & good_indexes[1]                                 # Make an array of logicals

Picarro_data_subset = Picarro_data[good_indexes]
#%% Clean data
# BER 19.09.2021
bad_date_start = datetime.datetime(year=2021,month=9,day=19,hour=12,minute=10)
bad_date_stop = datetime.datetime(year=2021,month=9,day=19,hour=12,minute=16)
bad_indexes = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes = bad_indexes[0] & bad_indexes[1]
Picarro_data_subset.d18O[bad_indexes] = np.nan
Picarro_data_subset.dD[bad_indexes] = np.nan
# ------------------------------------------------------------
# GLW 19.09.2021: remove spike between 14:52 - 14:55 -------
bad_date_start = datetime.datetime(year=2021,month=9,day=19,hour=14,minute=52)
bad_date_stop = datetime.datetime(year=2021,month=9,day=19,hour=14,minute=55)
bad_indexes = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes = bad_indexes[0] & bad_indexes[1]
Picarro_data_subset.d18O[bad_indexes] = np.nan
Picarro_data_subset.dD[bad_indexes] = np.nan
# ------------------------------------------------------------
# GLW 20.09.2021: remove spike between 14:15 - 14:20 -------
bad_date_start = datetime.datetime(year=2021,month=9,day=20,hour=14,minute=15)
bad_date_stop = datetime.datetime(year=2021,month=9,day=20,hour=14,minute=21)
bad_indexes = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes = bad_indexes[0] & bad_indexes[1]
Picarro_data_subset.H2O[bad_indexes] = np.nan
Picarro_data_subset.d18O[bad_indexes] = np.nan
Picarro_data_subset.dD[bad_indexes] = np.nan
# ------------------------------------------------------------
# ------------------------------------------------------------
# FINSE 21.09.2021: remove spikes
bad_date_start = datetime.datetime(year=2021,month=9,day=21,hour=10,minute=14)
bad_date_stop = datetime.datetime(year=2021,month=9,day=21,hour=10,minute=19)
bad_indexes1 = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes1 = bad_indexes1[0] & bad_indexes1[1]

bad_date_start = datetime.datetime(year=2021,month=9,day=21,hour=10,minute=46)
bad_date_stop = datetime.datetime(year=2021,month=9,day=21,hour=10,minute=49)
bad_indexes2 = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes2 = bad_indexes2[0] & bad_indexes2[1]

bad_date_start = datetime.datetime(year=2021,month=9,day=21,hour=11,minute=35)
bad_date_stop = datetime.datetime(year=2021,month=9,day=21,hour=11,minute=45)
bad_indexes3 = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes3 = bad_indexes3[0] & bad_indexes3[1]

bad_date_start = datetime.datetime(year=2021,month=9,day=21,hour=12,minute=50)
bad_date_stop = datetime.datetime(year=2021,month=9,day=21,hour=12,minute=58)
bad_indexes4 = [Picarro_data_subset.index > bad_date_start, Picarro_data_subset.index < bad_date_stop] # Select by dates
bad_indexes4 = bad_indexes4[0] & bad_indexes4[1]

bad_indexes = bad_indexes1 | bad_indexes2 | bad_indexes3 | bad_indexes4

Picarro_data_subset.H2O[bad_indexes] = np.nan
Picarro_data_subset.d18O[bad_indexes] = np.nan
Picarro_data_subset.dD[bad_indexes] = np.nan
# ------------------------------------------------------------
#%% Plot H2O timeseries
fig, ax = plt.subplots(nrows = 3, figsize = (10, 8))
# date_format = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
date_format = mdates.DateFormatter("%H:%M:%S")
ax[0].plot(Picarro_data_subset.index, Picarro_data_subset.H2O)
ax[0].xaxis.set_major_formatter(date_format)
ax[0].set(ylabel = 'H$_{2}$O [ppm]')
ax[0].grid()

ax[1].plot(Picarro_data_subset.index, Picarro_data_subset.d18O)
ax[1].xaxis.set_major_formatter(date_format)
ax[1].set(ylabel = '$\delta^{18}$O [‰]')
ax[1].grid()

ax[2].plot(Picarro_data_subset.index, Picarro_data_subset.dD)
ax[2].xaxis.set_major_formatter(date_format)
ax[2].set(ylabel = '$\delta$D [‰]')
ax[2].grid()



#%% Bin data based on H2O levels
#levels          = np.histogram_bin_edges(Picarro_data_subset['H2O'], bins = 20)
# levels          = np.histogram_bin_edges(Picarro_data_subset['H2O'])
levels = np.histogram_bin_edges(Picarro_data_subset.H2O[~np.isnan(Picarro_data_subset.H2O)])
level_window    = 300

# Preallocate memory for level values
H2O_level   = np.zeros((len(levels), 1))
d18O_means  = np.zeros((len(levels), 1))
d18O_stds   = np.zeros((len(levels), 1))
dD_means    = np.zeros((len(levels), 1))
dD_stds     = np.zeros((len(levels), 1))
# Extra
residuals_means         = np.zeros((len(levels), 1)) 
slope_shift_means       = np.zeros((len(levels), 1))
baseline_shift_means    = np.zeros((len(levels), 1))
idx = 0

for level in levels[:]:
    good_indexes    = [Picarro_data_subset['H2O'] > (level - level_window), Picarro_data_subset['H2O'] < (level + level_window)]
    good_indexes    = good_indexes[0] & good_indexes[1] # Make an array of logicals
    # ---
    H2O_level[idx]  = Picarro_data_subset.H2O[good_indexes].mean(skipna=True)
    d18O_means[idx] = Picarro_data_subset.d18O[good_indexes].mean(skipna=True)
    dD_means[idx]   = Picarro_data_subset.dD[good_indexes].mean(skipna=True)
    # ---
    d18O_stds[idx] = Picarro_data_subset.d18O[good_indexes].std(skipna=True)
    dD_stds[idx]   = Picarro_data_subset.dD[good_indexes].std(skipna=True)
    # ---
    residuals_means[idx]         = Picarro_data_subset.residuals[good_indexes].std(skipna=True)
    slope_shift_means[idx]       = Picarro_data_subset.slope_shift[good_indexes].std(skipna=True)
    baseline_shift_means[idx]    = Picarro_data_subset.baseline_shift[good_indexes].std(skipna=True)
    
    idx+=1
# Prepare numpy array
d = np.concatenate((H2O_level, d18O_means, d18O_stds, dD_means, dD_stds, 
                    residuals_means, slope_shift_means, baseline_shift_means), axis = 1)

#%% Save DataFrame
my_data_frame = pd.DataFrame(d, columns = ['H2O', 'd18O_mean', 'd18O_err', 'dD_mean', 'dD_err', 
                                           'residuals', 'slope_shift', 'baseline_shift'])
my_data_frame.dropna(inplace = True)
my_data_frame.to_pickle(filename_to_save)
#%% Plot curves
fig, ax = plt.subplots(nrows = 2, figsize = [15,10])
ax[0].scatter(my_data_frame['H2O'], my_data_frame['d18O_mean'] - d18O_standard,
              s = 64, marker = 'o')
ax[0].set(ylabel = '$\delta^{18}$O meas-std [‰]')
ax[0].grid()

ax[1].scatter(my_data_frame['H2O'], my_data_frame['dD_mean'] - dD_standard,
              s = 64, marker = 'o')
ax[1].set(ylabel = '$\delta$D meas-std [‰]')
ax[1].grid()