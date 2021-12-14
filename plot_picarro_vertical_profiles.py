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
#from scipy.stats import linregress

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

#%% Configuration
#iMet_filename               = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename            = '../Picarro_HIDS2254/2021/09/HIDS2254-20210923-DataLog_User.nc'
Flight_table_filename       = '../Excel/Flights_Table.csv'
Flight_OI                   =  16#[2,3]#[4,5,6,7]#[8]#[9,10,11]#[12]#[14,15]#[16]
Calibration_param_filename  = 'Standard_reg_param_STD_corr.pkl'
display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'auto' #'auto', 'manual'
bins                        = np.arange(400, 20000, 400)
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

#%% Pressure to alitude conversion
# https://www.weather.gov/epz/wxcalc_pressurealtitude
Torr2feet = lambda p:(1-((p*1.33322)/1013.25)**(0.190284))*145366.45
Torr2meters = lambda p: ((1-((p*1.33322)/1013.25)**(0.190284))*145366.45)*0.3048

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
                                  'AmbientPressure':AmbientPressure,
                                  'CavityPressure': CavityPressure,
                                  'CavityTemp':CavityTemp,
                                  'DasTemp':DasTemp,
                                  'WarmBoxTemp':WarmBoxTemp}, index = ncdate_pd_picarro)
# Resample and center at 1 sec freq
df_Picarro = df_Picarro.resample("1S").mean()

#%% Import Flights table to filter only flight time
df_Flight_table = pd.read_csv(Flight_table_filename)
df_Flight_table['Takeoff_fulldate'] = pd.to_datetime(df_Flight_table['Takeoff_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')
df_Flight_table['Landing_fulldate'] = pd.to_datetime(df_Flight_table['Landing_fulldate'], 
                                                         format = '%d/%m/%Y %H:%M')

start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
if Flight_OI == 1:
    start_date = start_date + datetime.timedelta(minutes = 5)
    #stop_date = stop_date - datetime.timedelta(minutes = 5)   
# Adjust time for comparison. It is flight dependent
if Flight_OI == 7:
    start_date = start_date + datetime.timedelta(minutes = 5)
    stop_date = stop_date - datetime.timedelta(minutes = 5)     
    
df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]
#df_iMet_mask = (df_iMet.index > start_date.iloc[0]) & (df_iMet.index < stop_date.iloc[0])
#df_iMet_subset = df_iMet.loc[df_iMet_mask]

#%% Calibrate Picarro data
calibration_paramters = pd.read_pickle(Calibration_param_filename)
DOI = df_Picarro_subset.index[100].day
tot = calibration_paramters.index.day == DOI
IOI = np.where(tot==True)
IOI = IOI[0][0]

Picarro_data_calibrated = df_Picarro_subset.copy()
# Humidity-isotope correction
Picarro_data_calibrated['d18O'] = hum_corr_fun(df_Picarro_subset['H2O'], 
                                               df_Picarro_subset['d18O'], 
                                               18, 17000, 'mean')
Picarro_data_calibrated['dD'] = hum_corr_fun(df_Picarro_subset['H2O'], 
                                               df_Picarro_subset['dD'], 
                                               2, 17000, 'mean')
# Isotope calibration
if calibrate_isotopes == 'yes':
    Picarro_data_calibrated['d18O'] = Picarro_data_calibrated['d18O']*calibration_paramters['Slope_d18O'].iloc[IOI]+calibration_paramters['Intercept_d18O'].iloc[IOI]
    Picarro_data_calibrated['dD'] = Picarro_data_calibrated['dD']*calibration_paramters['Slope_dD'].iloc[IOI]+calibration_paramters['Intercept_dD'].iloc[IOI]
else:
    Picarro_data_calibrated['d18O'] = df_Picarro_subset['d18O']
    Picarro_data_calibrated['dD'] = df_Picarro_subset['dD']

# Humidity calibration, using OPTISONDE relationship
if calibrate_humidity == 'yes':
    Picarro_data_calibrated['H2O'] = Picarro_data_calibrated['H2O']*0.957 - 6.431
else:
    Picarro_data_calibrated['H2O'] = Picarro_data_calibrated['H2O']

#%% Visualization of single data points
if display == 'raw':
    fig, ax = plt.subplots(ncols=3, figsize=(10,15))
    plt.subplots_adjust(wspace = .05) 
    ax[0].scatter(Picarro_data_calibrated['H2O'], Torr2meters(df_Picarro_subset['AmbientPressure']),
                  s = 16, marker = 'o', facecolors='none', 
                  c = Picarro_data_calibrated.index, cmap = 'jet') #edgecolors='k')
                  
    ax[0].set_xlabel('H$_2$O [ppm]', fontsize=18)
    ax[0].set_ylabel('Altitude [m AMSL]', fontsize=18)
    ax[0].tick_params(axis='both', which='major', labelsize=14)
    ax[0].grid()
    
    ax[1].scatter(Picarro_data_calibrated['dD'], Torr2meters(df_Picarro_subset['AmbientPressure']),
                  s = 16, marker = 'o', facecolors='none',
                  c = Picarro_data_calibrated.index, cmap = 'jet') #edgecolors='k')#edgecolors='r')
    ax[1].grid()
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    ax[1].yaxis.set_ticklabels([])
    ax[1].set_xlabel('$\delta$D [‰]', fontsize=18)
    
    ax[2].scatter(Picarro_data_calibrated['dD']-8*Picarro_data_calibrated['d18O'], Torr2meters(df_Picarro_subset['AmbientPressure']),
                  s = 16, marker = 'o', facecolors='none',
                  c = Picarro_data_calibrated.index, cmap = 'jet') #edgecolors='k')edgecolors='b')
    ax[2].grid()
    ax[2].tick_params(axis='both', which='major', labelsize=14)
    ax[2].yaxis.set_ticklabels([])
    ax[2].set_xlabel('d-excess [‰]', fontsize=18)
    ax[2].set_xlim([-50, 50])
    
    buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
    fig.suptitle(buff_text)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
elif display == 'binned':
    # Compute means by bins
    altitudes   = Torr2meters(df_Picarro_subset['AmbientPressure'])
    if bin_mode == 'auto':
        bins = np.histogram_bin_edges(altitudes[~np.isnan(altitudes)])
    bins = bins.tolist()
    H2O_means   = np.empty(len(bins) - 1)
    H2O_stds    = np.empty(len(bins) - 1)
    d18O_means  = np.empty(len(bins) - 1)
    d18O_stds   = np.empty(len(bins) - 1)
    dD_means    = np.empty(len(bins) - 1)
    dD_stds     = np.empty(len(bins) - 1)
    d_means     = np.empty(len(bins) - 1)
    d_stds      = np.empty(len(bins) - 1)
    for curr_bin, next_bin, idx in zip(bins[:-1], bins[1:], range(0, len(altitudes))):
        H2O_means[idx] = Picarro_data_calibrated['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        H2O_stds[idx] = Picarro_data_calibrated['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        d18O_means[idx] = Picarro_data_calibrated['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        d18O_stds[idx] = Picarro_data_calibrated['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        dD_means[idx] = Picarro_data_calibrated['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        dD_stds[idx] = Picarro_data_calibrated['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        d_means[idx] = dD_means[idx] - 8 * d18O_means[idx]
        d_stds[idx] = np.sqrt(dD_stds[idx]**2 + 8*d18O_stds[idx]**2) #https://acp.copernicus.org/preprints/acp-2018-1313/acp-2018-1313.pdf
        
    # Plot
    altitude_center = bins[:-1] + np.diff(bins)/2
    fig, ax = plt.subplots(ncols=3, figsize=(10,15))
    plt.subplots_adjust(wspace = .05) 
    ax[0].plot(H2O_means, altitude_center, linewidth=1, color = [0,0,0])
    ax[0].plot(H2O_means+H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0])
    ax[0].plot(H2O_means-H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0])
    ax[0].fill_betweenx(altitude_center, H2O_means-H2O_stds, H2O_means+H2O_stds, color = [0,0,0], alpha = .3 )
    ax[0].set_xlabel('H$_2$O [ppm]', fontsize=18)
    ax[0].set_ylabel('Altitude [m AMSL]', fontsize=18)
    ax[0].tick_params(axis='both', which='major', labelsize=14)
    ax[0].grid()

    # ax[1].plot(d18O_means, altitude_center, linewidth=1, color = [1,0,0])
    # ax[1].plot(d18O_means+d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    # ax[1].plot(d18O_means-d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    # ax[1].fill_betweenx(altitude_center, d18O_means-d18O_stds, d18O_means+d18O_stds, color = [1,0,0], alpha = .3 )
    # ax[1].grid()
    # ax[1].tick_params(axis='both', which='major', labelsize=14)
    # ax[1].yaxis.set_ticklabels([])
    # ax[1].set_xlabel('$\delta^{18}$O [‰]', fontsize=18)
    
    ax[1].plot(dD_means, altitude_center, linewidth=1, color = [1,0,0])
    ax[1].plot(dD_means+dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    ax[1].plot(dD_means-dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    ax[1].fill_betweenx(altitude_center, dD_means-dD_stds, dD_means+dD_stds, color = [1,0,0], alpha = .3 )
    ax[1].grid()
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    ax[1].yaxis.set_ticklabels([])
    ax[1].set_xlabel('$\delta$D [‰]', fontsize=18)
    
    ax[2].plot(d_means, altitude_center, linewidth=1, color = [0,0,1])
    ax[2].plot(d_means+d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1])
    ax[2].plot(d_means-d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1])
    ax[2].fill_betweenx(altitude_center, d_means-d_stds, d_means+d_stds, color = [0,0,1], alpha = .3 )
    ax[2].grid()
    ax[2].tick_params(axis='both', which='major', labelsize=14)
    ax[2].yaxis.set_ticklabels([])
    ax[2].set_xlabel('d-excess [‰]', fontsize=18)
    #ax[2].set_xlim([-50, 50])
    
    buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
    fig.suptitle(buff_text)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
else:
    print("Display off")

