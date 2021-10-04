#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 08:51:45 2021

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

GLW20210919 = pd.read_pickle('GLW_20210919.pkl')
GLW20210920 = pd.read_pickle('GLW_20210920.pkl')

temp_df = pd.concat((GLW20210919, GLW20210920))
temp_df = temp_df.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy() - standard('GLW', 'd18O')

mod = ExpressionModel('offset + amplitude * x**exponent')
result = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
r_squared = 1 - result.residual.var() / np.var(YVar)

fig, ax = plt.subplots()
ax.plot(XVar, YVar, 'bo')
# ax.plot(XVar, result.init_fit, 'k--', label='initial fit')
ax.plot(XVar, result.best_fit, 'r--', label='best fit')
ax.legend(loc='best')
buff_text = ("R$^2$=%.2f" % r_squared)
ax.text(15000, 4, buff_text)

#%% the rest

BER20210919 = pd.read_pickle('BER_20210919.pkl')
FIN20210921 = pd.read_pickle('FINSE_20210921.pkl')
    