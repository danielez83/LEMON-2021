#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 15:37:47 2021

@author: daniele
"""
#%% Import section
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from sklearn.linear_model import LinearRegression

from hum_corr_fun import hum_corr_fun

from FARLAB_standards import standard

#%% Configuration
filename = "../Picarro_HIDS2254/Standard_Table.txt"
filename_to_save = "Standard_reg_param.pkl"


#%% Load data into pandas 
calibration_data = pd.read_csv(filename, delimiter = ',')
# Convert index as datetime
calibration_data.index = pd.to_datetime(calibration_data['Date'], 
                                        format= '%d-%b-%Y %H:%M:%S')
calibration_data.drop('Date', axis = 1, inplace = True)

#%% Apply humidity correction
calibration_data['d18O'] = hum_corr_fun(calibration_data['H20'], calibration_data['d18O'],
                                        18, 17000, 'mean')
calibration_data['dD'] = hum_corr_fun(calibration_data['H20'], calibration_data['dD'],
                                        2, 17000, 'mean')

# %% Plot section for Bermuda standard
# Plot calibration trend for 
fig, ax = plt.subplots(nrows = 2, figsize = [15,10])

calibration_data['d18O'][calibration_data['Standard'] == 'BERM'].plot(ax = ax[0])
ax[0].plot([np.min(calibration_data.index), np.max(calibration_data.index)], [0.5750, 0.5750],
           color = [1,0,0], linestyle = '--')
ax[0].grid()
ax[0].set(ylabel = "$\delta^{18}$O [‰]", ylim = [-1, 1])
ax[0].text(np.min(calibration_data.index), 0.75, "True Bermuda $\delta^{18}$O value")

calibration_data['dD'][calibration_data['Standard'] == 'BERM'].plot(ax = ax[1])
ax[1].plot([np.min(calibration_data.index), np.max(calibration_data.index)], [6.47, 6.47],
           color = [1,0,0], linestyle = '--')
ax[1].grid()
ax[1].set(ylabel = "$\delta$D [‰]", ylim = [0, 20])
ax[1].text(np.min(calibration_data.index), 7.5, "True Bermuda $\delta$D value")

# %% Plot section for GLW standard
# Plot calibration trend for 
fig, ax = plt.subplots(nrows = 2, figsize = [15,10])

calibration_data['d18O'][calibration_data['Standard'] == 'GLW'].plot(ax = ax[0])
ax[0].plot([np.min(calibration_data.index), np.max(calibration_data.index)], [-40.0608, -40.0608],
           color = [1,0,0], linestyle = '--')
ax[0].grid()
ax[0].set(ylabel = "$\delta^{18}$O [‰]", ylim = [-41, -35])
ax[0].text(np.min(calibration_data.index), -39.5, "True Bermuda $\delta^{18}$O value")

calibration_data['dD'][calibration_data['Standard'] == 'GLW'].plot(ax = ax[1])
ax[1].plot([np.min(calibration_data.index), np.max(calibration_data.index)], [-308.14, -308.14],
           color = [1,0,0], linestyle = '--')
ax[1].grid()
ax[1].set(ylabel = "$\delta$D [‰]", ylim = [-330, -300])
ax[1].text(np.min(calibration_data.index), -306, "True Bermuda $\delta$D value")

#%% Calculate calibration factors
# Days in standard table
days = calibration_data.index.day.unique()

start = datetime.datetime(2000, 1, 1)
dt_array = np.array([start + datetime.timedelta(hours=i) for i in range(len(days))])

d = {'Date': dt_array,
     'Slope_d18O':np.zeros(len(days)),
     'Intercept_d18O':np.zeros(len(days)),
     'Slope_dD':np.zeros(len(days)),
     'Intercept_dD':np.zeros(len(days))}

idx = 0

for day in days:
    temp_df = calibration_data[calibration_data.index.day == day]
    d['Date'][idx] = temp_df.index[0] + (temp_df.index[-1] - temp_df.index[0])/2
    # Create an observations column
    obs_vals_d18O = temp_df['d18O'].to_numpy()
    obs_vals_dD = temp_df['dD'].to_numpy()
    
    # Create a std_vals column
    std_vals_d18O = np.zeros(temp_df.d18O.count())
    std_vals_dD = np.zeros(temp_df.dD.count())
    for j in range(temp_df.d18O.count()):
        std_vals_d18O[j] = standard(temp_df['Standard'][j], 'd18O')
        std_vals_dD[j] = standard(temp_df['Standard'][j], 'dD')
    
    # Regress model
    modeld18O = LinearRegression().fit(obs_vals_d18O.reshape((-1, 1)), std_vals_d18O)
    # Save regression parameters
    d['Slope_d18O'][idx] = modeld18O.coef_
    d['Intercept_d18O'][idx] = modeld18O.intercept_
    # Regress model
    modeldD = LinearRegression().fit(obs_vals_dD.reshape((-1, 1)), std_vals_dD)
    # Save regression parameters
    d['Slope_dD'][idx] = modeldD.coef_
    d['Intercept_dD'][idx] = modeldD.intercept_
    
    idx+=1
        
#%% Save calibration parameters as dataframe

df = pd.DataFrame(data = d, index = d['Date'])
df.drop(columns = 'Date', inplace = True)
df.to_pickle(filename_to_save)
