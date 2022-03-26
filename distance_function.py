#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 17:41:52 2022

@author: daniele
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import pickle

from scipy import signal

from pyproj import Proj

#%% Configuration
data_filename            = '../PKL final data/flight_04.pkl'


display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 20000, 50)


#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)
    
#%% Convert Lat Lon in UTM (meters)
# https://ocefpaf.github.io/python4oceanographers/blog/2013/12/16/utm/
myProj = Proj("+proj=utm +zone=31T, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
UTMx, UTMy = myProj(flight_data['LON'].to_numpy(), flight_data['LAT'].to_numpy())
flight_data['UTMx'] = UTMx
flight_data['UTMy'] = UTMy

pos = [flight_data['UTMx'].to_numpy() - flight_data['UTMx'].mean(),
       flight_data['UTMy'].to_numpy() - flight_data['UTMy'].mean(),
       flight_data['ALT'].to_numpy() - flight_data['ALT'].mean(),]

#%% Calculate distances

import numpy as np
# Dimension of array (eg 2D or 3D)
dim = np.size(pos, 0)
elements = np.size(pos, 1)
dist = 0
for e in range(elements):
    for i in range(dim):
        dist += pos[:,i]