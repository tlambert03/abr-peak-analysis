from collections import namedtuple
import numpy as np

def fitstats(ydata, yfit, npar):
    resid = yfit - ydata
    sse = np.sum(resid**2)
    sstot = np.sum((ydata-ydata.mean())**2)
    r2 = 1 - sse/sstot
    
    n = len(ydata)
    k = npar - 1
    adj_r2 = 1 - (((1-r2)*(n-1)) / (n - k - 1))
    
    return namedtuple('stats', 'sse,r2,adj_r2')(sse,r2,adj_r2)

def smooth(y, n):
    y = np.append(y[0], y)
    y = np.append(y, y[-1])
    w = np.ones(n) / n
    y = np.convolve(y, w, 'same')
    return y[1:-1]
