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

GLW20210919 = pd.read_pickle('GLW_20210919_extended.pkl')
GLW20210920 = pd.read_pickle('GLW_20210920_extended.pkl')

temp_df = pd.concat((GLW20210919, GLW20210920))
temp_df = temp_df.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy() - standard('GLW', 'd18O')

mod = ExpressionModel('offset + amplitude * x**exponent')
result_GLW = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
r_squared = 1 - result_GLW.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_GLW.eval(x = x_pred)

# Plot curve
fig, ax = plt.subplots()
ax.plot(XVar, YVar, 'ko')
# ax.plot(XVar, result.init_fit, 'k--', label='initial fit')
# ax.plot(XVar, result.best_fit, 'r--', label='best fit')
ax.plot(x_pred, y_pred, 'r--', label='best fit')
ax.legend(loc='best')
buff_text = ("R$^2$=%.2f" % r_squared)
ax.text(15000, 4, buff_text)
ax.set(ylabel = '$\delta^{18}$O obs-std [‰]', xlabel = 'H$_2$O [ppm]')
ax.grid()
# Print best fit parameters
print('Best fit result ----------------')
for j in result_GLW.best_values:
    print(j, '= ', result_GLW.best_values[j])
print('--------------------------------')
#%%
FIN20210921 = pd.read_pickle('FINSE_20210921_extended.pkl')
temp_df = FIN20210921.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy() - standard('FINSE', 'd18O')

mod = ExpressionModel('offset + amplitude * x**exponent')
result_FIN = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
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
ax.text(15000, 1, buff_text)
ax.set(ylabel = '$\delta^{18}$O obs-std [‰]', xlabel = 'H$_2$O [ppm]')
ax.grid()
# Print best fit parameters
print('Best fit result ----------------')
for j in result_FIN.best_values:
    print(j, '= ', result_FIN.best_values[j])
print('--------------------------------')

#%% Fit BERMUDA d18O
BER20210919 = pd.read_pickle('BER_20210919_extended.pkl')
temp_df = BER20210919.sort_values(by = ['H2O'])

XVar = temp_df['H2O'].to_numpy()

YVar = temp_df['d18O_mean'].to_numpy() - standard('BER', 'd18O')

mod = ExpressionModel('offset + amplitude * x**exponent')
result_BER = mod.fit(YVar, x=XVar, offset = 4, amplitude = 1, exponent = 1)
r_squared = 1 - result_BER.residual.var() / np.var(YVar)
x_pred = np.linspace(1000, 20000)
y_pred = result_BER.eval(x = x_pred)

# Plot curve
fig, ax = plt.subplots()
ax.plot(XVar, YVar, 'ko')
# ax.plot(XVar, result.init_fit, 'k--', label='initial fit')
# ax.plot(XVar, result.best_fit, 'r--', label='best fit')
ax.plot(x_pred, y_pred, 'r--', label='best fit')
ax.legend(loc='best')
buff_text = ("R$^2$=%.2f" % r_squared)
ax.text(15000, -.6, buff_text)
ax.set(ylabel = '$\delta^{18}$O obs-std [‰]', xlabel = 'H$_2$O [ppm]')
ax.grid()
# Print best fit parameters
print('Best fit result ----------------')
for j in result_BER.best_values:
    print(j, '= ', result_BER.best_values[j])
print('--------------------------------')

#%% Single Plot with all standards
fig, ax = plt.subplots(figsize=(15,10))

# DATA FIRST
# BERMUDA
ax.errorbar(BER20210919['H2O'], BER20210919['d18O_mean']-standard('BER', 'd18O'), 
           BER20210919['d18O_err'], fmt = 'D', ms = 8, c='#001146')
# FINSE
ax.errorbar(FIN20210921['H2O'], FIN20210921['d18O_mean']-standard('FINSE', 'd18O'), 
           FIN20210921['d18O_err'], fmt = 'o', ms = 8, c='#0165fc')
# GLW
ax.errorbar(GLW20210919['H2O'], GLW20210919['d18O_mean']-standard('GLW', 'd18O'), 
           GLW20210919['d18O_err'], fmt = '^', ms = 8, c='#95d0fc')
ax.errorbar(GLW20210920['H2O'], GLW20210920['d18O_mean']-standard('GLW', 'd18O'), 
           GLW20210920['d18O_err'], fmt = '^', ms = 8, c='#95d0fc')

# Graphics
ax.set_xlabel('H$_2$O [ppm]', fontsize=24)
ax.set_ylabel('$\delta^{18}$O obs-std [‰]', fontsize=24)
plt.xticks(np.arange(0, 21000, step = 2500))
ax.tick_params(axis='both', which='major', labelsize=20)
ax.legend(['Bermuda','Finse','GLW'], fontsize=16)
ax.grid()

# BERMUDA FIT
x_pred = np.linspace(1000, 20000)
y_pred = result_BER.eval(x = x_pred)
ax.plot(x_pred, y_pred, 'r--', label='best fit')

# FINSE FIT
x_pred = np.linspace(1000, 20000)
y_pred = result_FIN.eval(x = x_pred)
ax.plot(x_pred, y_pred, 'r--', label='best fit')

# GLW FIT
x_pred = np.linspace(1000, 20000)
y_pred = result_GLW.eval(x = x_pred)
ax.plot(x_pred, y_pred, 'r--', label='best fit')



    