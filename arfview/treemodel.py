from pyside import QtCore, QtGui


class TreeModel(QtCore.AbstractItemModel):
    def __init__(self, data, parent=None):
        super(TreeModel, self).__init__(parent)
        self.rootItem = 
        self.name = name
        self.children = []
        self.parent = parent

        if parent is not None:
            self.parent.addChild(slef)

    def addChild(self, child):
        self.children.append(child)

    def name(self):
        return self.name

    def childCount(self, row):
        return len(self.children)

    def parent(self):
        return self.parent

    def row(self):
        if self.parent is not None:
            return self.parent.children.index(self)


    