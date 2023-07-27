# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:21:35 2022

@author: kehan
"""

from numpy import array
import re

fname = 'D:\Development\ABR Peak Analysis\Sample Data\FBN_35_COCH_EXT_LEFT_12K.txt'

with open(fname) as f:
    data = f.read()
    
    
    levelStr = re.compile('Intensity:([\d,]+)').search(data).group(1)
    levelList = re.compile(',+([\d]+)').findall(levelStr)
    levels = [float(x) for x in levelList]
    
    dtStr = re.compile('Smp. Period:([\d\.,]+)').search(data).group(1)
    dtList = re.compile(',+([\d\.]+)').findall(dtStr)
    dt = [float(x) for x in dtList]
    
    freqStr = re.compile('Stim. Freq.([\d,]+)').search(data).group(1)
    freqList = re.compile(',+([\d]+)').findall(freqStr)
    freqs = [float(x) for x in freqList]
    
    dataStr = data.split('Data Pnt')[1].split('\n', 1)[1]
    a = array(dataStr.replace(',', ' ').split()).astype(float)
    numCols = len(levels) * 6 + 1
    y = a.reshape(int(len(a) / numCols), numCols).T
    y = y[2::6,:]
    
    

    
    


