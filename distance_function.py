#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 17:41:52 2022

@author: daniele
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

import pickle

from scipy import signal

from pyproj import Proj

#%% Configuration
data_filename            = '../PKL final data/flight_07.pkl'


display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 20000, 50)


#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)

flight_data = flight_data[flight_data['ALT'] < 2000]
    
#%% Convert Lat Lon in UTM (meters)
# https://ocefpaf.github.io/python4oceanographers/blog/2013/12/16/utm/
myProj = Proj("+proj=utm +zone=31T, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
UTMx, UTMy = myProj(flight_data['LON'].to_numpy(), flight_data['LAT'].to_numpy())
flight_data['UTMx'] = UTMx
flight_data['UTMy'] = UTMy

pos = np.array([flight_data['UTMx'].to_numpy() - flight_data['UTMx'].mean(),
                flight_data['UTMy'].to_numpy() - flight_data['UTMy'].mean(),
                flight_data['ALT'].to_numpy() - flight_data['ALT'].mean(),])
pos = pos.T
data = flight_data['dexcess'].to_numpy()

#%%
def distance_matrix(pos):
    """
    Parameters
    ----------
    pos : numpy array of location in space
          THe dimension of the pos array must be
          elements on the rows (n), dimensions (m) on the comlumn. E.g.
          pos = numpy.array([x0, y0, z0], .. , [xn, yn, zn])

    Returns
    -------
    The euclidean distances on a n by n matrix.

    """
    import numpy as np
    # Number of elements in array
    elements = np.size(pos, 0)
    # Dimension of array (eg 2D or 3D)
    dim = np.size(pos, 1)
    dist_array = np.zeros((elements, elements))
    for e in range(elements):
        dist = 0
        for i in range(dim):
            dist += (np.repeat(pos[e,i], elements) - pos[:,i])**2
        dist = np.sqrt(dist)
        dist_array[:,e] = dist
    return dist_array
#%% Calculate distances
# Array with dimension >= 2
# Rows = elements
# Columns = dimensions
# Return the matrix of distances based on euclidean distance

# Compute delta matrix
dist_matrix = distance_matrix(pos)
prod = 0
denom = 0
S_0 = 0
for i in range (np.size(dist_matrix, 0)):
    position_of_interest = np.where(dist_matrix[:,i] == 0)[0][0]
    other_positions = np.arange(position_of_interest + 1, np.size(dist_matrix, 0))
    z_i = data[position_of_interest] - data.mean()
    denom += z_i**2 
    for j in other_positions:
        z_j = data[j] - data.mean()
        w_i_j = 1/dist_matrix[j, position_of_interest]
        prod += w_i_j * z_i * z_j
        S_0 += w_i_j
ratio = prod/denom
#%%
n = len(data)
MoranI = (n/S_0) * ratio

print(MoranI)
