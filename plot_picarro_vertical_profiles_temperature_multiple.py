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
data_filename            = ['../PKL final data/flight_04.pkl',
                            '../PKL final data/flight_05.pkl',
                            '../PKL final data/flight_06.pkl',
                            '../PKL final data/flight_07.pkl',
                            '../PKL final data/flight_08.pkl',
                            '../PKL final data/flight_09.pkl',
                            '../PKL final data/flight_10.pkl',
                            '../PKL final data/flight_11.pkl',
                            '../PKL final data/flight_12.pkl',
                            '../PKL final data/flight_13.pkl',
                            '../PKL final data/flight_14.pkl',
                            '../PKL final data/flight_15.pkl',
                            '../PKL final data/flight_16.pkl',
                            ]


display                     = 'binned' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 3500, 100)
label_profile               = True


#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)

#%% Generate figure
fig, ax = plt.subplots(ncols=3, figsize=(20,15), sharey=True, dpi = 300)

#%% Visualization of single data points
if display == 'raw':
    plt.subplots_adjust(wspace = .05)
    for filename in data_filename:
        s = 'flight_data_' + filename[-13:-4]
        # AX0
        strbuff = "ax[0].scatter(%s['TA'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)
        # AX1
        strbuff = "ax[1].scatter(%s['TD'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)
        # AX2
        strbuff = "ax[2].scatter(%s['UU'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)

    # Common graphical settings
    for axis in ax:
        axis.tick_params(axis='both', which='major', labelsize=14)
        axis.grid()

    # Specific graphical settings   
    ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)     
    ax[0].set_xlabel('Temperature (˚C)', fontsize=18)
    ax[1].set_xlabel('Dew point (˚C)', fontsize=18)
    ax[2].set_xlabel('RH (%)', fontsize=18)
    
    #buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
    #fig.suptitle(buff_text)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
elif display == 'binned':
    for filename in data_filename:
        s = 'flight_data_' + filename[-13:-4]
        # Extract altitudes vector
        altitudes = []
        strbuff = "altitudes = %s['ALT']" % s
        exec(strbuff)
        if bin_mode == 'auto':
            bins = np.histogram_bin_edges(altitudes[~np.isnan(altitudes)])
            bins = bins.tolist()
        TA_means   = np.repeat(np.nan, len(bins) - 1)
        TA_stds    = np.repeat(np.nan, len(bins) - 1)
        TD_means  = np.repeat(np.nan, len(bins) - 1)
        TD_stds   = np.repeat(np.nan, len(bins) - 1)
        UU_means    = np.repeat(np.nan, len(bins) - 1)
        UU_stds     = np.repeat(np.nan, len(bins) - 1)    
        for curr_bin, next_bin, idx in zip(bins[:-1], bins[1:], range(0, len(altitudes))):
            strbuff = "TA_means[idx] = %s['TA'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "TA_stds[idx] = %s['TA'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            strbuff = "TD_means[idx] = %s['TD'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "TD_stds[idx] = %s['TD'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            strbuff = "UU_means[idx] = %s['UU'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "UU_stds[idx] = %s['UU'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)

        # Plot
        altitude_center = bins[:-1] + np.diff(bins)/2
        plt.subplots_adjust(wspace = .05) 
        ax[0].plot(TA_means, altitude_center, linewidth=1, color = [0,0,0])
        ax[0].plot(TA_means+TA_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].plot(TA_means-TA_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].fill_betweenx(altitude_center, TA_means-TA_stds, TA_means+TA_stds, color = [0,0,0], alpha = .1)
        ax[0].set_xlabel('Temperature (˚C)', fontsize=18)
        ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)
        ax[0].tick_params(axis='both', which='major', labelsize=18)

        ax[1].plot(TD_means, altitude_center, linewidth=1, color = [1,0,0])
        ax[1].plot(TD_means+TD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0], alpha = .1)
        ax[1].plot(TD_means-TD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0], alpha = .1)
        ax[1].fill_betweenx(altitude_center, TD_means-TD_stds, TD_means+TD_stds, color = [1,0,0], alpha = .1 )
        ax[1].tick_params(axis='both', which='major', labelsize=18)
        #ax[1].yaxis.set_ticklabels([])
        ax[1].set_xlabel('Dew point (˚C)', fontsize=18)
    
        ax[2].plot(UU_means, altitude_center, linewidth=1, color = [1,0,1])
        ax[2].plot(UU_means+UU_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[2].plot(UU_means-UU_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[2].fill_betweenx(altitude_center, UU_means-UU_stds, UU_means+UU_stds, color = [1,0,1], alpha = .1 )
        ax[2].tick_params(axis='both', which='major', labelsize=18)
        #ax[2].yaxis.set_ticklabels([])
        ax[2].set_xlabel('RH (%)', fontsize=18)
               
        if label_profile:
            strbuff = "hour_start = %s.index[0].hour" % s
            exec(strbuff)
            # Find nans
            nans = np.argwhere(np.isnan(TD_means))
            good_idx = nans[0][0] - 1
            y = altitudes.max()

            x = TA_means[good_idx]
            ax[0].text(x, y, hour_start, size= 18, weight=1.5)
            x = TD_means[good_idx]
            ax[1].text(x, y, hour_start, size= 18, weight=1.5)
            x = UU_means[good_idx]
            ax[2].text(x, y, hour_start, size= 18, weight=1.5)
        
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    # Common graphical settings
    for axis in ax:
        axis.tick_params(axis='both', which='major', labelsize=18)
        axis.grid()
else:
    print("Display off")
