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
data_filename            = '../PKL final data/flight_16.pkl'


display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 20000, 50)
calibrate_isotopes          = 'yes'
calibrate_humidity          = 'yes'

#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)



#%% Visualization of single data points
if display == 'raw':
    fig, ax = plt.subplots(ncols=3, figsize=(10,15))
    plt.subplots_adjust(wspace = .05) 
    ax[0].scatter(flight_data['H2O'], flight_data['ALT'],
                  s = 16, marker = 'o', facecolors='none', 
                  c = flight_data.index, cmap = 'jet') #edgecolors='k')
                  
    ax[0].set_xlabel('H$_2$O (ppm)', fontsize=18)
    ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)
    ax[0].tick_params(axis='both', which='major', labelsize=14)
    ax[0].grid()
    
    ax[1].scatter(flight_data['dD'], flight_data['ALT'],
                  s = 16, marker = 'o', facecolors='none',
                  c = flight_data.index, cmap = 'jet') #edgecolors='k')#edgecolors='r')
    ax[1].grid()
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    ax[1].yaxis.set_ticklabels([])
    ax[1].set_xlabel('$\delta$D (‰)', fontsize=18)
    
    ax[2].scatter(flight_data['dD']-8*flight_data['d18O'], flight_data['ALT'],
                  s = 16, marker = 'o', facecolors='none',
                  c = flight_data.index, cmap = 'jet') #edgecolors='k')edgecolors='b')
    ax[2].grid()
    ax[2].tick_params(axis='both', which='major', labelsize=14)
    ax[2].yaxis.set_ticklabels([])
    ax[2].set_xlabel('d-excess (‰)', fontsize=18)
    #ax[2].set_xlim([0, 20])
    
    #buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
    #fig.suptitle(buff_text)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
elif display == 'binned':
    # Compute means by bins
    altitudes   = flight_data['ALT']
    if bin_mode == 'auto':
        bins = np.histogram_bin_edges(altitudes[~np.isnan(altitudes)])
    bins = bins.tolist()
    H2O_means   = np.empty(len(bins) - 1)
    H2O_stds    = np.empty(len(bins) - 1)
    d18O_means  = np.empty(len(bins) - 1)
    d18O_stds   = np.empty(len(bins) - 1)
    dD_means    = np.empty(len(bins) - 1)
    dD_stds     = np.empty(len(bins) - 1)
    d_means     = np.empty(len(bins) - 1)
    d_stds      = np.empty(len(bins) - 1)
    for curr_bin, next_bin, idx in zip(bins[:-1], bins[1:], range(0, len(altitudes))):
        H2O_means[idx] = flight_data['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        H2O_stds[idx] = flight_data['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        d18O_means[idx] = flight_data['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        d18O_stds[idx] = flight_data['d18O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        dD_means[idx] = flight_data['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()
        dD_stds[idx] = flight_data['dD'][(altitudes > curr_bin) & (altitudes < next_bin)].std()
        d_means[idx] = dD_means[idx] - 8 * d18O_means[idx]
        d_stds[idx] = np.sqrt(dD_stds[idx]**2 + 8*d18O_stds[idx]**2) #https://acp.copernicus.org/preprints/acp-2018-1313/acp-2018-1313.pdf
        
    # Plot
    altitude_center = bins[:-1] + np.diff(bins)/2
    fig, ax = plt.subplots(ncols=3, figsize=(10,15))
    plt.subplots_adjust(wspace = .05) 
    ax[0].plot(H2O_means, altitude_center, linewidth=1, color = [0,0,0])
    ax[0].plot(H2O_means+H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0])
    ax[0].plot(H2O_means-H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0])
    ax[0].fill_betweenx(altitude_center, H2O_means-H2O_stds, H2O_means+H2O_stds, color = [0,0,0], alpha = .3 )
    ax[0].set_xlabel('H$_2$O (ppm)', fontsize=18)
    ax[0].set_ylabel('Altitude (m AMSL)', fontsize=18)
    ax[0].tick_params(axis='both', which='major', labelsize=14)
    ax[0].grid()

    # ax[1].plot(d18O_means, altitude_center, linewidth=1, color = [1,0,0])
    # ax[1].plot(d18O_means+d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    # ax[1].plot(d18O_means-d18O_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    # ax[1].fill_betweenx(altitude_center, d18O_means-d18O_stds, d18O_means+d18O_stds, color = [1,0,0], alpha = .3 )
    # ax[1].grid()
    # ax[1].tick_params(axis='both', which='major', labelsize=14)
    # ax[1].yaxis.set_ticklabels([])
    # ax[1].set_xlabel('$\delta^{18}$O [‰]', fontsize=18)
    
    ax[1].plot(dD_means, altitude_center, linewidth=1, color = [1,0,0])
    ax[1].plot(dD_means+dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    ax[1].plot(dD_means-dD_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,0])
    ax[1].fill_betweenx(altitude_center, dD_means-dD_stds, dD_means+dD_stds, color = [1,0,0], alpha = .3 )
    ax[1].grid()
    ax[1].tick_params(axis='both', which='major', labelsize=14)
    ax[1].yaxis.set_ticklabels([])
    ax[1].set_xlabel('$\delta$D (‰)', fontsize=18)
    
    ax[2].plot(d_means, altitude_center, linewidth=1, color = [0,0,1])
    ax[2].plot(d_means+d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1])
    ax[2].plot(d_means-d_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,1])
    ax[2].fill_betweenx(altitude_center, d_means-d_stds, d_means+d_stds, color = [0,0,1], alpha = .3 )
    ax[2].grid()
    ax[2].tick_params(axis='both', which='major', labelsize=14)
    ax[2].yaxis.set_ticklabels([])
    ax[2].set_xlabel('d-excess (‰)', fontsize=18)
    #ax[2].set_xlim([-50, 50])
    
    #buff_text = ("Flight n. %d  %s" % (Flight_OI, start_date.iloc[0]))
    #fig.suptitle(buff_text)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.95)
else:
    print("Display off")
