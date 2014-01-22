import pyqtgraph as pg
import numpy as np

class rasterTick(pg.PlotDataItem):
    def __init__(self, toe, trial_number):
        super(rasterTick,self).__init__()
        x = (toe, toe)
        y = (trial_number - .5, trial_number + .5)
        self.setData(x, y)

class rasterPlot(pg.PlotItem):
    def __init__(self, toes):
        super(rasterPlot, self).__init__()
        if not isinstance(toes, np.ndarray) or toes.ndim > 2:
            raise ValueError('Event times must be given as ndarray of dimension 2 or less')
        elif toes.ndim == 1:
            toes.reshape((1,toes.size))

        for idx, t in enumerate(toes):
            rasterTick(t, idx)
            self.addItem(rasterTick(t, idx))

        self.ntrials = toes.shape[0]


    def add_trials(self, toes):
        for idx, t in enumerate(toes):
            self.addItem(rasterTick(t, self.ntrials + idx))

        self.ntrials += toes.shape[0]
        

