import pyqtgraph as pg
import numpy as np

class downsamplePlot(pg.PlotItem):
    def __init__(self, dataset, *args, **kwargs):
        super(downsamplePlot, self).__init__(*args, **kwargs)
        sr = float(dataset.attrs['sampling_rate'])
        factor=int(np.ceil(dataset.len()/100000.0))
        t = np.arange(0, dataset.len(), factor) / sr
        self.plot(t, dataset[::factor])
        # self.data_item = pg.PlotDataItem(self.times,dataset)
        # ax = self.getAxis('bottom')
        # npoints = sum(np.logical_and(ax.range[0]<self.times,ax.range[1]>self.times))
        # max_points=100000.0
        # self.data_item.setDownsampling(max(1,npoints/max_points))
        # self.addItem(self.data_item)

    