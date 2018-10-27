from PyQt5 import QtGui, QtWidgets, uic
import os

basepath =  os.path.dirname(__file__)
path = os.path.join(basepath,"..","..","Views", "StringEditor.ui")
base, form = uic.loadUiType(path)

class StringEditor(base, form):
    def __init__(self, parent=None):
        super(StringEditor, self).__init__(parent)
        self.setupUi(self)
        self._dataMapper = QtWidgets.QDataWidgetMapper(self)
        self.connect_layout()
        
    def connect_layout(self):
        pass
#        self.uiValue.clicked.connect(self.on_check)
    
#    def on_check(self):
#        self._dataMapper.itemDelegate().commitData.emit(self.uiValue)

    def setModel(self, proxyModel):
        self._proxyModel = proxyModel
        self._dataMapper.setModel(proxyModel.sourceModel())
        self._dataMapper.addMapping(self.uiName, 0)
        self._dataMapper.addMapping(self.uiCollection, 2)
        self._dataMapper.addMapping(self.uiValue, 3)

    def setSelection(self, current):
        parent = current.parent()
        self._dataMapper.setRootIndex(parent)
        self._dataMapper.setCurrentModelIndex(current)