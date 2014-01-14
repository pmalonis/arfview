from PySide.QtGui import *
from PySide.QtCore import *
import sys
import pyqtgraph as pg
import numpy as np
import arfview.utils as utils
import h5py
import arf

class labelPlot(pg.PlotItem): 
    def __init__(self, lbl, *args, **kwargs):
        super(labelPlot, self).__init__(*args, **kwargs)
        if not utils.is_complex_event(lbl):           
            raise TypeError("Argument must be complex event dataset")
        elif lbl.maxshape != (None,):
            raise TypeError("Argument must have maxshape (None,)")
        else:
             self.lbl = lbl

        self.key = None
        self.activeLabel = None

        if self.lbl.attrs['units'] == 'ms':
            self.scaling_factor = 1000
        elif self.lbl.attrs['units'] == 'samples':
            self.scaling_factor = self.lbl.attrs['sampling_rate']
        else:
            self.scaling_factor = 1
        
        for tup in self.lbl:
            self.plot_complex_event(tup)
                
    def plot_complex_event(self, complex_event, with_text=True):
            
        start = complex_event['start'] / self.scaling_factor
        stop = complex_event['stop'] / self.scaling_factor
        region = pg.LinearRegionItem([start, stop])
        region.setMovable(False)
        self.addItem(region)
        if with_text:
            label = complex_event['name']
            text = pg.TextItem(label)
            text.setPos(start, .5)
            self.addItem(text)
            
        return region
        
    def keyPressEvent(self, event):
        if event.text().isalpha():
            self.key = event.text().upper()

    def keyReleaseEvent(self, event):
        if event.text().upper() == self.key:
            self.key = None
        
    def mouseClickEvent(self, event):        
        pos=self.getViewBox().mapSceneToView(event.scenePos())
        t = pos.x() * self.scaling_factor
        if self.key and not self.activeLabel:
           
            arf.append_data(self.lbl, (self.key, t, t))

            if event.modifiers() == Qt.ShiftModifier:
                self.activeLabel = self.plot_complex_event(self.lbl[-1],
                                                           with_text=False)    
            else:
                self.plot_complex_event(self.lbl[-1])
        elif self.activeLabel:
            if t >= self.lbl[-1]['start']:
                self.lbl[-1] = (self.lbl[-1]['name'], self.lbl[-1]['start'], t)
            else:
                self.lbl[-1] =  (self.lbl[-1]['name'], t, self.lbl[-1]['stop'])

            self.plot_complex_event(self.lbl[-1])
            self.activeLabel = None
        
def main():

    lbl=np.zeros((2,),dtype=[('name', 'a8'), ('start',float), ('stop', float)])
    lbl[:] = [('A', .2, .4), ('B', .5, .9)]
    with h5py.File('test.arf','a') as f:
        arf.create_dataset(f['/'],'asdf',data=lbl,units='s',maxshape=(None,),datatype=2002)
        app = QApplication(sys.argv)

        win = pg.GraphicsWindow()

        g = labelPlot(f['asdf'])
        win.addItem(g)
        win.show()
        sys.exit(app.exec_())


if __name__=='__main__':
    main()