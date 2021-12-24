#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 22:18:35 2021

@author: daniele
"""

#%% Import section
import pandas as pd
import numpy as np
import netCDF4 as nc
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

from scipy.signal import savgol_filter

from FARLAB_standards import standard


calibration_paramters = pd.read_pickle('Standard_reg_param.pkl')

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

#%% Apply Humidity correction
DOI = Picarro_data.index[3600].day
tot = calibration_paramters.index.day == DOI
IOI = np.where(tot==True)
IOI = IOI[0][0]

Picarro_data_calibrated = Picarro_data.copy()
# Humidity-isotope correction
Picarro_data_calibrated['d18O'] = hum_corr_fun(Picarro_data['H2O'], 
                                               Picarro_data['d18O'], 
                                               18, 17000, 'mean')
Picarro_data_calibrated['dD'] = hum_corr_fun(Picarro_data['H2O'], 
                                               Picarro_data['dD'], 
                                               2, 17000, 'mean')
# Isotope calibration
Picarro_data_calibrated['d18O'] = Picarro_data_calibrated['d18O']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
Picarro_data_calibrated['dD'] = Picarro_data_calibrated['dD']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]

#%%
idx_start = 250000
idx_stop =  270000
#idx_start = 25000 # Ok for deep profile example
#idx_stop = 50000 # Ok for deep profile example
#idx_start = 141500 # OK FLIGTH 10 DETAILS
#idx_stop = 165000 # OK FLIGTH 10 DETAILS
#date_format = mdates.DateFormatter("%H:%M:%S")
date_format = mdates.DateFormatter("%H:%M")
#idx_start   = 100000 # OK FOR CALIBRATION DETAIL
#idx_stop    = 150000 # OK FOR CALIBRATION DETAIL
fig, ax = plt.subplots(nrows=3)
ax[0].plot(Picarro_data.index[idx_start:idx_stop], Picarro_data['d18O'][idx_start:idx_stop])
ax[0].plot(Picarro_data_calibrated.index[idx_start:idx_stop], Picarro_data_calibrated['d18O'][idx_start:idx_stop])
ax[0].grid()
ax[0].xaxis.set_major_formatter(date_format)
#ax[0].set_ylim(-5, 5)

ax[1].plot(Picarro_data.index[idx_start:idx_stop], Picarro_data['dD'][idx_start:idx_stop])
ax[1].plot(Picarro_data_calibrated.index[idx_start:idx_stop], Picarro_data_calibrated['dD'][idx_start:idx_stop])
ax[1].grid()
#ax[1].set_ylim(-10, 10)
ax[1].xaxis.set_major_formatter(date_format)

d_excess = Picarro_data['dD'] - 8* Picarro_data['d18O']
d_excess_calibrated = Picarro_data_calibrated['dD'] - 8* Picarro_data_calibrated['d18O']
ax[2].plot(Picarro_data.index[idx_start:idx_stop], d_excess[idx_start:idx_stop])
ax[2].plot(Picarro_data_calibrated.index[idx_start:idx_stop], d_excess_calibrated[idx_start:idx_stop])
ax[2].grid()
ax[2].xaxis.set_major_formatter(date_format)
#%% Plot dD and Altitude Flight 10
fig, ax = plt.subplots(nrows = 2, figsize = (15, 10))
yhat = savgol_filter(Picarro_data['dD'][idx_start:idx_stop], 101, 1)
yhat_calib = savgol_filter(Picarro_data_calibrated['dD'][idx_start:idx_stop], 101, 1)
ax[0].plot(Picarro_data.index[idx_start:idx_stop], yhat)
ax[0].plot(Picarro_data_calibrated.index[idx_start:idx_stop], yhat_calib)
ax[0].grid()
#ax[1].set_ylim(-10, 10)
ax[0].xaxis.set_major_formatter(date_format)
ax[0].set(ylabel = '$\delta$D [‰]')
ax[0].legend(["RAW", "Calibrated"])

altitude = (-22286*np.log(AmbientPressure[idx_start:idx_stop]) + 148309)*0.3048
ax[1].plot(Picarro_data.index[idx_start:idx_stop], altitude, color = 'r')
ax[1].grid()
#ax[1].set_ylim(-10, 10)
ax[1].xaxis.set_major_formatter(date_format)
ax[1].set(ylabel = 'Altitude [m ASL]')
#%% Plot Humidity
fig, ax = plt.subplots(figsize = (15, 5))
yhat = savgol_filter(Picarro_data['H2O'][idx_start:idx_stop], 101, 1)
yhat_calib = savgol_filter(Picarro_data_calibrated['dD'][idx_start:idx_stop], 101, 1)
ax.plot(Picarro_data.index[idx_start:idx_stop], yhat, color = 'k')
ax.grid()
#ax[1].set_ylim(-10, 10)
ax.xaxis.set_major_formatter(date_format)
ax.set(ylabel = 'H$_2$O [ppm]')
#ax.legend(["RAW", "Calibrated"])

#%% Plot humidity, d18O dD, d-excess
idx_start = 258000 # Standard spike
idx_stop =  265000 # Standard spike
fig, ax = plt.subplots(nrows=4, figsize = (10, 15))
yhat_calib = savgol_filter(Picarro_data_calibrated['d18O'][idx_start:idx_stop], 11, 1)
ax[0].plot([Picarro_data_calibrated.index[idx_start], Picarro_data_calibrated.index[idx_stop]], [standard('BER', 'd18O'), standard('BER', 'd18O')], 'r--')
ax[0].plot(Picarro_data.index[idx_start:idx_stop], yhat_calib)
ax[0].grid()
ax[0].set_ylim(-30, 2)
ax[0].xaxis.set_major_formatter(date_format)
ax[0].set(ylabel = '$\delta^{18}$O [‰]')

yhat_calib = savgol_filter(Picarro_data_calibrated['dD'][idx_start:idx_stop], 11, 1)
ax[1].plot(Picarro_data.index[idx_start:idx_stop], yhat_calib)
ax[1].plot([Picarro_data_calibrated.index[idx_start], Picarro_data_calibrated.index[idx_stop]], [standard('BER', 'dD'), standard('BER', 'dD')], 'r--')
ax[1].grid()
ax[1].set_ylim(-200, 20)
ax[1].xaxis.set_major_formatter(date_format)
ax[1].set(ylabel = '$\delta$D [‰]')

expected_d = standard('BER', 'dD') - 8* standard('BER', 'd18O')

yhat_calib = savgol_filter(Picarro_data_calibrated['dD'][idx_start:idx_stop] - 8*Picarro_data_calibrated['d18O'][idx_start:idx_stop] , 11, 1)
ax[2].plot(Picarro_data.index[idx_start:idx_stop], yhat_calib)
ax[2].plot([Picarro_data_calibrated.index[idx_start], Picarro_data_calibrated.index[idx_stop]], [expected_d, expected_d], 'r--')
ax[2].grid()
ax[2].set_ylim(-20, 45)
ax[2].xaxis.set_major_formatter(date_format)
ax[2].set(ylabel = 'd-excess [‰]')

yhat_calib = savgol_filter(Picarro_data_calibrated['H2O'][idx_start:idx_stop], 11, 1)
ax[3].plot(Picarro_data.index[idx_start:idx_stop], yhat_calib)
ax[3].grid()
ax[3].set_ylim(1000, 11000)
ax[3].xaxis.set_major_formatter(date_format)
ax[3].set(ylabel = 'H$_2$O [ppm]')



