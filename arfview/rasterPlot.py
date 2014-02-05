import pyqtgraph as pg
import numpy as np

class rasterTick(pg.PlotDataItem):
    def __init__(self, toe, trial_number):
        super(rasterTick,self).__init__()
        x = (toe, toe)
        y = (trial_number - .5, trial_number + .5)
        self.setData(x, y)

class rasterPlot(pg.PlotItem):
    def __init__(self, toes, *args, **kwargs):
        super(rasterPlot, self).__init__(*args,**kwargs)
        # if not isinstance(toes, list) or toes.ndim > 1:
        #     raise ValueError('Event times must be given as ndarray of dimension 2 or less')

        self.ntrials = 0
        for idx,trial_toes in enumerate(toes):
            self.add_trial(trial_toes)

        self.setMouseEnabled(y=False)

    def add_trial(self, toes):
        self.ntrials += 1
        for idx, t in enumerate(toes):
            self.plot([t,t], [self.ntrials-.5, self.ntrials+.5])

       
        

