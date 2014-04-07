"""an alpha version of the plotter"""


from __future__ import absolute_import, division, \
    print_function
from PySide import QtGui, QtCore
import signal
import sys
import pyqtgraph as pg
import pyqtgraph.dockarea as pgd
import h5py
import numpy as np
from scipy.io import wavfile
import os.path
import tempfile
from datatree import DataTreeView, createtemparf, named_types
import arfview.utils as utils
QtCore.qInstallMsgHandler(lambda *args: None) # suppresses PySide 1.2.1 bug
from scipy.interpolate import interp2d
import scipy.signal
from arfview.labelPlot import labelPlot
from arfview.treeToolBar import treeToolBar
from arfview.settingsPanel import settingsPanel
from arfview.rasterPlot import rasterPlot
from arfview.downsamplePlot import downsamplePlot
import arf
import libtfr

import lbl
#print(lbl.__version__)

class MainWindow(QtGui.QMainWindow):
    '''the main window of the program'''
    def __init__(self):
        super(MainWindow, self).__init__()
        self.current_file = None
        self.open_files = []    # TODO replace current_file with list
        self.plotchecked = False
        self.initUI()

    def initUI(self):
        """"Assembles the basic Gui layout, status bar, menubar
        toolbar etc."""
        # status bar
        self.statusBar().showMessage('Ready')

        # actions
        soundAction = QtGui.QAction(QtGui.QIcon.fromTheme('media-playback-start'),
                                    'Play Sound', self)
        soundAction.setShortcut('Ctrl+S')
        soundAction.setStatusTip('Play data as sound')
        soundAction.triggered.connect(self.playSound)
        exitAction = QtGui.\
            QAction(QtGui.QIcon.fromTheme('window-close'),
                    'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)
        openAction = QtGui.\
            QAction(QtGui.QIcon.fromTheme('document-open'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open an arf file')
        openAction.triggered.connect(self.showDialog)

        exportAction = QtGui.QAction(QtGui.QIcon.fromTheme('document-save-as'),
                                    'Export checked', self)
        exportAction.setShortcut('Ctrl+e')
        exportAction.setStatusTip('Export dataset as wav')
        exportAction.triggered.connect(self.export)

        plotcheckedAction = QtGui.QAction(QtGui.QIcon.fromTheme('face-smile'),
                                          'Plot checked', self)
        plotcheckedAction.setShortcut('Ctrl+k')
        plotcheckedAction.setStatusTip('plot checked')
        plotcheckedAction.triggered.connect(self.toggleplotchecked)
        self.plotcheckedAction = plotcheckedAction

        refreshAction = QtGui.QAction(QtGui.QIcon.fromTheme('view-refresh'),
                                      'Refresh Data View', self)
        refreshAction.setShortcut('Ctrl+r')
        refreshAction.setStatusTip('Refresh Data View')
        refreshAction.triggered.connect(self.refresh_data_view)

        labelAction = QtGui.QAction(QtGui.QIcon.fromTheme('insert-object'),
                                      'Add Label', self)
        labelAction.setVisible(False)
        labelAction.setShortcut('Ctrl+l')
        labelAction.setStatusTip('Add label entry to current group')
        labelAction.triggered.connect(self.add_label)
        self.labelAction = labelAction

        addPlotAction = QtGui.QAction('Add Plot', self)
        addPlotAction.setVisible(False)
        addPlotAction.setStatusTip('Add checked datasets to current plot')
        addPlotAction.triggered.connect(self.add_plot)
        self.addPlotAction = addPlotAction
        
        # menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exportAction)
        fileMenu.addAction(plotcheckedAction)
        fileMenu.addAction(refreshAction)

        # toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(soundAction)
        self.toolbar.addAction(exportAction)
        self.toolbar.addAction(plotcheckedAction)
        self.toolbar.addAction(refreshAction)
        self.toolbar.addAction(labelAction)
        self.toolbar.addAction(addPlotAction)

        # file tree
        self.tree_view = DataTreeView()
        self.tree_view.currentItemChanged.connect(self.selectEntry)
        if self.current_file:
            self.populateTree()

        # tree_toolbar
        self.tree_toolbar = treeToolBar(self.tree_view)
        
        #attribute table
        self.attr_table = QtGui.QTableWidget(10, 2)
        self.attr_table.setHorizontalHeaderLabels(('key','value'))

        #plot region
        self.data_layout = pg.GraphicsLayoutWidget()
        self.subplots=[]

        #settings panel
        self.settings_panel = settingsPanel()

        # final steps
        self.area = pgd.DockArea()
        tree_dock = pgd.Dock("Tree", size=(200, 100))
        data_dock = pgd.Dock("Data", size=(500, 200))
        attr_table_dock = pgd.Dock("Attributes", size=(200, 50))
        settings_dock = pgd.Dock('Settings', size=(150,1))
        self.area.addDock(tree_dock, 'left')
        self.area.addDock(data_dock, 'right')
        self.area.addDock(attr_table_dock, 'bottom', tree_dock)
        self.area.addDock(settings_dock, 'bottom', attr_table_dock)
        tree_dock.addWidget(self.tree_view)
        tree_dock.addWidget(self.tree_toolbar)
        tree_dock.addAction(exitAction)
        data_dock.addWidget(self.data_layout)
        attr_table_dock.addWidget(self.attr_table)
        settings_dock.addWidget(self.settings_panel)
        self.settings_panel.show()
        
        self.setCentralWidget(self.area)
        self.setWindowTitle('arfview')
        self.resize(1200, 700)
        self.show()

    def toggleplotchecked(self):
        self.plotchecked = not self.plotchecked
        print('plot checked: ' + str(self.plotchecked))
        if self.plotchecked:
            self.plotcheckedAction.setIcon(QtGui.QIcon.fromTheme('face-cool'))
            self.plotcheckedAction.setStatusTip('click to turn check mode off')
            self.plotcheckedAction.setText('check mode is on')
            self.plotcheckedAction.setIconText('check mode is on')
            self.addPlotAction.setVisible(True)
        else:
            self.plotcheckedAction.setIcon(QtGui.QIcon.fromTheme('face-smile'))
            self.plotcheckedAction.setStatusTip('click to turn check mode on')
            self.plotcheckedAction.setText('check mode is off')
            self.plotcheckedAction.setIconText('check mode is off')
            self.addPlotAction.setVisible(False)


    def export(self):
        items = self.tree_view.all_checked_dataset_elements()
        if not items: return
        savedir, filename = os.path.split(items[0].file.filename)
        savepath =  os.path.join(savedir,os.path.splitext(filename)[0]
                                 + '_' + items[0].name.replace('/','_'))
        print(savepath)
        fname, fileextension = QtGui.QFileDialog.\
                               getSaveFileName(self, 'Save data as',
                                               savepath,
                                               'wav (*.wav);;text (*.csv, *.dat)')
        for i,item in enumerate(items):
            if 'datatype' in item.attrs.keys() and item.attrs['datatype'] < 1000:
                if i:
                    fname =  os.path.join(savedir,os.path.splitext(filename)[0]
                                          + '_' + item.name.replace('/','_'))
                export(item, fileextension.split(' ')[0], fname)
                
    def playSound(self):
        item = self.tree_view.currentItem().getData()
        playSound(item)

    def showDialog(self):
        fname, fileextension = QtGui.QFileDialog.\
                               getOpenFileName(self, 'Open file', '.',
                                               '*.arf *.hdf5 *.h5 *.mat *.wav *.lbl *.pcm *.pcm_seq2')
        if not fname: return
        print(fileextension)
        ext = os.path.splitext(fname)[-1]
        if ext not in ('.arf','.hdf5','.h5','.mat'):
            if ext in ('.lbl', '.wav'):
                temp_h5f = createtemparf(fname)
            elif ext in ('.pcm', '.pcm_seq2'):
                # reversing value and key to access type number from datatype_name
                sampled_types = {value:key for key,value in named_types.items()
                                 if key > 0 and key < 1000}
                #import pdb; pdb.set_trace()
                datatype_name,ok = QtGui.QInputDialog.getItem(self, "",
                                                              "Select datatype of file",
                                                              sampled_types.keys())
                if not ok: return
                temp_h5f = createtemparf(fname, datatype=sampled_types[datatype_name])

            fname = temp_h5f.file.filename
            
        print("%s opened" % (fname))
        self.statusBar().showMessage("%s opened" % (fname))
        self.current_file = h5py.File(str(fname))
        self.populateTree()
        
        # selects first entry if first file opened
        item=self.tree_view.topLevelItem(0)
        if item.getData().file.filename == fname:
            #self.selectEntry(item.child(0))
            self.tree_view.setCurrentItem(item.child(0))


    def populateTree(self):
        f = self.current_file
        root = f['/']
        self.tree_view.recursivePopulateTree(root)

    def refresh_data_view(self):
        checked_datasets = self.tree_view.all_checked_dataset_elements()
        if len(checked_datasets) > 0 and self.plotchecked:
            self.plot_dataset_list(checked_datasets, self.data_layout)
        else:
            item = self.tree_view.currentItem().getData()
            if type(item) == h5py.Dataset:
                datasets = [item]
            else:
                datasets = [x for x in item.values() if type(x) == h5py.Dataset]
            self.plot_dataset_list(datasets, self.data_layout)

    def add_plot(self):
        checked_datasets = self.tree_view.all_checked_dataset_elements()
        if len(checked_datasets) > 0 and self.plotchecked:
            new_layout = self.data_layout.addLayout(row=len(self.subplots),col=0)
            self.plot_dataset_list(checked_datasets, new_layout)
 

    def selectEntry(self, treeItem):
        item = treeItem.getData()
        populateAttrTable(self.attr_table, item)
        if not self.plotchecked:
            self.refresh_data_view()
        if (isinstance(item, h5py.Dataset) or isinstance(item, h5py.Group)
            and item.name != '/'):
            self.labelAction.setVisible(True)
        else:
            self.labelAction.setVisible(False)
            
    def add_label(self):
        item = self.tree_view.currentItem()
        if isinstance(item.getData(), h5py.Group):
            lbl_parent = item
        elif isinstance(item.getData(), h5py.Dataset):
            lbl_parent = item.parent()
        lbl_rec = np.zeros((0,),dtype=[('name', 'a8'), ('start',float), ('stop', float)])
        dset_name = 'lbl'
        #naming new label dataset if 'lbl' is already in group
        idx = 1
        while dset_name in lbl_parent.getData().keys():
            dset_name = 'lbl_%d' %(idx)
            idx += 1
            
        dset = lbl_parent.getData().create_dataset(dset_name,
                                                   data=lbl_rec,
                                                   maxshape=(None,))
        dset.attrs.create('units','ms')
        dset.attrs.create('datatype',2002)
        self.tree_view.add(dset, parent_node=lbl_parent)
        self.refresh_data_view()

    def plot_dataset_list(self, dataset_list, data_layout, append=False):
        ''' plots a list of datasets to a data layout'''
        data_layout.clear()
        if not append:
            self.subplots = []
        # rasterQPainterPath = QtGui.QPainterPath().addRect(-.1,-5,.2,1)  # TODO make a better raster
        # shape that works

        toes = []
        for dataset in dataset_list:
            print(dataset)
            if 'datatype' not in dataset.attrs.keys():
                print('{} is not an arf dataset'.format(repr(dataset)))
                if os.path.basename(dataset.name) == 'jill_log':
                    print(dataset.value)
                continue

            '''sampled data'''
            if dataset.attrs['datatype'] < 1000: # sampled data
                if (self.settings_panel.oscillogram_check.checkState()
                    ==QtCore.Qt.Checked): 
                    
                    pl = downsamplePlot(dataset, title=dataset.name,
                                        name=str(len(self.subplots)))
                    data_layout.addItem(pl,row=len(self.subplots), col=0)
                    pl.setXRange(0, dataset.size/float(dataset.attrs['sampling_rate']))
                    pl.setYRange(np.min(dataset), np.max(dataset))                    
                    self.subplots.append(pl)
                    pl.showGrid(x=True, y=True)

                ''' simple events '''
            elif utils.is_simple_event(dataset):
                if dataset.attrs['units'] == 'ms':
                    data = dataset.value / 1000.
                elif dataset.attrs['units'] == 'samples':
                    data = dataset.value / dataset.attrs['sampling_rate']
                else:
                    data = dataset.value
                if (self.settings_panel.raster_check.checkState()==QtCore.Qt.Checked or
                    self.settings_panel.psth_check.checkState()==QtCore.Qt.Checked or
                    self.settings_panel.isi_check.checkState()==QtCore.Qt.Checked):                    
                    toes.append(data)
                continue

                ''' complex event '''
            elif utils.is_complex_event(dataset):
                if (self.settings_panel.label_check.checkState()
                    ==QtCore.Qt.Checked):
                
                    #creating new extensible dataset if not extensible
                    if dataset.maxshape != (None,):
                        data = dataset[:]
                        name = dataset.name
                        group= dataset.parent
                        attributes = dataset.attrs
                        del group[name]
                        del dataset
                        dataset = arf.create_dataset(group, name, data,
                                                     maxshape=(None,),**attributes)

                    pl = labelPlot(dataset, title=dataset.name, name=str(len(self.subplots)))
                    data_layout.addItem(pl, row=len(self.subplots), col=0) 
                    pl.showLabel('left', show=False)
                    self.subplots.append(pl)

            else:
                print('I don\'t know how to plot {} of type {} \
                with datatype {}'.format(dataset,
                                         type(dataset),
                                         dataset.attrs['datatype']))
                continue

            '''adding spectrograms'''
            if dataset.attrs['datatype'] in [0, 1]: # show spectrogram
                if (self.settings_panel.spectrogram_check.checkState()
                    ==QtCore.Qt.Checked):
                    #getting spectrogram settings
                    sr = float(dataset.attrs['sampling_rate'])
                    win_size_text = self.settings_panel.win_size.text()
                    t_step_text = self.settings_panel.step.text()
                    min_text = self.settings_panel.freq_min.text()
                    max_text = self.settings_panel.freq_max.text()

                    if win_size_text:
                        win_size = int(float(win_size_text))
                    else:
                        win_size = self.settings_panel.defaults['win_size']
                        self.settings_panel.win_size.setText(str(win_size))
                    if t_step_text:
                        t_step = int(float(t_step_text) * sr/1000.)
                    else:
                        t_step = self.settings_panel.defaults['step']
                        self.settings_panel.win_size.setText(str(int(tstep*1000)))
                    if min_text:
                        freq_min = int(min_text)
                    else:
                        freq_min = self.settings_panel.defaults['freq_min']
                        self.settings_panel.freq_min.setText(str(freq_min))
                    if max_text:
                        freq_max = int(max_text)
                    else:
                        freq_max = self.settings_panel.defaults['freq_max']
                        self.settings_panel.freq_max.setText(str(freq_max))                                        
                    
                    window_name = self.settings_panel.window.currentText()                
                    if window_name == "Hann":
                        window = scipy.signal.hann(win_size)
                    elif window_name == "Bartlett":
                        window = scipy.signal.bartlett(win_size)
                    elif window_name == "Blackman":
                        window = scipy.signal.blackman(win_size)
                    elif window_name == "Boxcar":
                        window = scipy.signal.boxcar(win_size)
                    elif window_name == "Hamming":
                        window = scipy.signal.hamming(win_size)
                    elif window_name == "Parzen":
                        window = scipy.signal.parzen(win_size)
                    
                    #computing and interpolating image
                    Pxx = libtfr.stft(dataset,w=window,step=t_step)
                    spec = np.log(Pxx.T)
                    res_factor = 1.0 #factor by which resolution is increased
#                    spec = interpolate_spectrogram(spec, res_factor=res_factor)

                    #making color lookup table
                    pos = np.linspace(0,1,7)
                    color = np.array([[100,100,255,255],[0,0,255,255],[0,255,255,255],[0,255,0,255],
                                      [255,255,0,255],[255,0,0,255],[100,0,0,255]], dtype=np.ubyte)
                    color_map = pg.ColorMap(pos,color)
                    lut = color_map.getLookupTable(0.0,1.0,256)
                    img = pg.ImageItem(spec,lut=lut)
                    #img.setLevels((-5, 10))

                    pl = data_layout.addPlot(name=str(len(self.subplots)), row=len(self.subplots), col=0)
                    self.subplots.append(pl)

                    pl.addItem(img)
                    image_scale = t_step/sr/res_factor
                    img.setScale(image_scale)
                    df = sr/float(win_size)
                    plot_scale = df/res_factor/image_scale
                    pl.getAxis('left').setScale(plot_scale)
                    pl.setXRange(0, dataset.size / dataset.attrs['sampling_rate'])
                    pl.setYRange(freq_min/plot_scale, freq_max/plot_scale)
                    pl.setMouseEnabled(x=True, y=False)
                    
        if toes:
            if self.settings_panel.raster_check.checkState()==QtCore.Qt.Checked:
                pl= rasterPlot(toes)
                data_layout.addItem(pl, row=len(self.subplots), col=0) 
                pl.showLabel('left', show=False)
                self.subplots.append(pl)

            if self.settings_panel.psth_check.checkState()==QtCore.Qt.Checked:
                all_toes = np.zeros(sum(len(t) for t in toes))
                k=0
                for t in toes:
                    all_toes[k:k+len(t)] = t
                    k += len(t)
                if self.settings_panel.psth_bin_size.text():
                    bin_size = float(self.settings_panel.psth_bin_size.text())/1000.
                else:
                    bin_size = .01
                bins = np.arange(all_toes.min(),all_toes.max()+bin_size,bin_size)
                y,x = np.histogram(all_toes,bins=bins)
                psth = pg.PlotCurveItem(x, y, stepMode=True,
                                        fillLevel=0, brush=(0, 0, 255, 80))

                pl = data_layout.addPlot(row=len(self.subplots), col=0)
                pl.addItem(psth)
                pl.setMouseEnabled(y=False)
                self.subplots.append(pl)
                
        if self.settings_panel.isi_check.checkState()==QtCore.Qt.Checked:
            isis = np.zeros(sum(len(t)-1 for t in toes))
            k=0
            for t in toes:
                isis[k:k+len(t)-1] = np.diff(t)
                k += len(t)-1
            if self.settings_panel.psth_bin_size.text():
                bin_size = float(self.settings_panel.psth_bin_size.text())/1000.
            else:
                bin_size = .01
            bins = np.arange(isis.min(),isis.max()+bin_size,bin_size) 
            y,x = np.histogram(isis,bins=bins,normed=True)
            isi_hist = pg.PlotCurveItem(x, y, stepMode=True,
                                    fillLevel=0, brush=(0, 0, 255, 80))
    
            pl = data_layout.addPlot(row=len(self.subplots), col=0)
            pl.addItem(isi_hist)
            pl.setMouseEnabled(y=False)
            self.subplots.append(pl)

        '''linking x axes'''
        masterXLink = None
        for pl in self.subplots:
            if not masterXLink:
                masterXLink = pl
            pl.setXLink(masterXLink)


## Make all plots clickable
lastClicked = []


def clicked(plot, points):
    global lastClicked
    for p in lastClicked:
        p.resetPen()
    print("clicked points", points)
    for p in points:
        p.setPen('b', width=2)
        print(dir(p))
    lastClicked = points




def export(dataset, export_format='wav', savepath=None):
    if not savepath:
        savepath = os.path.basename(dataset.name)
    if export_format == 'wav':
        data = np.int16(dataset.value / max(abs(dataset.value)) * (2**15 - 1))
        wavfile.write(savepath + '.wav', dataset.attrs['sampling_rate'], data)
    if export_format == 'text':
        np.savetxt(savepath + '.csv', dataset)


def playSound(data):
    print('writing wav file')
    tfile = tempfile.mktemp() + '_' + data.name.replace('/', '_') + '.wav'
    normed_data = np.int16(data/np.max(np.abs(data.value)) * 32767)
    wavfile.write(tfile, data.attrs['sampling_rate'],
                  normed_data)
    os.system('play ' + tfile)


def populateAttrTable(table, item):
    """Populate QTableWidget with attribute values of hdf5 item ITEM"""
    table.setRowCount(len(item.attrs.keys()))


    for row, (key, value) in enumerate(item.attrs.iteritems()):
        attribute = QtGui.QTableWidgetItem(str(key))
        attribute_value = QtGui.QTableWidgetItem(str(value))
        table.setItem(row, 0, attribute)
        table.setItem(row, 1, attribute_value)


def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    QtGui.QApplication.quit()

def interpolate_spectrogram(spec, res_factor):
    """Interpolates spectrogram for plotting"""
    x = np.arange(spec.shape[1])
    y = np.arange(spec.shape[0])
    f = interp2d(x, y, spec, copy=False, kind = 'quintic')
    xnew = np.arange(0,spec.shape[1],1./res_factor)
    ynew = np.arange(0,spec.shape[0],1./res_factor)
    new_spec = f(xnew,ynew)

    return new_spec
    
def main():
    signal.signal(signal.SIGINT, sigint_handler)
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('arfview')
    timer = QtCore.QTimer()
    timer.start(500)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
    mainWin = MainWindow()
    sys.exit(app.exec_())
    #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #    QtGui.QApplication.instance().exec_()

if __name__=='__main__':
    main()
