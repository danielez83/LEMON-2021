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
                            #'../PKL final data/flight_05.pkl',
                            #'../PKL final data/flight_06.pkl',
                            #'../PKL final data/flight_07.pkl',
                            #'../PKL final data/flight_08.pkl',
                            #'../PKL final data/flight_09.pkl',
                            #'../PKL final data/flight_10.pkl',
                            #'../PKL final data/flight_11.pkl',
                            #'../PKL final data/flight_12.pkl',
                            #'../PKL final data/flight_14.pkl',
                            #'../PKL final data/flight_15.pkl',
                            #'../PKL final data/flight_16.pkl',
                            ]


display                     = 'binned' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 3500, 100)
label_profile               = False

show_PBLH                   = False
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
fig, ax = plt.subplots(ncols = 2, figsize=(15,15), sharey=True)

#%% Visualization of single data points
if display == 'raw':
    print('asd')
    # plt.subplots_adjust(wspace = .05)

elif display == 'binned':
    for filename in data_filename:
        s = 'flight_data_' + filename[-13:-4]
        # Extract altitudes vector
        altitudes = []
        strbuff = "altitudes = %s['ALT']" % s
        exec(strbuff)
        strbuff = "curr_flight_data = %s" % s
        exec(strbuff)
        if bin_mode == 'auto':
            bins = np.histogram_bin_edges(altitudes[~np.isnan(altitudes)])
            bins = bins.tolist()
        H2O_means   = np.repeat(np.nan, len(bins) - 1)
        H2O_stds    = np.repeat(np.nan, len(bins) - 1)
        HDO_means    = np.repeat(np.nan, len(bins) - 1)
        HDO_stds     = np.repeat(np.nan, len(bins) - 1)
        # Convert dD in HDO (ppm)
        Pw = curr_flight_data['H2O']*curr_flight_data['P']/1e6
        H2O_dry = 1e6*Pw/(curr_flight_data['P'] - Pw)
        HDO = (((curr_flight_data['dD']/1e3)+1)*(2*155.76e-6))*(H2O_dry)
        curr_flight_data['HDO'] = HDO.to_numpy()
        altitude_center = bins[:-1] + np.diff(bins)/2
    
        for curr_bin, next_bin, idx in zip(bins[:-1], bins[1:], range(0, len(altitudes))):
            strbuff = "H2O_means[idx] = %s['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "H2O_stds[idx] = %s['H2O'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
            strbuff = "HDO_means[idx] = %s['HDO'][(altitudes > curr_bin) & (altitudes < next_bin)].mean()" % s
            exec(strbuff)
            strbuff = "HDO_stds[idx] = %s['HDO'][(altitudes > curr_bin) & (altitudes < next_bin)].std()" % s
            exec(strbuff)
 

        ax[0].plot(H2O_means, altitude_center, linewidth=1, color = [0,0,0])
        ax[0].plot(H2O_means+H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].plot(H2O_means-H2O_stds, altitude_center, linestyle = '--', linewidth=1, color = [0,0,0], alpha = .1)
        ax[0].fill_betweenx(altitude_center, H2O_means-H2O_stds, H2O_means+H2O_stds, color = [0,0,0], alpha = .1)
        ax[0].set_xlabel('H$_2^{16}$O (ppm)', fontsize=32)
        ax[0].set_ylabel('Altitude (m AMSL)', fontsize=32)
        ax[0].tick_params(axis='both', which='major', labelsize=36)

        ax[1].plot(HDO_means, altitude_center, linewidth=1, color = [1,0,1])
        ax[1].plot(HDO_means+HDO_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[1].plot(HDO_means-HDO_stds, altitude_center, linestyle = '--', linewidth=1, color = [1,0,1], alpha = .1)
        ax[1].fill_betweenx(altitude_center, HDO_means-HDO_stds, HDO_means+HDO_stds, color = [1,0,1], alpha = .1 )
        ax[1].tick_params(axis='both', which='major', labelsize=36)
        #ax[1].yaxis.set_ticklabels([])
        #ax[1].set_ylabel('Altitude (m AMSL)', fontsize=32)
        ax[1].set_xlabel('HD$^{16}$O  (ppm)', fontsize=32)
        ax[1].set_xticks(np.arange(0,5, 1)) # OK flight 7

            
        #fig.tight_layout()
        fig.subplots_adjust(top=0.95)
    #ax[1].set_xticks(np.arange(-35, -10, 5)) # OK flight 7
    #ax[3].set_xticks(np.arange(-10, 55, 10)) # OK flight 7
    #ax[1].set_xticks(np.arange(-17, -15.5, .5)) # OK flight 10
    #ax[2].set_xticks(np.arange(-122, -112, 3)) # OK flight 10
    #ax[3].set_xticks(np.arange(5, 26, 5)) # OK flight 10
    #x[3].set_xlim([0,25]) # OK flight 10
    
    # Common graphical settings
    for axis in ax:
        axis.tick_params(axis='both', which='major', labelsize=32)
        axis.grid('on')
else:
    print("Display off")

plt.savefig("flights_ALL.svg", transparent=True)