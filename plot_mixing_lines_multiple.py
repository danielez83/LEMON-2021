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

from scipy import signal
from scipy import constants
from scipy.stats import linregress

#%% Configuration
data_filename            = [#'../PKL final data/flight_04.pkl',
                            #'../PKL final data/flight_05.pkl',
                            #'../PKL final data/flight_06.pkl',
                            '../PKL final data/flight_07.pkl',
                            #'../PKL final data/flight_08.pkl',
                            #'../PKL final data/flight_09.pkl',
                            #'../PKL final data/flight_10.pkl',
                            #'../PKL final data/flight_11.pkl',
                            #'../PKL final data/flight_12.pkl',
                            #'../PKL final data/flight_14.pkl',
                            #'../PKL final data/flight_15.pkl',
                            #'../PKL final data/flight_16.pkl'
                            ]


#x_limits                    = [0, 1e-4] # OK for flight 4
#x_limits                    = [0, 8e-4] # OK for flight 7
#x_limits                    = [0, 2e-4] # OK for flight 8
#x_limits                    = [0, 1.5e-4] # OK for flight 9
x_limits                    = [0, 2e-4] # OK for flight 11
label_profile               = True


#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)
        
        
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

#%% Visualization of single data points
fig, ax = plt.subplots(ncols=2, figsize=(30,15), dpi = 300)

plt.subplots_adjust(wspace = .05)
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    strbuff = "w = %s['H2O']" % s
    exec(strbuff)
    strbuff = "d18O = %s['d18O']" % s
    exec(strbuff)
    strbuff = "dD = %s['dD']" % s
    exec(strbuff)
    strbuff = "ALT = %s['ALT']" % s
    exec(strbuff)
    
    # Find index for ERA5
    ERA5_idx = np.where(abs(ncdate_ERA5 - d18O.index.mean()) == min(abs(ncdate_ERA5 - d18O.index.mean())))[0][0]
    # Extrapolate BLH i m AMSL
    BLH = ERA5_data['blh'][ERA5_idx] + ERA5_data['z'][ERA5_idx]

    #ax[0].scatter((1/w), d18O, s = 16, marker = 'o', facecolors='none', c = ALT, cmap = 'jet')
    #ax[1].scatter((1/w), dD, s = 16, marker = 'o', facecolors='none', c = ALT, cmap = 'jet')
    BBL_mask = ALT < BLH
    ABL_mask = ALT > BLH
    ax[0].scatter((w[BBL_mask]), d18O[BBL_mask], s = 16, marker = 'o', facecolors='k', alpha = 0.01)
    ax[0].scatter((w[ABL_mask]), d18O[ABL_mask], s = 16, marker = 'o', facecolors='r', alpha = 0.01)
    ax[1].scatter((w[BBL_mask]), dD[BBL_mask], s = 16, marker = 'o', facecolors='k', alpha = 0.01)
    ax[1].scatter((w[ABL_mask]), dD[ABL_mask], s = 16, marker = 'o', facecolors='r', alpha = 0.01)    
    
    # Linear fit
    res_d18O = linregress((1/w[BBL_mask]), d18O[BBL_mask])
    res_dD = linregress((1/w[BBL_mask]), dD[BBL_mask])
    # Plot fitted linex
    dummy_x = np.array([0, max(1/w[BBL_mask])])
    #ax[0].plot(dummy_x, dummy_x*res_d18O.slope + res_d18O.intercept, linewidth = 2, color = [0,0,0])
    #ax[1].plot(dummy_x, dummy_x*res_dD.slope + res_dD.intercept, linewidth = 2, color = [0,0,0])
    

# Common graphical settings
for axis in ax:
    axis.tick_params(axis='both', which='major', labelsize=14)
    axis.grid()
    #axis.set_xlim(x_limits)

# Specific graphical settings   
ax[0].set_xlabel('1/H$_2$O (1/ppm)', fontsize=18)
ax[0].set_ylabel('$\delta^{18}$O (‰)', fontsize=18)     
ax[1].set_xlabel('1/H$_2$O (1/ppm)', fontsize=18)
ax[1].set_ylabel('$\delta$D (‰)', fontsize=18)
#ax[2].set_xlabel('', fontsize=18)
#ax[3].yaxis.set_ticklabels([])
#ax[3].set_xlabel('d-excess (‰)', fontsize=18)
#ax[2].set_xlim([0, 20])

#buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
#fig.suptitle(buff_text)

fig.tight_layout()
fig.subplots_adjust(top=0.95)   
plt.show()

#%%
new_mask = flight_data_flight_07['ALT'] > 1500
from scipy.stats import linregress

asd = linregress(fligth_data_flight_07['ALT'][new_mask],
                 fligth_data_flight_07['dD'][new_mask] - 8*fligth_data_flight_07['d18O'][new_mask],
                 )
