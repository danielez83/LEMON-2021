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

import pickle

from scipy import signal

#%% Configuration
data_filename            = '../PKL final data/flight_03.pkl'

#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)



#%% Visualization of single data points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(flight_data['LON'], flight_data['LAT'], flight_data['ALT'],
              s = 16, marker = 'o', edgecolors='none', 
              c = flight_data.index, cmap = 'jet') #edgecolors='k')
              
#ax.set_xlabel('H$_2$O [ppm]', fontsize=18)
#ax.set_ylabel('Altitude [m AMSL]', fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=14)
ax.grid()

ax.set_xlabel('Lon (d.dd)')
ax.set_ylabel('Lat (d.dd)')
ax.set_zlabel('Altitude (m AMSL)')



