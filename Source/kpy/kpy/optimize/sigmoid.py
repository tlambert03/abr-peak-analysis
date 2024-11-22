# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 20:29:24 2018

@author: Ken
"""
import collections
import numpy as np
from scipy.optimize import curve_fit

from . import fitstats

def _compute_params(x, y, b, c):
    u = 1 / (1 + 10**(b*(c-x)))
    
    num = np.vstack((u, np.ones(x.size))).transpose()
    lincoeffs = np.linalg.lstsq(num, y, rcond=1)[0]
    a = lincoeffs[0]
    d = lincoeffs[1]
    return a, b, c, d

def make_model(y):
    def model(x, b, c):
        a,b,c,d = _compute_params(x, y, b, c)
        return evaluate(x, a, b, c, d)
    return model

def evaluate(x, a, b, c, d):
    return a / (1 + 10**(b*(c-x))) + d;

def inverse(y, a, b, c, d):
    if a/(y-d) <= 1:
        return float('NaN')
    
    return c - 1/b * np.log10(a/(y-d) - 1)
    
def initial_guess(x, y):
    a = np.max(y)
    xh = np.mean(x)
    b = (a - np.min(y)) / (np.max(x) - np.min(x)) * 4 / (a * np.log(10))
    c = xh  
    return np.array([b, c])

def fit(x,y): 
    Pinit = initial_guess(x, y)
    
    try:
        P, pcov = curve_fit(make_model(y), x, y, p0=Pinit, method='trf', max_nfev=10000)
    except (RuntimeError):
        P = Pinit
        
    a,b,c,d = _compute_params(x, y, *P)
    if a < 0:
#        print('flipping sigmoid parameters')
        b = -b
        d = d + a
        a = -a
    
    yfit = evaluate(x, a, b, c, d);
    
    stats = fitstats(y, yfit, 4)
    
    return collections.namedtuple('result', 'param,x,yfit,stats')(np.array([a,b,c,d]),x,yfit,stats)

