from PySide import QtGui, QtCore
import pyqtgraph.dockarea as pgd

class settingsPanel(QtGui.QDialog):
    def __init__(self):
        super(plotCheckedWindow, self).__init__()
        self.initUI

    def initUI(self):
        self.oscillogram = QtGui.QCheckBox("oscillogram")
        self.spectrogram = QtGui.QCheckBox("spectrogram")
        self.raster = QtGui.QCheckBox("raster")
        self.psth = QtGui.QCheckBox("PSTH")
        self.isi = QtGui.QCheckBox("ISI")
        self.applyButton=QtGui.QPushButton("apply")
        
        layout=QtGui.QGridLayout()

        ledge = 0
        uedge = 0

        layout.addWidget(self.oscillogram, uedge, ledge)
        layout.addWidget(self.spectrogram, uedge + 1, ledge)
        layout.addWidget(self.raster, uedge + 2, ledge)
        layout.addWidget(self.isi, uedge + 3, ledge)
        layout.addWidget(self.psth, uedge + 4, ledge)
        layout.addWidget(self.applyButton, uedge + 5, ledge + 1)
        self.setLayout(layout)
        