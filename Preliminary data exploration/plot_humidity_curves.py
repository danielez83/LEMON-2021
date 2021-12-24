#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  3 23:01:01 2021

@author: daniele
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from FARLAB_standards import standard


BER20210919 = pd.read_pickle('BER_20210919.pkl')
GLW20210919 = pd.read_pickle('GLW_20210919.pkl')
GLW20210920 = pd.read_pickle('GLW_20210920.pkl')
FIN20210921 = pd.read_pickle('FINSE_20210921.pkl')

#%% d18O
fig, ax = plt.subplots()
ax.scatter(BER20210919['H2O'], BER20210919['d18O_mean'] - standard('BER', 'd18O'))
ax.scatter(GLW20210919['H2O'], GLW20210919['d18O_mean'] - standard('GLW', 'd18O'))
ax.scatter(GLW20210920['H2O'], GLW20210920['d18O_mean'] - standard('GLW', 'd18O'))
ax.scatter(FIN20210921['H2O'], FIN20210921['d18O_mean'] - standard('FINSE', 'd18O'))
ax.legend(['BER_20210919', 'GLW20210919', 'GLW20210920', 'FIN20210921'])
ax.set(ylabel = '$\delta^{18}$O meas-std [‰]', xlabel = 'H$_{2}$O [ppm]')
ax.grid()
#%% dD
fig, ax = plt.subplots()
ax.scatter(BER20210919['H2O'], BER20210919['dD_mean'] - standard('BER', 'dD'))
ax.scatter(GLW20210919['H2O'], GLW20210919['dD_mean'] - standard('GLW', 'dD'))
ax.scatter(GLW20210920['H2O'], GLW20210920['dD_mean'] - standard('GLW', 'dD'))
ax.scatter(FIN20210921['H2O'], FIN20210921['dD_mean'] - standard('FINSE', 'dD'))
ax.legend(['BER_20210919', 'GLW20210919', 'GLW20210920', 'FIN20210921'])
