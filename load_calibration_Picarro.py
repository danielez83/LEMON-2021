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


#%% Load data into pandas 
filename = "../Picarro_HIDS2254/Standard_Table.txt"
calibration_data = pd.read_csv(filename, delimiter = ',')
# Convert index as datetime
calibration_data.index = pd.to_datetime(calibration_data['Date'], 
                                        format= '%d-%b-%Y %H:%M:%S')
calibration_data.drop('Date', axis = 1, inplace = True)

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
