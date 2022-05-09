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
from scipy.stats import linregress

#%% Configuration
data_filename            = [#'../PKL final data/flight_04.pkl',
                            #'../PKL final data/flight_05.pkl',
                            #'../PKL final data/flight_06.pkl',
                            #'../PKL final data/flight_07.pkl',
                            #'../PKL final data/flight_08.pkl',
                            #'../PKL final data/flight_09.pkl',
                            #'../PKL final data/flight_10.pkl',
                            #'../PKL final data/flight_11.pkl',
                            '../PKL final data/flight_12.pkl',
                            #'../PKL final data/flight_14.pkl',
                            #'../PKL final data/flight_15.pkl',
                            #'../PKL final data/flight_16.pkl'
                            ]


#x_limits                    = [0, 1e-4] # OK for flight 4
#x_limits                    = [0, 8e-4] # OK for flight 7
#x_limits                    = [0, 2e-4] # OK for flight 8
#x_limits                    = [0, 1.5e-4] # OK for flight 9
x_limits                    = [0, 2e-4] # OK for flight 11
label_profile               = True


#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)

#%% Generate figure
fig, ax = plt.subplots(ncols=2, figsize=(30,15), dpi = 300)

#%% Visualization of single data points
plt.subplots_adjust(wspace = .05)
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    strbuff = "w = %s['H2O']" % s
    exec(strbuff)
    strbuff = "d18O = %s['d18O']" % s
    exec(strbuff)
    strbuff = "dD = %s['dD']" % s
    exec(strbuff)
    strbuff = "ALT = %s['ALT']" % s
    exec(strbuff)

    ax[0].scatter((1/w), d18O, s = 16, marker = 'o', facecolors='none', c = ALT, cmap = 'jet')
    ax[1].scatter((1/w), dD, s = 16, marker = 'o', facecolors='none', c = ALT, cmap = 'jet')
    
    # Linear fit
    res_d18O = linregress((1/w), d18O)
    res_dD = linregress((1/w), dD)
    # Plot fitted linex
    dummy_x = np.array([min(1/w), max(1/w)])
    ax[0].plot(dummy_x, dummy_x*res_d18O.slope + res_d18O.intercept, linewidth = 2, color = [0,0,0])
    ax[1].plot(dummy_x, dummy_x*res_dD.slope + res_dD.intercept, linewidth = 2, color = [0,0,0])
    

# Common graphical settings
for axis in ax:
    axis.tick_params(axis='both', which='major', labelsize=14)
    axis.grid()
    axis.set_xlim(x_limits)

# Specific graphical settings   
ax[0].set_xlabel('1/H$_2$O (1/ppm)', fontsize=18)
ax[0].set_ylabel('$\delta^{18}$O (‰)', fontsize=18)     
ax[1].set_xlabel('1/H$_2$O (1/ppm)', fontsize=18)
ax[1].set_ylabel('$\delta$D (‰)', fontsize=18)
#ax[2].set_xlabel('', fontsize=18)
#ax[3].yaxis.set_ticklabels([])
#ax[3].set_xlabel('d-excess (‰)', fontsize=18)
#ax[2].set_xlim([0, 20])

#buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
#fig.suptitle(buff_text)

fig.tight_layout()
fig.subplots_adjust(top=0.95)   
