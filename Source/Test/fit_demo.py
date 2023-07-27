# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 15:56:32 2018

@author: Ken
"""

import matplotlib.pyplot as plt

import os
import sys
import numpy as np
sys.path.append(os.path.relpath("../"))
import datafile
#from datafile import loadabr

from kpy.optimize import power2, logistic


fn = 'D:\Data\ABR exemplars\ABR-102-1'
abr = datafile.loadabr(fn)
y, x = abr.get_corrcoefs()

#x = np.linspace(1, 10, 10)
#y = power2.evaluate(x, 1, 2, 0)
#np.random.seed(1729)
#y_noise = 2.5 * np.random.normal(size=x.size)
#y = y + y_noise

popt = power2.fit(x, y)
p2fit = power2.evaluate(x, *popt)

popt = logistic.fit(x, y)
logfit = logistic.evaluate(x, *popt)

plt.gcf().clear()
plt.plot(x, y, 'bo')   
plt.plot(x, p2fit, 'r-')
plt.plot(x, logfit, 'm-')

