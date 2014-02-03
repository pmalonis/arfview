#! /usr/bin/env python
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
from matplotlib.mlab import specgram
from scipy.io import wavfile
import os.path
import tempfile
from arfview.datatree import DataTreeView, createtemparf
import arfview.utils as utils
QtCore.qInstallMsgHandler(lambda *args: None) # suppresses PySide 1.2.1 bug
from arfview.labelPlot import labelPlot
from arfview.treeToolBar import treeToolBar
from arfview.settingsPanel import settingsPanel
import arf

import lbl
print(lbl.__version__)

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
                                    'PlaySound', self)
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
                                    'Export data', self)
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

        #settings panel
        self.settings_panel = settingsPanel()
        print(self.settings_panel.layout())
        # self.settings_panel = settingsPanel('Settings', size=(200,1))
        # self.oscillogram = QtGui.QCheckBox("oscillogram")
        # self.spectrogram = QtGui.QCheckBox("spectrogram")
        # self.raster = QtGui.QCheckBox("raster")
        # self.psth = QtGui.QCheckBox("PSTH")
        # self.isi = QtGui.QCheckBox("ISI")
        # self.applyButton=QtGui.QPushButton("apply")

        # ledge = 0
        # uedge = 0

        # self.settings_panel.addWidget(self.oscillogram, uedge, ledge)
        # self.settings_panel.addWidget(self.spectrogram, uedge + 1, ledge)
        # self.settings_panel.addWidget(self.raster, uedge + 2, ledge)
        # self.settings_panel.addWidget(self.isi, uedge + 3, ledge)
        # self.settings_panel.addWidget(self.psth, uedge + 4, ledge)
        # self.settings_panel.addWidget(self.applyButton, uedge + 5, ledge + 1)

        # final steps
        self.area = pgd.DockArea()
        tree_dock = pgd.Dock("Tree", size=(200, 1))
        data_dock = pgd.Dock("Data", size=(500, 200))
        attr_table_dock = pgd.Dock("Attributes", size=(200, 1))
        settings_dock = pgd.Dock('Settings', size=(300,200))
        self.area.addDock(tree_dock, 'left')
        self.area.addDock(data_dock, 'right')
        self.area.addDock(attr_table_dock, 'bottom', tree_dock)
        self.area.addDock(settings_dock, 'right', data_dock)
        tree_dock.addWidget(self.tree_view)
        tree_dock.addWidget(self.tree_toolbar)
        tree_dock.addAction(exitAction)
        data_dock.addWidget(self.data_layout)
        attr_table_dock.addWidget(self.attr_table)
        settings_dock.addWidget(self.settings_panel)
        self.settings_panel.show()
        
        self.setCentralWidget(self.area)
        self.setWindowTitle('arfview')
        self.resize(1200, 800)
        self.show()

    def toggleplotchecked(self):
        self.plotchecked = not self.plotchecked
        print('plot checked: ' + str(self.plotchecked))
        if self.plotchecked:
            self.plotcheckedAction.setIcon(QtGui.QIcon.fromTheme('face-cool'))
            self.plotcheckedAction.setStatusTip('click to turn check mode off')
            self.plotcheckedAction.setText('check mode is on')
            self.plotcheckedAction.setIconText('check mode is on')
        else:
            self.plotcheckedAction.setIcon(QtGui.QIcon.fromTheme('face-smile'))
            self.plotcheckedAction.setStatusTip('click to turn check mode on')
            self.plotcheckedAction.setText('check mode is off')
            self.plotcheckedAction.setIconText('check mode is off')


    def export(self):
        item = self.tree_view.currentItem().getData()
        savedir, filename = os.path.split(item.file.filename)
        savepath =  os.path.join(savedir,
                                 os.path.splitext(filename)[0] + '_' + item.name.replace('/','_'))
        print(savepath)
        if type(item) == h5py._hl.dataset.Dataset:
            print('die')
            fname, fileextension = QtGui.QFileDialog.\
                                   getSaveFileName(self, 'Save data as',
                                                   savepath,
                                                   'wav (*.wav);;text (*.csv, *.dat)')
            export(item, fileextension.split(' ')[0], fname)

    def playSound(self):
        item = self.tree_view.currentItem().getData()
        playSound(item)

    def showDialog(self):
        fname, fileextension = QtGui.QFileDialog.\
                               getOpenFileName(self, 'Open file', '.',
                                               '*.arf ;; *.lbl ;; *.hdf5, *.h5 ;; *.mat')
        print(fileextension)
        extention = os.path.splitext(fname)[-1]
        if extention == '.lbl':
            temp_h5f = createtemparf(fname)
            fname = temp_h5f.file.filename
        print("%s opened" % (fname))
        self.statusBar().showMessage("%s opened" % (fname))
        self.current_file = h5py.File(str(fname))
        self.populateTree()
        self.current_file_name = fname

    def populateTree(self):
        f = self.current_file
        root = f['/']
        self.tree_view.recursivePopulateTree(root)

    def refresh_data_view(self):
        checked_datasets = self.tree_view.all_checked_dataset_elements()
        if len(checked_datasets) > 0 and self.plotchecked:
            plot_dataset_list(checked_datasets, self.data_layout)
        else:
            item = self.tree_view.currentItem().getData()
            if type(item) == h5py.Dataset:
                datasets = [item]
            else:
                datasets = [x for x in item.values() if type(x) == h5py.Dataset]
            plot_dataset_list(datasets, self.data_layout)


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
            lbl_parent = item.parent
        lbl_rec = np.zeros((0,),dtype=[('name', 'a8'), ('start',float), ('stop', float)])
        dset_name = 'lbl'
        #naming new label dataset if 'lbl' is already in group
        idx = 1
        while dset_name in lbl_parent.getData().keys():
            dset_name = 'lbl_%d' %(idx)
            idx += 1
            
        dset = arf.create_dataset(lbl_parent.getData(), dset_name, data=lbl_rec, units = 'ms',
                                  maxshape=(None,), datatype=2002)
        self.tree_view.add(dset, parent_node=lbl_parent)
        self.refresh_data_view()

def plot_dataset_list(dataset_list, data_layout):
    ''' plots a list of datasets to a data layout'''
    data_layout.clear()
    subplots = []
    # rasterQPainterPath = QtGui.QPainterPath().addRect(-.1,-5,.2,1)  # TODO make a better raster
                                                                      # shape that works
    for dataset in dataset_list:
        print(dataset)
        if 'datatype' not in dataset.attrs.keys():
            print('{} is not an arf dataset'.format(repr(dataset)))
            if os.path.basename(dataset.name) == 'jill_log':
                print(dataset.value)
            continue

        '''sampled data'''
        if dataset.attrs['datatype'] < 1000: # sampled data
            sr = float(dataset.attrs['sampling_rate'])
            t = np.arange(0, len(dataset)) / sr
            pl = data_layout.addPlot(title=dataset.name,
                                          name=str(len(subplots)), row=len(subplots), col=0)
            subplots.append(pl)
            pl.plot(t, dataset)
            pl.showGrid(x=True, y=True)

            ''' simple events '''
        elif utils.is_simple_event(dataset):
            if dataset.attrs['units'] == 'ms':
                data = dataset.value / 1000.
            elif dataset.attrs['units'] == 'samples':
                data = dataset.value / dataset.attrs['sampling_rate']
            else:
                data = dataset.value
            pl = data_layout.addPlot(title=dataset.name, name=str(len(subplots)),
                                    row=len(subplots), col=0)
            subplots.append(pl)
            s = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120),
                                   symbol='s')
            spots = [{'pos': (i, 0), 'data': 1} for i in data]
            s.addPoints(spots)
            pl.addItem(s)
            s.sigClicked.connect(clicked)

            ''' complex event '''
        elif utils.is_complex_event(dataset):
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
                
            pl = labelPlot(dataset, title=dataset.name, name=str(len(subplots)))
            data_layout.addItem(pl, row=len(subplots), col=0) 
            pl.showLabel('left', show=False)
            subplots.append(pl)
            
        else:
            print('I don\'t know how to plot {} of type {} \
            with datatype {}'.format(dataset,
                                     type(dataset),
                                     dataset.attrs['datatype']))
            continue

        '''linking x axes'''
        if len(subplots) == 1:
            masterXLink = pl
        else:
            pl.setXLink(masterXLink)
        '''adding spectrograms'''
        if dataset.attrs['datatype'] in [0, 1]: # show spectrogram
            Pxx, freqs, ts = specgram(dataset, Fs=sr, NFFT=512, noverlap=400)
            img = pg.ImageItem(np.log(Pxx.T))
            #img.setLevels((-5, 10))
            img.setScale(ts[-1] / Pxx.shape[1])
            vb = data_layout.addViewBox(name=str(len(subplots)), row=len(subplots), col=0)
            subplots.append(vb)

            g = pg.GridItem()
            vb.addItem(g)
            vb.addItem(img)
            vb.setMouseEnabled(x=True, y=False)
            vb.setXLink(masterXLink)

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
    os.system('vlc ' + tfile + ' &')


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
