#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 21:52:53 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import datetime

#%%
acc_data = pd.read_csv('../Accelerometer/2021-09-2017.59.12.csv')
time = pd.to_datetime(acc_data['time'], format = '%H:%M:%S:%f')
acc_data.drop('time', axis = 1, inplace = True)

acc_data['ax (m/s^2)'].iloc[:2000].plot()