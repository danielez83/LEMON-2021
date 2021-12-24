#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 12:08:35 2021

@author: daniele
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from FARLAB_standards import standard

from lmfit import Model
from lmfit.lineshapes import exponential, powerlaw
from lmfit.models import ExpressionModel


#%% Fit GLW d18O

GLW20210919 = pd.read_pickle('GLW_20210919_extended.pkl')
GLW20210920 = pd.read_pickle('GLW_20210920_extended.pkl')
temp_df = pd.concat((GLW20210919, GLW20210920))
temp_df = temp_df.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()
YVar = temp_df['d18O_mean'].to_numpy()


mod = ExpressionModel('offset + amplitude * x**exponent')
result_GLW = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)

r_squared = 1 - result_GLW.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_GLW.eval(x = x_pred)

sampling_point_GLW = np.mean(YVar)

#%% Fit FINSE d18O
FIN20210921 = pd.read_pickle('FINSE_20210921_extended.pkl')
temp_df = FIN20210921.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy()

mod = ExpressionModel('offset + amplitude * x**exponent')
result_FIN = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)


r_squared = 1 - result_FIN.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_FIN.eval(x = x_pred)

sampling_point_FIN = np.mean(YVar)
    
#%% Fit BERMUDA d18O
BER20210919 = pd.read_pickle('BER_20210919_extended.pkl')
temp_df = BER20210919.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy()

mod = ExpressionModel('offset + amplitude * x**exponent')
result_BER = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
r_squared = 1 - result_BER.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_BER.eval(x = x_pred)

sampling_point_BER = np.mean(YVar)

#%% Make a new dataframe with parameters

