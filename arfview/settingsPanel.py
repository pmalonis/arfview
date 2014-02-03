from PySide import QtGui, QtCore
import pyqtgraph.dockarea as pgd
import pyqtgraph as pg

class settingsPanel(QtGui.QWidget):
    def __init__(self):
        super(settingsPanel, self).__init__()
        self.initUI()

    def initUI(self):
        self.time_axis_box = self.create_time_axis_box()
        self.oscillogram_box = self.create_oscillogram_box()
        self.spectrogram_box = self.create_spectrogram_box()
        self.raster_box = self.create_raster_box()
        self.psth_box = self.create_psth_box()
        self.isi_box = self.create_isi_box()
        self.applyButton=QtGui.QPushButton("apply")


        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.time_axis_box)
        layout.addWidget(self.oscillogram_box)
        layout.addWidget(self.spectrogram_box)
        layout.addWidget(self.raster_box)
        layout.addWidget(self.isi_box)
        layout.addWidget(self.psth_box)
        layout.addWidget(self.applyButton)

        self.setLayout(layout)

    def create_time_axis_box(self):
        self.t_min_edit = QtGui.QLineEdit()
        self.t_max_edit = QtGui.QLineEdit()
        self.t_min_edit.setMaximumWidth(100)
        self.t_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("Time Axis")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 1
        min_label=QtGui.QLabel('Time Min:')
        max_label=QtGui.QLabel('Time Max:')
        layout.addWidget(min_label,uedge-1, ledge)
        layout.addWidget(max_label,uedge-1, ledge+1)
        layout.addWidget(self.t_min_edit, uedge, ledge)
        layout.addWidget(self.t_max_edit, uedge, ledge+1)

        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(70)
        group_box.setLayout(layout)

        print layout.originCorner()
        return group_box
        
    def create_oscillogram_box(self):
        self.oscillogram_check=QtGui.QCheckBox("Visible")
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        self.y_min_edit.setMaximumWidth(100)
        self.y_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("Oscillogram")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 0
        min_label=QtGui.QLabel('Y Min:')
        max_label=QtGui.QLabel('Y Max:')
        layout.addWidget(self.oscillogram_check, uedge, ledge)
        layout.addWidget(min_label,uedge+1, ledge)
        layout.addWidget(max_label,uedge+1, ledge+1)
        layout.addWidget(self.y_min_edit, uedge+2, ledge)
        layout.addWidget(self.y_max_edit, uedge+2, ledge+1)
        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(100)
        group_box.setLayout(layout)

        return group_box

    def create_spectrogram_box(self):
        self.spectrogram_check=QtGui.QCheckBox("Visible")
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        self.y_min_edit.setMaximumWidth(100)
        self.y_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("Spectrogram")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 0
        min_label=QtGui.QLabel('Y Min:')
        max_label=QtGui.QLabel('Y Max:')
        layout.addWidget(self.spectrogram_check, uedge, ledge)
        layout.addWidget(min_label,uedge+1, ledge)
        layout.addWidget(max_label,uedge+1, ledge+1)
        layout.addWidget(self.y_min_edit, uedge+2, ledge)
        layout.addWidget(self.y_max_edit, uedge+2, ledge+1)
        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(100)
        group_box.setLayout(layout)
    
        return group_box
        

    def create_raster_box(self):
        self.raster_check=QtGui.QCheckBox("Visible")
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        self.y_min_edit.setMaximumWidth(100)
        self.y_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("Raster")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 0
        min_label=QtGui.QLabel('Y Min:')
        max_label=QtGui.QLabel('Y Max:')
        layout.addWidget(self.raster_check, uedge, ledge)
        layout.addWidget(min_label,uedge+1, ledge)
        layout.addWidget(max_label,uedge+1, ledge+1)
        layout.addWidget(self.y_min_edit, uedge+2, ledge)
        layout.addWidget(self.y_max_edit, uedge+2, ledge+1)
        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(100)
        group_box.setLayout(layout)

        return group_box

        
    def create_psth_box(self):
        self.psth_check=QtGui.QCheckBox("Visible")
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        self.y_min_edit.setMaximumWidth(100)
        self.y_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("PSTH")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 0
        min_label=QtGui.QLabel('Y Min:')
        max_label=QtGui.QLabel('Y Max:')
        layout.addWidget(self.psth_check, uedge, ledge)
        layout.addWidget(min_label,uedge+1, ledge)
        layout.addWidget(max_label,uedge+1, ledge+1)
        layout.addWidget(self.y_min_edit, uedge+2, ledge)
        layout.addWidget(self.y_max_edit, uedge+2, ledge+1)
        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(100)
        group_box.setLayout(layout)

        return group_box

    def create_isi_box(self):
        self.isi_check=QtGui.QCheckBox("Visible")
        self.isi_check=QtGui.QCheckBox("Visible")
        self.y_min_edit = QtGui.QLineEdit()
        self.y_max_edit = QtGui.QLineEdit()
        self.y_min_edit.setMaximumWidth(100)
        self.y_max_edit.setMaximumWidth(100)
        group_box = QtGui.QGroupBox("ISI")
        layout = QtGui.QGridLayout()
        ledge = 0
        uedge = 0
        min_label=QtGui.QLabel('Y Min:')
        max_label=QtGui.QLabel('Y Max:')
        layout.addWidget(self.isi_check, uedge, ledge)
        layout.addWidget(min_label,uedge+1, ledge)
        layout.addWidget(max_label,uedge+1, ledge+1)
        layout.addWidget(self.y_min_edit, uedge+2, ledge)
        layout.addWidget(self.y_max_edit, uedge+2, ledge+1)
        layout.setContentsMargins(0,0,50,10)
        layout.setColumnStretch(1,30)
        group_box.setMaximumHeight(100)
        group_box.setLayout(layout)

        return group_box