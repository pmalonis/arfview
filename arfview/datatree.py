'''
datatree.py

This file contains aspects of arf model and it's associated view DataTreeView

'''
import tempfile
import os.path
from PySide import QtGui
from PySide.QtCore import Qt
from datetime import datetime
from dateutil import tz
import h5py
import lbl
import arf


named_types = {0 : 'UNDEFINED', 1 : 'ACOUSTIC', 2 : 'EXTRAC_HP', 3 : 'EXTRAC_LF',
               4 : 'EXTRAC_EEG', 5 : 'INTRAC_CC', 6 : 'INTRAC_VC',
               23 : 'EXTRAC_RAW',
               1000 : 'EVENT',
               1001 : 'SPIKET',
               1002 : 'BEHAVET',
               2000 : 'INTERVAL',
               2001 : 'STIMI',
               2002 : 'COMPONENTL'}

def get_str_type(h5Object):
    if type(h5Object) == h5py.Dataset:
        if h5Object.attrs['datatype'] in named_types.keys():
            return named_types[h5Object.attrs['datatype']]
        else: return str(h5Object.attrs['datatype'])
    if type(h5Object) == h5py.Group:
        return ('entry')


def get_str_time(entry):
    if 'timestamp' not in entry.attrs.keys():
        return('')
    time = datetime.fromtimestamp(entry.attrs['timestamp'][0] + entry.attrs['timestamp'][1] * 1e-6,
                                  tz.tzutc()).astimezone(tz.tzlocal())
    return time.strftime('%Y-%m-%d, %H:%M:%S:%f')

def createtemparf(lblfilename):
    lbl_rec = lbl.read(lblfilename)
    print(lbl_rec)
    arffile = arf.open_file(tempfile.mktemp())
    arf.create_dataset(arffile, os.path.split(lblfilename)[-1], lbl_rec, units='s', datatype=2002)
    return arffile['/']

class Model():
    '''A data object for the data model,
    self.data must be an arf type entry or dataset

    This function was created due to PySide segfaulting on adding hdf5 objects as data
    it essentiall provides a python object wrapper for h5py objects and has some functions
    for converting other data types to this model'''
    def __init__(self, data):
        if type(data) in [h5py.Dataset, h5py.Group]:
            self.data = data
        else:
            raise TypeError     # TODO create and arf type with the data
    def __call__(self):
        return self.data


class DataTreeItem(QtGui.QTreeWidgetItem):
    ''' an item in a data tree'''
    def __init__(self, data, *args, **kwargs):
        super(DataTreeItem, self).__init__(*args, **kwargs)
        self.setData(0, Qt.UserRole, Model(data))

    def getData(self):
        ''' use this to access the arf data in a DataTreeItem '''
        return self.data(0, Qt.UserRole)()


class DataTreeView(QtGui.QTreeWidget):
    ''' a tree for storing data, both in hdf5 and other formats '''
    def __init__(self, *args, **kwargs):
        super(DataTreeView, self).__init__(*args, **kwargs)
        self.setColumnCount(4)
        self.setHeaderLabels(('Name', 'Type', 'Time', 'File'))

    def add(self, data, parent_node=None):
        '''creates a DataTreeItem from data and returns it'''
        # assuming arf for now
        str_type = get_str_type(data)
        if type(data) == h5py.Group:
            str_time = get_str_time(data)
        else: str_time = ''
        fname = data.file.filename
        tree_node = DataTreeItem(data, [data.name, str_type, str_time, fname])
        tree_node.setData(0, Qt.UserRole, Model(data))
        if type(data) == h5py.Dataset:
            tree_node.setCheckState(0, Qt.CheckState.Unchecked)
        if parent_node is not None:
            parent_node.addChild(tree_node)
        else:
            self.addTopLevelItem(tree_node)
        return tree_node

    def recursivePopulateTree(self, node_data, parent_node=None):
        node = self.add(node_data, parent_node)
        if type(node_data) == h5py.Group:
            for children in node_data.itervalues():
                self.recursivePopulateTree(children, node)

    def all_dataset_elements(self):
        ''' returns all the elements in the tree'''
        elements = []
        roots = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        for r in roots:
            entries = [r.child(i) for i in range(r.childCount())]
            topleveldatasets = [x for x in entries if type(x.getData()) == h5py.Dataset]
            elements.extend(topleveldatasets)
            for entry in entries:
                datasets = [entry.child(i) for i in range(entry.childCount())]
                elements.extend(datasets)
        return elements

    def all_checked_dataset_elements(self):
        dataset_items = self.all_dataset_elements()
        return [x.getData() for x in dataset_items if x.checkState(0) == Qt.Checked]











