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
import random
import gstools as gs
from pyproj import Proj

import pickle

from scipy import signal

#%% Configuration
data_filename                   = '../PKL final data/flight_10.pkl'

var_of_interest                 = 'dD'

plot_trend_line                 = True
Lanas_Airfield_Pos              = [44.541083, 4.371550]
Lanas_Airfield_Altitude         = 275 # m AMSL

# Flight 03 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#start_date_str                  = '2021-09-17 15:46:00'
#stop_date_str                   = '2021-09-17 16:26:00'
# Flight 04 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
start_date_str                  = '2021-09-18 05:20:00'
stop_date_str                   = '2021-09-18 06:10:00'
# Flight 05 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# start_date_str                  = '2021-09-18 08:15:00'
# stop_date_str                   = '2021-09-18 09:30:00'
# Flight 06 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# start_date_str                  = '2021-09-18 12:20:00'
# stop_date_str                   = '2021-09-18 13:05:00'
# Flight 07 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#start_date_str                  = '2021-09-18 15:00:00'
#stop_date_str                   = '2021-09-18 16:10:00'
# Flight 08 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
start_date_str                  = '2021-09-19 08:00:00'
stop_date_str                   = '2021-09-19 09:15:00'
# Flight 10 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
start_date_str                  = '2021-09-20 09:40:00'
stop_date_str                   = '2021-09-20 10:00:00'


#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)

#%% Haversine function 
#https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
#from math import radians, cos, sin, asin, sqrt
def haversine(s_lat, s_lng, e_lat, e_lng):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees)
    """
    R = 6372.8
    s_lat = s_lat*np.pi/180.0                      
    s_lng = np.deg2rad(s_lng)     
    e_lat = np.deg2rad(e_lat)                       
    e_lng = np.deg2rad(e_lng)  

    d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2
    return 2 * R * np.arcsin(np.sqrt(d))*1000

#%% Convert Lat Lon in UTM (meters)
# https://ocefpaf.github.io/python4oceanographers/blog/2013/12/16/utm/
myProj = Proj("+proj=utm +zone=31T, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
UTMx, UTMy = myProj(flight_data['LON'].to_numpy(), flight_data['LAT'].to_numpy())
flight_data['UTMx'] = UTMx
flight_data['UTMy'] = UTMy

Lanas_Airfield_Pos_UTMx,Lanas_Airfield_Pos_UTMy =  myProj(Lanas_Airfield_Pos[1], Lanas_Airfield_Pos[0])

#%% Subset data by time
start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime(stop_date_str, '%Y-%m-%d %H:%M:%S')

flight_data = flight_data[(flight_data.index >= start_date) & (flight_data.index <= stop_date)]

#%% Generate random indexes for sampling
# Set the seed
random.seed(1234)
L = flight_data['H2O'].size
n_samples = round(L*0.1)
good_indexes = random.sample(range(0, L), n_samples)

#%% Detrend data and plot trendline

XVar = flight_data['TA'].to_numpy()
YVar = flight_data[var_of_interest].to_numpy()

#from lmfit.models import ExponentialModel
#mod = ExponentialModel()
from lmfit.models import PolynomialModel
mod = PolynomialModel(2)
pars = mod.guess(YVar, x=XVar)
fit_model = mod.fit(YVar, pars, x=XVar)
YVar_pred = fit_model.eval(XVar = XVar)
residuals = YVar - YVar_pred
if plot_trend_line:
    # Plot fit for trend removal
    fig, ax = plt.subplots(dpi = 300)
    ax.scatter(XVar[good_indexes],
               YVar[good_indexes])
    ax.scatter(XVar[good_indexes],
               YVar_pred[good_indexes],
               color = 'r')
    ax.set_xlabel('Altitude (m AMSL)')
    ax.set_ylabel(var_of_interest)
    ax.grid()
    print(fit_model.fit_report())
    r_squared = 1 - fit_model.residual.var() / np.var(YVar)
    print("R^2 of fitted model is %.2f" % r_squared)

#%%
dim = 3
# rotation around z, y, x
angles = [np.deg2rad(90), np.deg2rad(90), np.deg2rad(90)]
main_axes = gs.rotated_main_axes(dim, angles)
axis1, axis2, axis3 = main_axes

pos = (flight_data['UTMx'].to_numpy() - flight_data['UTMx'].mean(), 
       flight_data['UTMy'].to_numpy() - flight_data['UTMy'].mean(), 
       flight_data['ALT'].to_numpy() - flight_data['ALT'].mean())
#field = flight_data[var_of_interest].to_numpy()
field = residuals

bins = np.arange(0, 3000, 200)
bin_center, dir_vario, counts = gs.vario_estimate(
    pos,
    field,
    direction = main_axes,
    bandwidth=10,
    bin_edges = bins,
    #sampling_size=2000,
    #sampling_seed=1001,
    #mesh_type="structured",
    return_counts=True,
)

fig, ax = plt.subplots(nrows= 3, sharex=True)
ax[0].scatter(bin_center, dir_vario[0], label="0. axis")
ax[1].scatter(bin_center, dir_vario[1], label="1. axis")
ax[2].scatter(bin_center, dir_vario[2], label="2. axis")
plt.tight_layout()
#ax.set_ylim([0, 1])
#%% Plot  of single data points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(flight_data['UTMx'][good_indexes] - flight_data['UTMx'][good_indexes].mean(), 
           flight_data['UTMy'][good_indexes] - flight_data['UTMy'][good_indexes].mean(), 
           flight_data['ALT'][good_indexes] - flight_data['ALT'][good_indexes].mean(),
           s = 16, marker = 'o', edgecolors='none', 
           c = flight_data.index[good_indexes], cmap = 'jet') #edgecolors='k')

ax.plot([0, axis1[0]], [0, axis1[1]], [0, axis1[2]*1000], label="0.")
ax.plot([0, axis2[0]], [0, axis2[1]*1000], [0, axis2[2]], label="1.")
ax.plot([0, axis3[0]*1000], [0, axis3[1]], [0, axis3[2]], label="2.")
              
#ax.set_xlabel('H$_2$O [ppm]', fontsize=18)
#ax.set_ylabel('Altitude [m AMSL]', fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=14)
ax.grid()

ax.set_xlabel('Lon (d.dd)')
ax.set_ylabel('Lat (d.dd)')
ax.set_zlabel('Altitude (m AMSL)')

#%% Plot 1D data
fig, ax = plt.subplots(dpi = 300)
ax.scatter(flight_data['ALT'][good_indexes],
           #flight_data['H2O'][good_indexes])
           residuals[good_indexes])
#ax.plot(XVar, YVar_pred)

