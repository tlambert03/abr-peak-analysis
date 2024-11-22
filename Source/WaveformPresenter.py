#!/usr/bin/env python
# vim: set fileencoding=utf-8

"""
Created: Sat 23 Jun 2007 12:18:30 PM
Modified: Wed 13 Feb 2008 02:47:16 PM
"""

import wx
from abrpanel import WaveformPlot 
from abrpanel import PointPlot
from peakdetect import find_np
from peakdetect import manual_np
from datatype import Point
from datatype import waveformpoint
from datatype import ABRDataType
from numpy import concatenate
from numpy import array
import numpy as np
import operator

from config import DefaultValueHolder
import filter_EPL_LabVIEW_ABRIO_File as peakio
from filter_EPL_LabVIEW_ABRIO_File import safeopen
#import wx.lib.pubsub as pubsub

from datatype import ThrSource

from kpy.kpy.optimize import smooth

#----------------------------------------------------------------------------

class WaveformPresenter(object):

    defaultscale = 7
    minscale = 1
    maxscale = 15

    def __init__(self, model, view, interactor, options=None):
        self._redrawflag = True
        self._plotupdate = True
        self.view = view
        self.plots = []
        self.N = False
        self.P = False
        self.showWork = False
        self.showIO = False
        self.ann = None
        interactor.Install(self, view)
        if model is not None:
            self.load(model, options)

    def load(self, model, options=None):
        self.options = options
        self.model = model
        if self.model.threshold is None:
            self.guess_p()
            if self.options is not None and self.options.nauto:
                self.guess_n()
        else:
            self.N = True
            self.P = True
        self.plots = [WaveformPlot(w, self.view.subplot) \
                for w in self.model.series]
        xMax = 8.5
        if self.model.dataType == ABRDataType.Clinical:
            xMax = 25
        self.view.subplot.axis(xmax=xMax)
        self.current = len(self.model.series)-1
        self.update_labels()

        # restore analysis if auto option is enabled and file exists        
        restore = DefaultValueHolder("PhysiologyNotebook", "autoRestore")
        restore.SetVariables(value=False)
        restore.InitFromConfig()
        if restore.value and peakio.have_stored_analysis((self.model)):
            self.restore()

    def delete(self):
        self.plots[self.current].remove()
        del self.plots[self.current]
        del self.model.series[self.current]
        self._plotupdate = True
        self.view.subplot.axis

    def save(self):
        if self.P and self.N:
            msg = peakio.save(self.model)
            self.view.GetTopLevelParent().SetStatusText(msg)
#            pubsub.Publisher().sendMessage("DATA SAVED")
        else:
            msg = "Please identify N1-5 before saving"
            wx.MessageBox(msg, "Error")
            
    def restore(self):
        msg, pind, nind, thr = peakio.restore_analysis(self.model)
        
        self.model.threshold = thr
        
        for k in range(pind.shape[0]):
            cur = self.model.series[k]
            for j in range(5):
                self.setpoint(cur, (Point.PEAK, j+1), pind[k, j])
                self.setpoint(cur, (Point.VALLEY, j+1), nind[k, j])

        self.view.GetTopLevelParent().SetStatusText(msg)
        
        self.N = True
        self._plotupdate = True

    def clear_analysis(self):
        self.model.threshold = None
        self.N = False
        for w in self.model.series:
            w.points = {}
        for p in self.plots:
            p.clear_points()


        self.guess_p()
            
        self.view.GetTopLevelParent().SetStatusText('')
        self._plotupdate = True


    def update(self):
        if self._plotupdate:
            self._plotupdate = False
            self._redrawflag = True
            
            for p in self.plots:
                p.update()
            #waveform = self.model.series[-1]
            #ymax = (((waveform.y.max()*self.scale + waveform.level)/5)+1)*5
            #self.view.subplot.axis(ymin=0, ymax=ymax, xmax=8.5)
            xMax = 8.5
            if self.model.dataType == ABRDataType.Clinical:
                xMax = self.model.Tmax
#                xMax = 25
            if self.model.dataType == ABRDataType.CFTS:
                xMax = self.model.Tmax
                
            self.view.subplot.axis(xmax=xMax)
            if self.ann != None:
                self.ann.remove()
                self.ann = None
                
            if not self.model.threshold is None:
                
                self.ann = self.view.subplot.annotate('', 
                                           xy=(0, self.model.threshold), xycoords='data',
                                           xytext=(-0.05*self.view.subplot.get_xlim()[1], self.model.threshold), textcoords=('data'),
                                           arrowprops=dict(facecolor='g', shrink=0.05, headlength=15))
                                           
                titleStr = "Threshold = {:.1f} dB SPL "
                if self.model.thresholdSource == ThrSource.Auto:
                    if self.model.best_fit_type == "power law (noisy)":
                        titleStr += "(auto. WARNING: noisy data, verify result.)"
                    else:
                        titleStr += "(auto)"
                else:
                   titleStr += "(manual)"
                   
                self.view.subplot.set_title(titleStr.format(self.model.threshold), loc='left')
            
            elif self.model.thresholdEstimationFailed:
                self.view.subplot.set_title("Automatic threshold estimation failed", loc='left')
            else:
                self.view.subplot.set_title('', loc='Left')
                
                
            if self.showWork or self.showIO:
                self.view.subplot.set_position([0.125, 0.5, 0.775, 0.4])
            else:
                self.view.subplot.set_position([0.125, 0.1, 0.775, 0.8])

            if self.showIO:
                self.plot_io()
            
            self.view.ccplot.set_visible(self.showWork)
            self.view.cctext.set_visible(self.showWork)
            self.view.ioplot.set_visible(self.showIO)
               
        if self._redrawflag:
            self._redrawflag = False
            self.view.canvas.draw()

    def get_current(self):
        try: return self._current
        except AttributeError: return -1

    def set_current(self, value):
        if value < 0 or value > len(self.model.series)-1: pass
        elif value == self.current: pass
        else:    
            self.iterator = None
            try: self.plots[self.current].current = False
            except IndexError: pass
            self.plots[value].current = True
            self._redrawflag = True
            self._current = value

    current = property(get_current, set_current, None, None)      

    def get_scale(self):
        try: return self._scale
        except AttributeError: return WaveformPresenter.defaultscale

    def set_scale(self, value):
        if value <= WaveformPresenter.minscale: pass
        elif value >= WaveformPresenter.maxscale: pass
        elif value == self.scale: pass
        else:
            self._scale = value
            for p in self.plots:
                p.scale = value
            self.view.set_ylabel(value)    
            self.update_labels()    
            self._redrawflag = True

    scale = property(get_scale, set_scale, None, None)      

    def update_labels(self):
        label = u'uV*%d + dB SPL' % self.scale
        if self.normalized:
            self.view.set_ylabel('normalized ' + label)
        else:
            self.view.set_ylabel(label)

    def get_normalized(self):
        try: return self._normalized
        except AttributeError: return False

    def set_normalized(self, value):
        if value == self.normalized: pass
        else:    
            for p in self.plots:
                p.normalized = value
            self._normalized = value
            self.update_labels()    
            self._plotupdate = True

    normalized = property(get_normalized, set_normalized, None, None)      

    def set_threshold(self):
        self.model.set_manual_threshold(self.model.series[self.current].level)
        self._plotupdate = True

    def get_toggle(self):
        try: return self._toggle[self.current]
        except AttributeError: 
            self._toggle = {}
        except KeyError:    
            pass
        return None

    def set_toggle(self, value):
        if value == self.toggle: pass
        else:
            self.iterator = None
            self.plots[self.current].toggle = value
            self._toggle[self.current] = value
            self._redrawflag = True
        
    toggle = property(get_toggle, set_toggle, None, None)

    def guess_p(self, start=None):
        minlatency = DefaultValueHolder('PhysiologyNotebook','minlatency')
        minlatency.SetVariables(value=float(1.0))
        minlatency.InitFromConfig()

        self.P = True
        if start is None:
            start = len(self.model.series)
            
        for i in reversed(range(start)):
            cur = self.model.series[i]
            if i == len(self.model.series)-1:
                p_indices = find_np(cur.fs, cur.y, min_latency=minlatency.value)
            else:
                prev = self.model.series[i+1]
                i_peaks = self.getindices(prev, Point.PEAK)
                a_peaks = prev.y[i_peaks]
                p_indices = find_np(cur.fs, cur.y, algorithm='seed',
                        seeds=list(zip(i_peaks, a_peaks)), nzc='noise_filtered') 

            for i,v in enumerate(p_indices):
                self.setpoint(cur, (Point.PEAK, i+1), v)

    def update_point(self):
        for i in reversed(range(self.current)):
            cur = self.model.series[i]
            index = self.model.series[i+1].points[self.toggle].index
            amplitude = self.model.series[i+1].y[index]
            if self.toggle[0] == Point.PEAK:
                index = find_np(cur.fs, cur.y, algorithm="seed", n=1,
                        seeds=[(index, amplitude)], nzc='noise_filtered')[0]
            else:    
                index = find_np(cur.fs, -cur.y, algorithm="seed", n=1,
                        seeds=[(index, amplitude)], nzc='noise_filtered')[0]
            self.setpoint(cur, self.toggle, index)
        self._plotupdate = True

    def guess_n(self, start=None):
        self.N = True
        if start is None:
            start = len(self.model.series)
        for i in reversed(range(start)):
            cur = self.model.series[i]
            p_indices = self.getindices(cur, Point.PEAK)
            bounds = concatenate((p_indices, array([len(cur.y)-1])))
            try:
                prev = self.model.series[i+1]
                i_valleys = self.getindices(prev, Point.VALLEY)
                a_valleys = prev.y[i_valleys]
                n_indices = find_np(cur.fs, -cur.y, algorithm='bound',
                        seeds=list(zip(i_valleys, a_valleys)), bounds=bounds,
                        bounded_algorithm='seed', dev=0.5) 
            except IndexError as e:
                n_indices = find_np(cur.fs, -cur.y, bounds=bounds,
                        algorithm='bound', bounded_algorithm='y_fun', dev=0.5)
            for i,v in enumerate(n_indices):
                self.setpoint(cur, (Point.VALLEY, i+1), v)
        self._plotupdate = True

    def invert(self):
        self.model.invert()
        self.guess_p()
        for p in self.plots:
            p.invert()
        self._plotupdate = True

    def estimate_threshold(self):
        wx.Cursor(wx.StockCursor(wx.CURSOR_WAIT))
        self.model.estimate_threshold()
        self.plot_threshold_estimation_work()
        self._plotupdate = True
        wx.Cursor(wx.StockCursor(wx.CURSOR_DEFAULT))

    def plot_threshold_estimation_work(self):
        cc, level = self.model.get_corrcoefs()
#        cc_smooth = smooth(cc, 3)

        p2 = self.model.power2_result
        sig = self.model.sigmoid_result                
        
        self.view.ccplot.plot(level, cc, 'ko')   
#        self.view.ccplot.plot(level, cc, 'ko', color='#d8dcd6')   
#        self.view.ccplot.plot(level, cc_smooth, 'ko')   
        self.view.ccplot.plot(p2.x, p2.yfit, 'r-')
        self.view.ccplot.plot(level, sig.yfit, 'b-')
        self.view.ccplot.autoscale(False)
        thr = self.model.threshold
        crit = self.model.thresholdCriterion
        self.view.ccplot.plot(np.array([level[0], thr]), np.array([crit, crit]), 'k:')
        self.view.ccplot.plot(np.array([thr, thr]), np.array([crit, self.view.ccplot.get_ylim()[0]]), 'k:')

        self.view.ccplot.set_xlim(np.min(level)-5, np.max(level)+5)

        self.view.cctext.annotate('power2\nSSE = {:.4f}\nR2 = {:.4f}\nadjR2 = {:.4f}'.format(p2.stats.sse, p2.stats.r2, p2.stats.adj_r2),
                     xy=(0,1), xycoords=('axes fraction'), 
                     color='red', va='top')

        self.view.cctext.annotate('sigmoid\nSSE = {:.4f}\nR2 = {:.4f}\nadjR2 = {:.4f}\nslope = {:.3f}'.format(sig.stats.sse, sig.stats.r2, sig.stats.adj_r2, sig.param[1]),
                     xy=(0,0), xycoords=('axes fraction'), 
                     color='blue', va='bottom')

    def plot_io(self):
        ymax = 0
        level = np.array([w.level for w in self.model.series])
        for k in range(5):
            y = np.array([w.points[(Point.PEAK, k+1)].amplitude for w in self.model.series]) 
            ymax = np.max((ymax, y.max()))
            self.view.ioplot.plot(level, y, '-', color=PointPlot.COLORS[k])
            
        for k in range(len(self.model.randomPeaks)):
            p = self.model.randomPeaks[k]
            self.view.ioplot.plot(level[k]*np.ones(len(p)), p, 'o', color='k', markersize=4)
        
        self.view.ioplot.plot((np.min(level)-5, np.max(level)+5), self.model.noiseFloor*np.ones(2), '-', color='k')
        
        self.view.ioplot.set_xlim(np.min(level)-5, np.max(level)+5)
        self.view.ioplot.set_ylim(0, ymax * 1.05)
        

    def toggle_show_work(self):
        self.showWork = not self.showWork and self.model.auto_thresholded
        self.showIO = self.showIO and not self.showWork
        self._plotupdate = True

    def toggle_show_io(self):
        self.showIO = not self.showIO
        self.showWork = self.showWork and not self.showIO
        self._plotupdate = True

        
    def setpoint(self, waveform, point, index):
        if not hasattr(waveform, 'points'):
            setattr(waveform, 'points', {})
        try:
            waveform.points[point].index = index
        except KeyError:
            waveform.points[point] = waveformpoint(waveform, index, point)
        self._redrawflag = True

    def getindices(self, waveform, point):
        points = [(v.point[1], v.index) for v in \
                waveform.points.values() if v.point[0] == point]
        points.sort(key=operator.itemgetter(0))
        return [p for i,p in points]

    def get_iterator(self):
        try:
            if self._iterator[self.current] is not None:
                return self._iterator[self.current]
        except AttributeError:
            self._iterator = {}
        except KeyError:
            pass
        if self.toggle is not None:
            waveform = self.model.series[self.current]
            start_index = waveform.points[self.toggle].index
            if self.toggle[0] == Point.PEAK:
                iterator = manual_np(waveform.fs, waveform.y, start_index)
            else:    
                iterator = manual_np(waveform.fs, -waveform.y, start_index)
            next(iterator)
#            iterator.next()
            self._iterator[self.current] = iterator
            return self._iterator[self.current]    
        else:
            return None

    def set_iterator(self, value):
        try:
            self._iterator[self.current] = value
        except AttributeError:
            self._iterator = {}
            self._iterator[self.current] = value

    iterator = property(get_iterator, set_iterator, None, None)

    def move(self, step):
        if self.toggle is None:
            return
        else:
            waveform = self.model.series[self.current]
            waveform.points[self.toggle].index = self.iterator.send(step)
            self.plots[self.current].points[self.toggle].update()
            self._redrawflag = True

    def export(self):
        extension = DefaultValueHolder("PhysiologyNotebook", "extension")
        extension.SetVariables(value='txt')
        extension.InitFromConfig()

        #Prepare spreadsheet
        series = self.model.series

        header = 'Time (ms)\t' + '\t'.join(['{} dB'.format(w.level) for w in series]) + '\n'
        
        data = np.array([np.array(w.y) for w in series])
        data = np.vstack((series[0].x, data))
        
        spreadsheet = '\n'.join('\t'.join('%f' %x for x in y) for y in np.transpose(data))
#        for k = 1 to series.length:
#            spreadsheet += series[k].y(1) + '\t'
    
    
        filename = self.model.filename + '-filtered.' + extension.value

        f = safeopen(filename)
        f.writelines(header + spreadsheet)
        f.close()

        msg = 'Exported filtered waveforms to %s' % filename
        self.view.GetTopLevelParent().SetStatusText(msg)
    
        
