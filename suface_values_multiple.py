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
fig, ax = plt.subplots(nrows = 4, sharex=True, dpi = 600)
plt.subplots_adjust(hspace = .25)
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    altitudes = []
    strbuff = "altitudes = %s['ALT']" % s
    exec(strbuff)
    altitude_mask = altitudes < surf_altitude_range
    strbuff = "df_subset = %s[%s['ALT'] < surf_altitude_range]" % (s, s)
    exec(strbuff)
    ax[0].grid('on')
    ax[0].scatter(np.mean(df_subset.index.day), df_subset['H2O'].mean(), s = 16, marker = 'o', edgecolor = 'k', facecolors='none',)
    ax[0].set_ylim([8000, 16000])
    ax[0].set_yticks(np.arange(8000, 18000, 2000))
    ax[0].set_ylabel('H$_{2}$O (ppm)', size = 8)
    ax[0].tick_params(axis='both', which='major', labelsize= 8)
    
    ax[1].scatter(np.mean(df_subset.index.day), df_subset['d18O'].mean(), s = 16, marker = 'o', edgecolor = [1,0,0], facecolors='none',)
    ax[1].set_ylim([-22, -14])
    ax[1].set_yticks(np.arange(-22, -13, 2))
    ax[1].grid('on')
    ax[1].set_ylabel('$\delta^{18}$O (‰)', size = 8)
    ax[1].tick_params(axis='both', which='major', labelsize= 8)
    
    ax[2].scatter(np.mean(df_subset.index.day), df_subset['dD'].mean(), s = 16, marker = 'o', edgecolor = [1,0,1], facecolors='none',)
    ax[2].set_ylim([-160, -80])
    ax[2].set_yticks(np.arange(-180, -80, 20))
    ax[2].grid('on')
    ax[2].set_ylabel('$\delta$D (‰)', size = 8)
    ax[2].tick_params(axis='both', which='major', labelsize= 8)
    
    ax[3].scatter(np.mean(df_subset.index.day), df_subset['dD'].mean() - 8*df_subset['d18O'].mean(), s = 16, marker = 'o', edgecolor = [0,0,1], facecolors='none',)
    ax[3].set_ylim([10, 25])
    ax[3].set_yticks(np.arange(10, 25, 5))
    ax[3].grid('on')
    ax[3].set_ylabel('d-excess (‰)', size = 8)
    ax[3].tick_params(axis='both', which='major', labelsize=8)
