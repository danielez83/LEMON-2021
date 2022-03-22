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

import pickle

from scipy import signal

#%% Configuration
data_filename                   = '../PKL final data/flight_03.pkl'

var_of_interest                 = 'H2O'

# Flight 03 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
start_date_str                  = '2021-09-17 15:46:00'
stop_date_str                   = '2021-09-17 16:26:00'

#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)

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

#%% Detrend data and

XVar = flight_data['ALT'].to_numpy()
YVar = flight_data[var_of_interest].to_numpy()

#from lmfit.models import ExponentialModel
#mod = ExponentialModel()
from lmfit.models import PolynomialModel
mod = PolynomialModel()
pars = mod.guess(YVar, x=XVar)
fit_model = mod.fit(YVar, pars, x=XVar)
#print(fit_model.fit_report())
r_squared = 1 - fit_model.residual.var() / np.var(YVar)
print("R^2 of fitted model is %.2f" % r_squared)
YVar_pred = fit_model.eval(XVar = XVar)
residuals = YVar - YVar_pred


#%% Plot  of single data points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter(flight_data['LON'][good_indexes], flight_data['LAT'][good_indexes], flight_data['ALT'][good_indexes],
              s = 16, marker = 'o', edgecolors='none', 
              c = flight_data.index[good_indexes], cmap = 'jet') #edgecolors='k')
              
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
           flight_data['H2O'][good_indexes])
           #residuals[good_indexes])
ax.plot(XVar, YVar_pred)

