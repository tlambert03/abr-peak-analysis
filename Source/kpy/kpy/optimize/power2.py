# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:55:35 2018

@author: HANCOCK
"""
import collections
import numpy as np
from scipy.optimize import curve_fit
from kpy.optimize import fitstats

def _compute_params(x, y, b):
    num = np.vstack((x**b, np.ones(x.size))).transpose()
    lincoeffs = np.linalg.lstsq(num, y, rcond=1)[0]
    a = lincoeffs[0]
    c = lincoeffs[1]
    return a, b, c

def make_model(y):
    def model(x, b):
        a,b,c = _compute_params(x, y, b)
        return evaluate(x, a, b, c)
    return model

def evaluate(x, a, b, c):
    return a * x**b + c;

def inverse(y, a, b, c):
    return ((y-c) / a) ** (1/b)
    
def initial_guess(x, y):
    idx = (x>0) & (y>0)
    x = x[idx]
    y = y[idx]        
    
    # Compute the value of |b| by assuming all data is from the same power
    # function.
    b = np.mean( np.log( y[0]/y[1:] ) / np.log( x[0]/x[1:] ) );

    return b

def fit(x,y): 

    if np.min(x) == 0:
        offset = 1
    elif np.min(x) < 0:
        offset = -np.min(x)
    else:
        offset = 0

    xp = x + offset    
    yp = y
#    idx = (x>0)
#    xp = x[idx]
#    yp = y[idx]        
    
    b_init = initial_guess(xp, yp)
    try:
        b, pcov = curve_fit(make_model(yp), xp, yp, p0=b_init, method='trf', max_nfev=10000)
    except (RuntimeError):
        b = b_init
    
    param = _compute_params(xp, yp, *b)
    yfit = evaluate(xp, *param)
    stats = fitstats(yp, yfit, 3)
    
    return collections.namedtuple('result', 'param,x,xoff,yfit,stats')(param,x,offset,yfit,stats)

