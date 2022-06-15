#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 15:10:16 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting 
import datetime

import pickle

from scipy import signal

#%% Configuration
data_filename            = '../PKL final data/flight_10.pkl'

#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)



#%% Visualization of single data points
alt_mask = flight_data['ALT'] > 1000
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(flight_data['LON'][alt_mask], flight_data['LAT'][alt_mask], flight_data['ALT'][alt_mask],
              s = 8, c = flight_data['dD'][alt_mask], cmap = 'jet')
              
#ax.set_xlabel('H$_2$O [ppm]', fontsize=18)
#ax.set_ylabel('Altitude [m AMSL]', fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=8)
ax.grid()

ax.set_xlabel('Lon (d.dd)')
ax.set_ylabel('Lat (d.dd)')
ax.set_zlabel('Altitude (m AMSL)')

#%% Some analsysis for EGU
from scipy.stats import linregress
threshold = 1500
alt_mask = flight_data['ALT'] < threshold

#alt_mask = (flight_data['ALT'] > 1200) & (flight_data['ALT'] < 1500)
#alt_mask = (flight_data['ALT'] > 700) & (flight_data['ALT'] < 825)



#slope, intercept, r, p, se = linregress(flight_data['ALT'][alt_mask], flight_data['dD'][alt_mask])
slope, intercept, r, p, se = linregress(flight_data['ALT'][alt_mask], 
                                        (flight_data['dD'][alt_mask] - 8*flight_data['d18O'][alt_mask]))
#slope, intercept, r, p, se = linregress(flight_data['d18O'][alt_mask], flight_data['dD'][alt_mask])
#plt.scatter(flight_data['ALT'][alt_mask], 
#            (flight_data['dD'][alt_mask] - 8*flight_data['d18O'][alt_mask]))
#plt.scatter( flight_data['d18O'][alt_mask], flight_data['dD'][alt_mask])
plt.scatter((flight_data['TA'][alt_mask]), flight_data['dD'][alt_mask])
slope, intercept, r, p, se = linregress(flight_data['TA'][alt_mask], flight_data['dD'][alt_mask])
print(slope)


