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
data_filename            = [#'../PKL final data/flight_04.pkl',
                            #'../PKL final data/flight_04_V1.pkl',
                            #'../PKL final data/flight_04_nofilt_V1.pkl',
                            #'../PKL final data/flight_05.pkl',
                            #'../PKL final data/flight_05_V1.pkl',
                            #'../PKL final data/flight_05_nofilt_V1.pkl',
                            #'../PKL final data/flight_06.pkl',
                            #'../PKL final data/flight_06_V1.pkl',
                            #'../PKL final data/flight_06_nofilt_V1.pkl',
                            #'../PKL final data/flight_07.pkl',
                            #'../PKL final data/flight_07_nofilt_V1.pkl',
                            #'../PKL final data/flight_07_V1.pkl',
                            #'../PKL final data/flight_08.pkl',
                            #'../PKL final data/flight_08_nofilt_V1.pkl',
                            #'../PKL final data/flight_08_V1.pkl',
                            #'../PKL final data/flight_09.pkl',
                            #'../PKL final data/flight_10.pkl',
                            #'../PKL final data/flight_11.pkl',
                            '../PKL final data/flight_12.pkl',
                            #'../PKL final data/flight_12_nofilt_V1.pkl',
                            '../PKL final data/flight_12_V1.pkl',
                            #'../PKL final data/flight_14.pkl',
                            #'../PKL final data/flight_15.pkl',
                            #'../PKL final data/flight_16.pkl',
                            ]


display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 3500, 100)
label_profile               = False

show_PBLH                   = True
PBLH_values                 = [1503.4145564912014, 1949.820674343401] # Average
PBLH_values                 = [981.7148488141952, 1002.3649894834459] # For flight 07, BLH at 15 and at 16
PBLH_values                 = [1553.746437814716, 1562.5964981015377] # For flight 10, BLH at 10 and 11

#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)

#%% Generate figure
fig, ax = plt.subplots(nrows=4, figsize=(20,15), sharex=True, dpi = 300)

#%% Visualization of single data points
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    # AX0
    strbuff = "ax[0].plot(%s.index, %s['d18O'], label = %s)" % (s, s, s) 
    exec(strbuff)
    # AX1
    strbuff = "ax[1].plot(%s.index, %s['dD'], label = %s)" % (s, s, s) 
    exec(strbuff)
    # AX2
    strbuff = "ax[2].plot(%s.index, %s['dD']-8*%s['d18O'], label = %s)" % (s, s, s, s) 
    exec(strbuff)
    # AX3
    strbuff = "ax[3].plot(%s.index, %s['UU'], label = %s)" % (s, s, s) 
    exec(strbuff)

# Common graphical settings
for axis in ax:
    axis.tick_params(axis='both', which='major', labelsize=14)
    axis.grid()

# Specific graphical settings   

ax[0].set_ylabel('$\delta^{18}$O (‰)', fontsize=18)
ax[1].set_ylabel('$\delta$D (‰)', fontsize=18)
#ax[3].yaxis.set_ticklabels([])
ax[2].set_ylabel('d-excess (‰)', fontsize=18)
ax[3].set_ylabel('RH$_{iMet}$ (%)', fontsize=18)
ax[3].set_xlabel('Time', fontsize=18)     

#buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
#fig.suptitle(buff_text)

#fig.tight_layout()
#fig.subplots_adjust(top=0.95)