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
                            '../PKL final data/flight_14.pkl',
                            '../PKL final data/flight_15.pkl',
                            '../PKL final data/flight_16.pkl',
                            ]


display                     = 'binned' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 3500, 100)
label_profile               = True

show_PBLH                   = True
PBLH_values                 = [1503.4145564912014, 1949.820674343401]


#%% Load data
for filename in data_filename:
    s = 'flight_data_' + filename[-13:-4]
    m = 'metadata_' + filename[-13:-4]
    with open(filename, 'rb') as f:
        strbuff = '%s, %s = pickle.load(f)' % (s, m)
        exec(strbuff)

#%% Generate figure
fig, ax = plt.subplots(ncols=4, figsize=(20,15), sharey=True, dpi = 300)

#%% Visualization of single data points
if display == 'raw':
    plt.subplots_adjust(wspace = .05)
    for filename in data_filename:
        s = 'flight_data_' + filename[-13:-4]
        # AX0
        strbuff = "ax[0].scatter(%s['H2O'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)
        # AX1
        strbuff = "ax[1].scatter(%s['d18O'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)
        # AX2
        strbuff = "ax[2].scatter(%s['dD'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s) 
        exec(strbuff)
        # AX3
        strbuff = "ax[3].scatter(%s['dD']-8*%s['d18O'], %s['ALT'], s = 16, marker = 'o', facecolors='none', c = %s.index, cmap = 'jet')" % (s, s, s, s) 
        exec(strbuff)

    # Common graphical settings
    for axis in ax:
        axis.tick_params(axis='both', which='major', labelsize=14)
        axis.grid()

    # Specific graphical settings   
    ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)     
    ax[0].set_xlabel('H$_2$O (ppm)', fontsize=18)
    ax[1].set_xlabel('$\delta^{18}$O (‰)', fontsize=18)
    ax[2].set_xlabel('$\delta$D (‰)', fontsize=18)
    #ax[3].yaxis.set_ticklabels([])
    ax[3].set_xlabel('d-excess (‰)', fontsize=18)
    #ax[2].set_xlim([0, 20])
    
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
        H2O_means   = np.repeat(np.nan, len(bins) - 1)
        H2O_stds    = np.repeat(np.nan, len(bins) - 1)
        d18O_means  = np.repeat(np.nan, len(bins) - 1)
        d18O_stds   = np.repeat(np.nan, len(bins) - 1)
        dD_means    = np.repeat(np.nan, len(bins) - 1)
        dD_stds     = np.repeat(np.nan, len(bins) - 1)
        d_means     = np.repeat(np.nan, len(bins) - 1)
        d_stds      = np.repeat(np.nan, len(bins) - 1)       
        for curr_bin, next_bin, idx in zip(bins[:-1], bins[1:], range(0, len(altitudes))):
            strbuff = "H2O_means[idx] = %s['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "H2O_stds[idx] = %s['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            strbuff = "d18O_means[idx] = %s['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "d18O_stds[idx] = %s['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            strbuff = "dD_means[idx] = %s['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "dD_stds[idx] = %s['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            
            d_means[idx] = dD_means[idx] - 8 * d18O_means[idx]
            d_stds[idx] = np.sqrt(dD_stds[idx]**2 + 8*d18O_stds[idx]**2) #https://acp.copernicus.org/preprints/acp-2018-1313/acp-2018-1313.pdf
        # Plot
        altitude_center = bins[:-1] + np.diff(bins)/2
        plt.subplots_adjust(wspace = .05) 
        ax[0].plot(H2O_means, altitude_center, linewidth=1, color = [0,0,0])
        ax[0].plot(H2O_means+H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].plot(H2O_means-H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].fill_betweenx(altitude_center, H2O_means-H2O_stds, H2O_means+H2O_stds, color = [0,0,0], alpha = .1)
        ax[0].set_xlabel('H$_2$O (ppm)', fontsize=18)
        ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)
        ax[0].tick_params(axis='both', which='major', labelsize=18)

        ax[1].plot(d18O_means, altitude_center, linewidth=1, color = [1,0,0])
        ax[1].plot(d18O_means+d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0], alpha = .1)
        ax[1].plot(d18O_means-d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0], alpha = .1)
        ax[1].fill_betweenx(altitude_center, d18O_means-d18O_stds, d18O_means+d18O_stds, color = [1,0,0], alpha = .1 )
        ax[1].tick_params(axis='both', which='major', labelsize=18)
        #ax[1].yaxis.set_ticklabels([])
        ax[1].set_xlabel('$\delta^{18}$O [‰]', fontsize=18)
    
        ax[2].plot(dD_means, altitude_center, linewidth=1, color = [1,0,1])
        ax[2].plot(dD_means+dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[2].plot(dD_means-dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[2].fill_betweenx(altitude_center, dD_means-dD_stds, dD_means+dD_stds, color = [1,0,1], alpha = .1 )
        ax[2].tick_params(axis='both', which='major', labelsize=18)
        #ax[2].yaxis.set_ticklabels([])
        ax[2].set_xlabel('$\delta$D (‰)', fontsize=18)
        
        ax[3].plot(d_means, altitude_center, linewidth=1, color = [0,0,1])
        ax[3].plot(d_means+d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1], alpha = .1)
        ax[3].plot(d_means-d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1], alpha = .1)
        ax[3].fill_betweenx(altitude_center, d_means-d_stds, d_means+d_stds, color = [0,0,1], alpha = .1 )
        ax[3].tick_params(axis='both', which='major', labelsize=18)
        #ax[3].yaxis.set_ticklabels([])
        ax[3].set_xlabel('d-excess (‰)', fontsize=18)
        
        if label_profile:
            strbuff = "hour_start = %s.index[0].hour" % s
            exec(strbuff)
            # Find nans
            nans = np.argwhere(np.isnan(d18O_means))
            good_idx = nans[0][0] - 1
            y = altitudes.max()

            x = H2O_means[good_idx]
            ax[0].text(x, y, hour_start, size= 18, weight=1.5)
            x = d18O_means[good_idx]
            ax[1].text(x, y, hour_start, size= 18, weight=1.5)
            x = dD_means[good_idx]
            ax[2].text(x, y, hour_start, size= 18, weight=1.5)
            x = d_means[good_idx]
            ax[3].text(x, y, hour_start, size= 18, weight=1.5)
        
        if show_PBLH:
            ax[0].plot([H2O_means[~np.isnan(H2O_means)].min(), H2O_means[~np.isnan(H2O_means)].max()],
                       [PBLH_values[0], PBLH_values[0]], 'k--')
            ax[0].plot([H2O_means[~np.isnan(H2O_means)].min(), H2O_means[~np.isnan(H2O_means)].max()],
                       [PBLH_values[1], PBLH_values[1]], 'k--')
            ax[1].plot([d18O_means[~np.isnan(d18O_means)].min(), d18O_means[~np.isnan(d18O_means)].max()],
                       [PBLH_values[0], PBLH_values[0]], 'k--')
            ax[1].plot([d18O_means[~np.isnan(d18O_means)].min(), d18O_means[~np.isnan(d18O_means)].max()],
                       [PBLH_values[1], PBLH_values[1]], 'k--')
            ax[2].plot([dD_means[~np.isnan(dD_means)].min(), dD_means[~np.isnan(dD_means)].max()],
                       [PBLH_values[0], PBLH_values[0]], 'k--')
            ax[2].plot([dD_means[~np.isnan(dD_means)].min(), dD_means[~np.isnan(dD_means)].max()],
                       [PBLH_values[1], PBLH_values[1]], 'k--')
            ax[3].plot([-20, 60],
                       [PBLH_values[0], PBLH_values[0]], 'k--')
            ax[3].plot([-20, 60],
                       [PBLH_values[1], PBLH_values[1]], 'k--')
            
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
    # Common graphical settings
    for axis in ax:
        axis.tick_params(axis='both', which='major', labelsize=18)
        axis.grid()
else:
    print("Display off")
