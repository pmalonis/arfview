#! /usr/bin/env python
"""an alpha version of the plotter"""

from __future__ import absolute_import, division, \
    print_function, unicode_literals
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

class MainWindow(QtGui.QMainWindow):
    '''the main window of the program'''
    def __init__(self):
        super(MainWindow, self).__init__()
        self.current_file = None
        self.open_files = []    # TODO replace current_file with list
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

        # menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(openAction)

        # toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(soundAction)
        self.toolbar.addAction(exportAction)

        # file tree
        self.tree_view = QtGui.QTreeWidget()
        self.tree_view.currentItemChanged.connect(self.selectEntry)
        if self.current_file:
            self.populateTree()

        #attribute table
        self.attr_table = QtGui.QTableWidget(10, 2)

        #plot region
        self.data_layout = pg.GraphicsLayoutWidget()

        # final steps
        self.area = pgd.DockArea()
        tree_dock = pgd.Dock("Tree", size=(1, 1))
        data_dock = pgd.Dock("Data", size=(500, 200))
        attr_table_dock = pgd.Dock("Attributes", size=(1, 1))
        self.area.addDock(tree_dock, 'left')
        self.area.addDock(data_dock, 'right')
        self.area.addDock(attr_table_dock, 'bottom', tree_dock)
        tree_dock.addWidget(self.tree_view)
        data_dock.addWidget(self.data_layout)
        attr_table_dock.addWidget(self.attr_table)
        self.setCentralWidget(self.area)
        self.setWindowTitle('arfview')
        self.resize(1000, 500)
        self.show()

    def export(self):
        treeItem = self.tree_view.currentItem()
        item = self.current_file[treeItem.text(0)]
        savedir = os.path.dirname(self.current_file_name)
        if type(item) == h5py._hl.dataset.Dataset:
            fname, fileextension = QtGui.QFileDialog.\
                                   getSaveFileName(self, 'Save data as',
                                                   os.path.join(savedir,
                                                                item.name),
                                                   'wav (*.wav);;dat (*.dat)')
            export(item, fileextension.split(' ')[0], fname)

    def playSound(self):
        pass
        #item = self.current_file[treeItem.text(0)]
        #playSound(item)

    def showDialog(self):
        fname, fileextension = QtGui.QFileDialog.\
                               getOpenFileName(self, 'Open file', '.',
                                               '*.arf ;; *.hdf5, *.h5 ;; *.mat')
        print("%s opened" % (fname))
        self.statusBar().showMessage("%s opened" % (fname))
        self.current_file = h5py.File(str(fname))
        self.populateTree()
        self.current_file_name = fname

    def populateTree(self):
        f = self.current_file

        def recursivePopulateTree(parent_node, data):
            tree_node = QtGui.QTreeWidgetItem([data.name])
            #tree_node.setData(0, QtCore.Qt.UserRole, data)
            tree_node.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            parent_node.addChild(tree_node)
            if type(data) == h5py._hl.group.Group:
                for item in data.itervalues():
                    recursivePopulateTree(tree_node, item)

        # add root
        topnode = QtGui.QTreeWidgetItem(["/"])
        root = f["/"]
        #topnode.setData(0, QtCore.Qt.UserRole, root)
        self.tree_view.addTopLevelItem(topnode)
        sorted_names = sorted([b.name for b in root.values()])
        sorted_entries = [root[b] for b in sorted_names]
        for item in sorted_entries:
            recursivePopulateTree(topnode, item)

    def selectEntry(self, treeItem):
        item = self.current_file[treeItem.text(0)]
        populateAttrTable(self.attr_table, item)
        plot_data(item, self.data_layout)


def plot_data(item, data_layout):
        data_layout.clear()
        subplots = []
        if type(item) == h5py._hl.dataset.Dataset:
            datasets = [item]
        else:
            datasets = [x for x in item.values() if type(x) == h5py._hl.dataset.Dataset]
        sampled_datasets = [x for x in datasets
                            if 'datatype' in x.attrs.keys() and x.attrs['datatype'] < 1000]
        event_datasets = [x for x in datasets
                          if 'datatype' in x.attrs.keys() and x.attrs['datatype'] >= 1000
                          and len(x) > 0]

        for dataset in sampled_datasets:
            sr = float(dataset.attrs['sampling_rate'])
            t = np.arange(0, len(dataset)) / sr
            pl = data_layout.addPlot(title=dataset.name,
                                          name=str(len(subplots)), row=len(subplots), col=0)
            subplots.append(pl)
            pl.plot(t, dataset)
            pl.showGrid(x=True, y=True)
            if len(subplots) == 1:
                masterXLink = pl
            else:
                pl.setXLink(masterXLink)

        for dataset in sampled_datasets: # Plot spectrograms
            if dataset.attrs['datatype'] in [0, 1]:
                sr = float(dataset.attrs['sampling_rate'])
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

        for dataset in event_datasets:
            if dataset.attrs['units'] == 'ms':
                data = dataset.value / 1000.
            else:
                data = dataset.value
            w = data_layout.addPlot(title=dataset.name, name=str(len(subplots)),
                                    row=len(subplots), col=0)
            subplots.append(w)
            s = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 120))
            spots = [{'pos': (i, 0), 'data': 1} for i in data]
            s.addPoints(spots)
            w.addItem(s)
            s.sigClicked.connect(clicked)
            if len(subplots) == 1:
                masterXLink = w
            else:
                w.setXLink(masterXLink)

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
    if export_format == 'dat':
        np.savetxt(savepath + '.dat', dataset)

def playSound(data):
    print('writing wav file')
    wavfile.write('temp.wav', data.attrs['sampling_rate'],
                  np.array(data))
#    os.system('totem temp.wav')

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
if __name__ == '__main__':
    main()
