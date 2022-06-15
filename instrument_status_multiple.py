#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 15:10:16 2021
Show isotope variaiblity at the surface.
@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import pickle

from scipy import signal

#%% Configuration
data_filename            = ['../PKL final data/flight_04.pkl',
                            '../PKL final data/flight_05.pkl',
                            '../PKL final data/flight_06.pkl',
                            '../PKL final data/flight_07.pkl',
                            '../PKL final data/flight_08.pkl',
                            '../PKL final data/flight_09.pkl',
                            '../PKL final data/flight_10.pkl',
                            '../PKL final data/flight_11.pkl',
                            '../PKL final data/flight_12.pkl',
                            '../PKL final data/flight_14.pkl',
                            '../PKL final data/flight_15.pkl',
                            '../PKL final data/flight_16.pkl',
                            ]


display                     = 'binned' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 3500, 100)
label_profile               = True

surf_altitude_range         = 600 # m AMSL --> 200 above ground


#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)

#%% Visualization of single data points
#fig, ax = plt.subplots(nrows = 4, sharex=True, dpi = 600)e, did #plt.subplots_adjust(hspace = .25)
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    strbuff = "data = %s.copy()" % s
    exec(strbuff)
    plt.scatter(data['ALT'], data['H2O'])

