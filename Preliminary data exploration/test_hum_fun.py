#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 22:20:04 2021

@author: daniele
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from FARLAB_standards import standard

from hum_corr_fun import hum_corr_fun

#%%
GLW20210919 = pd.read_pickle('GLW_20210919_extended.pkl')
GLW20210920 = pd.read_pickle('GLW_20210920_extended.pkl')

temp_df = pd.concat((GLW20210919, GLW20210920))
temp_df = temp_df.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

# YVar = temp_df['d18O_mean'].to_numpy() - standard('GLW', 'd18O')
YVar18 = temp_df['d18O_mean'].to_numpy()
YVarcorr18 = hum_corr_fun(XVar, YVar18, 18, 15000, 'mean')

YVar2 = temp_df['dD_mean'].to_numpy()
YVarcorr2 = hum_corr_fun(XVar, YVar2, 2, 15000, 'mean')

#%%
FIN20210921 = pd.read_pickle('FINSE_20210921_extended.pkl')
temp_df = FIN20210921.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()
YVar = temp_df['d18O_mean'].to_numpy()

YVar18 = temp_df['d18O_mean'].to_numpy()
YVarcorr18 = hum_corr_fun(XVar, YVar18, 18, 15000, 'mean')

YVar2 = temp_df['dD_mean'].to_numpy()
YVarcorr2 = hum_corr_fun(XVar, YVar2, 2, 15000, 'mean')