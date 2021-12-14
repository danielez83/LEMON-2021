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



#%%
FIN20210921 = pd.read_pickle('WIFVOSdfBermudaCali.pkl')
temp_df = FIN20210921.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

#YVar = temp_df['d18O_mean'].to_numpy() - standard('FINSE', 'd18O')
YVar = temp_df['d18O'].to_numpy() - standard('FINSE', 'd18O')
#YVar = ((temp_df['d18O_mean']/1000)+1)*(2005.20e-6)

#mod = ExpressionModel('offset + amplitude * x**exponent')
#result_FIN = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
mod = ExpressionModel('off + a*exp(b*x)')
result_FIN = mod.fit(YVar, x=XVar, off = 0, a = 1, b = -1e-3)


# Yongbiao Model --------------------------------------
# mod = ExpressionModel('a/x + b*x + c')
# result_FIN = mod.fit(YVar, x=XVar, a = 0, b = 1, c = 1)
# -----------------------------------------------------

r_squared = 1 - result_FIN.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_FIN.eval(x = x_pred)

# Plot curve
fig, ax = plt.subplots()
ax.plot(XVar, YVar, 'ko')
# ax.plot(XVar, result.init_fit, 'k--', label='initial fit')
# ax.plot(XVar, result.best_fit, 'r--', label='best fit')
ax.plot(x_pred, y_pred, 'r--', label='best fit')
ax.legend(loc='best')
buff_text = ("R$^2$=%.2f" % r_squared)
#ax.text(15000, 1, buff_text)
ax.set(ylabel = '$\delta^{18}$O obs-std [‰]', xlabel = 'H$_2$O [ppm]')
ax.grid()
# Print best fit parameters
print('Best fit result ----------------')
for j in result_FIN.best_values:
    print(j, '= ', result_FIN.best_values[j])
print("Mean ± 1std d18O observed: %.2f±%.2f" % ( 
      np.mean(temp_df['d18O']), 
      np.std(temp_df['d18O'], ddof=1)))
print('--------------------------------')

#%%
XVar = temp_df['H2O'].to_numpy()

#YVar = temp_df['d18O_mean'].to_numpy() - standard('FINSE', 'd18O')
YVar = temp_df['dD'].to_numpy() - standard('FINSE', 'dD')
#YVar = ((temp_df['d18O_mean']/1000)+1)*(2005.20e-6)

#mod = ExpressionModel('offset + amplitude * x**exponent')
#result_FIN = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
mod = ExpressionModel('off + a*exp(b*x)')
result_FIN = mod.fit(YVar, x=XVar, off = 0, a = -1, b = 1e-4)


# Yongbiao Model --------------------------------------
# mod = ExpressionModel('a/x + b*x + c')
# result_FIN = mod.fit(YVar, x=XVar, a = 0, b = 1, c = 1)
# -----------------------------------------------------

r_squared = 1 - result_FIN.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_FIN.eval(x = x_pred)

# Plot curve
fig, ax = plt.subplots()
ax.plot(XVar, YVar, 'ko')
# ax.plot(XVar, result.init_fit, 'k--', label='initial fit')
# ax.plot(XVar, result.best_fit, 'r--', label='best fit')
ax.plot(x_pred, y_pred, 'r--', label='best fit')
ax.legend(loc='best')
buff_text = ("R$^2$=%.2f" % r_squared)
#ax.text(15000, 1, buff_text)
ax.set(ylabel = '$\deltaD obs-std [‰]', xlabel = 'H$_2$O [ppm]')
ax.grid()
# Print best fit parameters
print('Best fit result ----------------')
for j in result_FIN.best_values:
    print(j, '= ', result_FIN.best_values[j])
print("Mean ± 1std d18O observed: %.2f±%.2f" % ( 
      np.mean(temp_df['dD']), 
      np.std(temp_df['dD'], ddof=1)))
print('--------------------------------')

