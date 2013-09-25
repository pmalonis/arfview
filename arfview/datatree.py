'''
datatree.py

This file contains aspects of arf model and it's associated view DataTreeView

'''

from PySide import QtGui
from PySide.QtCore import Qt
from datetime import datetime
from dateutil import tz
import h5py

named_types = {0 : 'UNDEFINED', 1 : 'ACOUSTIC', 2 : 'EXTRAC_HP', 3 : 'EXTRAC_LF',
               4 : 'EXTRAC_EEG', 5 : 'INTRAC_CC', 6 : 'INTRAC_VC',
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
        return('foo')
    time = datetime.fromtimestamp(entry.attrs['timestamp'][0] + entry.attrs['timestamp'][1] * 1e-6,
                                  tz.tzutc()).astimezone(tz.tzlocal())
    return time.strftime('%Y-%m-%d, %H:%M:%S:%f')


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
        self.setCheckState(1, Qt.CheckState.Unchecked)

    def getData(self):
        ''' use this to access the arf data in a DataTreeItem '''
        return self.data(0, Qt.UserRole)()


class DataTreeView(QtGui.QTreeWidget):
    ''' a tree for storing data, both in hdf5 and other formats '''
    def __init__(self, *args, **kwargs):
        super(DataTreeView, self).__init__(*args, **kwargs)
        self.setColumnCount(5)
        self.setHeaderLabels(('Name', 'Plot', 'Type', 'Time', 'File'))

    def add(self, data, parent_node=None):
        '''creates a DataTreeItem from data and returns it'''
        # assuming arf for now
        str_type = get_str_type(data)
        if type(data) == h5py.Group:
            str_time = get_str_time(data)
        else: str_time = ''
        fname = data.file.filename
        tree_node = DataTreeItem(data, [data.name, '', str_type, str_time, fname])
        tree_node.setData(0, Qt.UserRole, Model(data))
        tree_node.setCheckState(1, Qt.CheckState.Unchecked)
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



















