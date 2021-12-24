#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 22:24:15 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import netCDF4 as nc
#from scipy.stats import linregress

from hum_corr_fun import hum_corr_fun_v2 as hum_corr_fun

#%% 
for i in range(-300, -100, 10):
    print(i, hum_corr_fun(1000, i, 2, 20000, 'mean'))
#%%
start_val = -18
for i in range(10):
    old_val = start_val
    start_val = (hum_corr_fun(10000, start_val, 18, 20000, 'FINSE'))
    print(start_val)
    print(start_val - old_val)