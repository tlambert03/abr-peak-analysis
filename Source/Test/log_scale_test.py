# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import numpy as np

plt.gcf().clear()
plt.xscale('log')
plt.xlim(2, 32)
plt.xticks([2, 4, 8, 16, 32])
plt.gca().xaxis.set_major_formatter(ticker.ScalarFormatter())