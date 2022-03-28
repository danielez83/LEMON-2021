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

import pysal

from scipy import signal

from pyproj import Proj

#%% Configuration
data_filename            = '../PKL final data/flight_04.pkl'


display                     = 'raw' #'raw', 'binned'
bin_mode                    = 'manual' #'auto', 'manual'
bins                        = np.arange(400, 20000, 50)


#%% Load data
with open(data_filename, 'rb') as f:
    flight_data, metadata = pickle.load(f)

#flight_data = flight_data[flight_data['ALT'] < 1000]
    
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
data = flight_data['dD'].to_numpy()

#%%
def distance_matrix(pos):
    """
    Compute euclidean distances matrix.
    
    Parameters
    ----------
    pos : numpy array of location in space
          THe dimension of the pos array must be
          elements on the rows (n), dimensions (m) on the comlumn. E.g.
          pos = numpy.array([x0, y0, z0], .. , [xn, yn, zn])

    Returns
    -------
    The euclidean distances (n x n) matrix.

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
def MoranI(pos, field):
    """
    Compute Moran I spatial autocorrelation index based on a 2D or 3D dataset.
    
    Parameters
    ----------
    pos : numpy array of location in space
          THe dimension of the pos array must be
          elements on the rows (n), dimensions (m) on the comlumn. E.g.
          pos = numpy.array([x0, y0, z0], .. , [xn, yn, zn])
    field : numpy array with field associated to position. Same number of rows 
            of pos array. E.g. T =  numpy.array([T0, ..., Tn])
    Returns
    Moran I index (-1, 1 if input is standardized) and significance as p-value
    (pval, MoranI)
    -------
    - Determine the feasibility of using a particular statistical method 
      (for example, linear regression analysis and many other statistical techniques 
      require independent observations).
    - Help identify an appropriate neighborhood distance for a variety of 
      spatial analysis methods. For example, find the distance where spatial autocorrelation 
      is strongest.



    More info on Moran I 
    https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-statistics/h-how-spatial-autocorrelation-moran-s-i-spatial-st.htm
    Moran I in 3D
    Marwan, N., Saparin, P., & Kurths, J. (2007). 
    Measures of complexity for 3D image analysis of trabecular bone. 
    European Physical Journal: Special Topics, 143(1), 109–116. https://doi.org/10.1140/epjst/e2007-00078-x
    
    http://lixuworld.blogspot.com/2016/03/matlab-global-morans-i.html
    """
    
    # Compute delta matrix
    dist_matrix = distance_matrix(pos)
    # Preallocate memory for sum computation
    prod        = 0 # For Moran I
    denom       = 0 # For Moran I
    S_0         = 0 # For Moran I
    z_i_squared = 0 # For Z-Score
    z_i_pow4    = 0 # For Z-Score
    for i in range (np.size(dist_matrix, 0)):
        position_of_interest = np.where(dist_matrix[:,i] == 0)[0][0]
        other_positions = np.arange(position_of_interest + 1, np.size(dist_matrix, 0))
        # Compute deviation from the mean for i-th element
        z_i = data[position_of_interest] - data.mean()
        z_i_squared += z_i**2
        z_i_pow4 += z_i**4
        denom += z_i**2 
        for j in other_positions:
            # Compute deviation from the mean for j-th element
            z_j = data[j] - data.mean()
            # Compute weigths (inverse of euclidean distance)
            w_i_j = 1/dist_matrix[j, position_of_interest]
            prod += w_i_j * z_i * z_j
            S_0 += w_i_j
    ratio = prod/denom
    n = len(data)
    # Calculate Moran I index
    MoranI = (n/S_0) * ratio
    # Z-Score
    expectation = -1/(n-1)
    #---------------------
    #A = n((N**2 - 3*n + 3))
    
    
    
    return MoranI

#%%
#w=pysal.lib.weights.Voronoi(pos)
#pysal_MoranI = pysal.explore.esda.Moran(data, w)
print(MoranI(pos, data))
