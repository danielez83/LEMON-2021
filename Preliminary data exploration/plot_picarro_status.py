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
import matplotlib.dates as mdates

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

#%% Configuration
#iMet_filename      = '../iMet/44508/iMet-XQ2-44508_20210918.nc'
Picarro_filename   = '../Picarro_HIDS2254/2021/09/HIDS2254-20210923-DataLog_User.nc'
Flight_table_filename = '../Excel/Flights_Table.csv'
Flight_OI =  16#[4,5,6,7]#[8]#[9,10,11]#[12,13]#[14,15]#[16]
Calibration_param_filename = 'Standard_reg_param.pkl'

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

# Flight data    
df_Picarro_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_subset = df_Picarro.loc[df_Picarro_mask]

# Before Flight 45 min
start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
start_date = start_date - datetime.timedelta(minutes = 50)
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = stop_date - datetime.timedelta(minutes = 81)
df_Picarro_before_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_before_subset = df_Picarro.loc[df_Picarro_before_mask]

# After Flight 45 min
start_date = df_Flight_table['Takeoff_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
start_date = start_date + datetime.timedelta(minutes = 81)
stop_date = df_Flight_table['Landing_fulldate'][df_Flight_table['Flight ID'] == Flight_OI]
stop_date = stop_date + datetime.timedelta(minutes = 50)
df_Picarro_after_mask = (df_Picarro.index > start_date.iloc[0]) & (df_Picarro.index < stop_date.iloc[0])
df_Picarro_after_subset = df_Picarro.loc[df_Picarro_after_mask]

#%% PLot timeseries
date_format = mdates.DateFormatter("%H:%M")

fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9), (ax10, ax11, ax12)) = plt.subplots(nrows = 4, ncols=3, figsize=(15,10))
plt.subplots_adjust(wspace = .05) 

# Cavity Temperature ---------------------------------------------------------
CavityTemp_ylim = [round(df_Picarro_subset['CavityTemp'].min(), ndigits=2),
                   round(df_Picarro_after_subset['CavityTemp'].max(), ndigits=2)]
# before
ax1.plot(df_Picarro_before_subset.index, df_Picarro_before_subset['CavityTemp'], 'k-')
ax1.set(ylim=CavityTemp_ylim, ylabel = "Cavity Temperature [˚C]")
ax1.xaxis.set_major_formatter(date_format)
ax1.grid()
buff_text = ("Before flight %d" % Flight_OI)
ax1.set_title(buff_text)
# during
ax2.plot(df_Picarro_subset.index, df_Picarro_subset['CavityTemp'], 'r-')
ax2.set(ylim=CavityTemp_ylim)
ax2.yaxis.set_ticklabels([])
ax2.xaxis.set_major_formatter(date_format)
ax2.grid()
buff_text = ("During flight %d" % Flight_OI)
ax2.set_title(buff_text)
# after 
ax3.plot(df_Picarro_after_subset.index, df_Picarro_after_subset['CavityTemp'], 'k-')
ax3.set(ylim=CavityTemp_ylim)
ax3.yaxis.set_ticklabels([])
ax3.xaxis.set_major_formatter(date_format)
ax3.grid()
buff_text = ("After flight %d" % Flight_OI)
ax3.set_title(buff_text)

# Cavity Pressure ---------------------------------------------------------
CavityPress_ylim = [round(df_Picarro_subset['CavityPressure'].min(), ndigits=2), 
                    round(df_Picarro_subset['CavityPressure'].max(), ndigits=2)]
# before
ax4.plot(df_Picarro_before_subset.index, df_Picarro_before_subset['CavityPressure'], 'k-')
ax4.set(ylim=CavityPress_ylim, ylabel = "Cavity Pressure [Torr]")
ax4.xaxis.set_major_formatter(date_format)
ax4.grid()
# during
ax5.plot(df_Picarro_subset.index, df_Picarro_subset['CavityPressure'], 'r-')
ax5.set(ylim=CavityPress_ylim)
ax5.yaxis.set_ticklabels([])
ax5.xaxis.set_major_formatter(date_format)
ax5.grid()
# after 
ax6.plot(df_Picarro_after_subset.index, df_Picarro_after_subset['CavityPressure'], 'k-')
ax6.set(ylim=CavityPress_ylim)
ax6.yaxis.set_ticklabels([])
ax6.xaxis.set_major_formatter(date_format)
ax6.grid()

# Warm Box Temperature ---------------------------------------------------------
WarmBox_ylim = [round(df_Picarro_subset['WarmBoxTemp'].min(), ndigits=2),
                round(df_Picarro_subset['WarmBoxTemp'].max()+.1, ndigits=2)]
# before
ax7.plot(df_Picarro_before_subset.index, df_Picarro_before_subset['WarmBoxTemp'], 'k-')
ax7.set(ylim=WarmBox_ylim, ylabel = "Warm Box Temperature [˚C]")
ax7.xaxis.set_major_formatter(date_format)
ax7.grid()
# during
ax8.plot(df_Picarro_subset.index, df_Picarro_subset['WarmBoxTemp'], 'r-')
ax8.set(ylim=WarmBox_ylim)
ax8.yaxis.set_ticklabels([])
ax8.xaxis.set_major_formatter(date_format)
ax8.grid()
# after 
ax9.plot(df_Picarro_after_subset.index, df_Picarro_after_subset['WarmBoxTemp'], 'k-')
ax9.set(ylim=WarmBox_ylim)
ax9.yaxis.set_ticklabels([])
ax9.xaxis.set_major_formatter(date_format)
ax9.grid()

# DAS Temperature ---------------------------------------------------------
DAS_ylim = [round(df_Picarro_subset['DasTemp'].min()-5, ndigits=2),
            round(df_Picarro_after_subset['DasTemp'].max()+5, ndigits=2)]
# before
ax10.plot(df_Picarro_before_subset.index, df_Picarro_before_subset['DasTemp'], 'k-')
ax10.set(ylim=DAS_ylim, ylabel = "DAS Temperature [˚C]")
ax10.xaxis.set_major_formatter(date_format)
ax10.grid()
# during
ax11.plot(df_Picarro_subset.index, df_Picarro_subset['DasTemp'], 'r-')
ax11.set(ylim=DAS_ylim)
ax11.yaxis.set_ticklabels([])
ax11.xaxis.set_major_formatter(date_format)
ax11.grid()
# after 
ax12.plot(df_Picarro_after_subset.index, df_Picarro_after_subset['DasTemp'], 'k-')
ax12.set(ylim=DAS_ylim)
ax12.yaxis.set_ticklabels([])
ax12.xaxis.set_major_formatter(date_format)
ax12.grid()

#ax7.plot(df_Picarro_before_subset.index, df_Picarro_before_subset['CavityTemp'], 'k-')
#ax7.set(ylim=[79.5, 80.5])
#ax7.xaxis.set_major_formatter(date_format)
fig.autofmt_xdate()

buff_text = ("%d-%d-%d" % (df_Picarro_subset.index[0].day, df_Picarro_subset.index[0].month, df_Picarro_subset.index[0].year))
fig.suptitle(buff_text, fontsize=16)