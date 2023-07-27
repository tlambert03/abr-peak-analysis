# -*- coding: utf-8 -*-

import matplotlib.cm as cm
import matplotlib.ticker as ticker
import numpy as np


#----------------------------------------------------------------------------

class AudiogramPresenter(object):

    def __init__(self, model, view, interactor, options=None):
        self._redrawflag = True
        self._plotupdate = True
        self.view = view
        interactor.Install(self, view)
        if model is not None:
            self.load(model, options)

    def load(self, model, options=None):
        self.options = options
        self.model = model

    def save(self):
        msg = self.model.save()
        self.view.GetTopLevelParent().SetStatusText(msg)

    def update(self):
        if self._plotupdate:
            self._plotupdate = False
            self._redrawflag = True
            
            self.view.subplot.plot(self.model.freqs, self.model.thresholds, 'b-')   
            
            colors = [cm.jet(x) for x in np.linspace(0, 1, len(self.model.freqs))]

            for idx in range(len(self.model.freqs)):
                self.view.subplot.plot(self.model.freqs[idx], self.model.thresholds[idx], 'bo', color=colors[idx])   
                

            self.view.subplot.axis(ymin=self.model.minLevel, ymax=self.model.maxLevel)
            self.view.subplot.set_xscale('log')
            
            xmin = np.min(self.model.freqs) / 2**0.5
            xmax = np.max(self.model.freqs) * 2**0.5
            
            kt_min = np.round(np.log2(xmin))            
            kt_max = np.round(np.log2(xmax))            
            xt = 2 ** np.arange(kt_min, kt_max+1)            
            
            self.view.subplot.set_xlim(xmin, xmax)
            self.view.subplot.set_xticks(xt)
            self.view.subplot.xaxis.set_major_formatter(ticker.ScalarFormatter())            
            self.view.subplot.xaxis.set_minor_formatter(ticker.NullFormatter())            
            self.view.subplot.xaxis.set_minor_locator(ticker.LogLocator(base=2, subs=(np.sqrt(2),)))

            idx = 0
            for l,c in zip(self.model.levels, self.model.fits):
                self.view.ccplot.plot(l, c, 'k-', color=colors[idx])
                idx = idx  +1

            self.view.ccplot.plot(np.array([self.model.minLevel, self.model.maxLevel]), np.array([0.35, 0.35]), 'k:')
            self.view.ccplot.axis(xmin=self.model.minLevel, xmax=self.model.maxLevel)

        if self._redrawflag:
            self._redrawflag = False
            self.view.canvas.draw()

