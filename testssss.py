#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 21:51:20 2022

@author: daniele
"""

#%%
import numpy as np
Y = complex(2, 3)
X = complex(4, 5)

print("Division is :", Y/X)
print("Real: ", (Y.real*X.real+Y.imag*X.imag)/(X.real**2 + X.imag**2))