from common.lib.clients.qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
try:
    from config.DDS_client_config import DDS_config
except:
    from common.lib.config.DDS_client_config import DDS_config
    
class DDSclient(QtGui.QWidget):

    def __init__(self, reactor, parent = None):
        """initializels the GUI creates the reactor 
            and empty dictionary for channel widgets to 
            be stored for iteration. also grabs chan info
            from wlm_client_config file 
        """     
        super(DDSclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.d = {}
        self.connect()

    @inlineCallbacks    
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "DDS client")
        self.server = yield self.cxn.dds_device_server
        self.reg = self.cxn.registry
        yield self.reg.cd('settings')
        self.settings = yield self.reg.dir()
        self.settings = self.settings[1]
        self.chaninfo = DDS_config.info
        self.initializeGUI()
        
    @inlineCallbacks
    def initializeGUI(self):      
        layout = QtGui.QGridLayout()
        from labrad.units import WithUnit as U
        self.U = U
        qBox = QtGui.QGroupBox('DDS Control')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)
        for chan in self.chaninfo:
            port = self.chaninfo[chan][0]
            position = self.chaninfo[chan][1]
            channel = self.chaninfo[chan][2]
            initfreq = self.chaninfo[chan][3]
            widget = QCustomFreqPower(chan) 
            MinPower =  self.U(-63, 'dbm')
            MaxPower =  self.U(-1.1625, 'dbm')
            MinFreq = self.U(0, 'MHz')
            MaxFreq = self.U(500, 'MHz')
            widget.setPowerRange((MinPower, MaxPower))
            widget.setFreqRange((MinFreq, MaxFreq))
            if chan in self.settings:
                value = yield self.reg.get(chan)
                initstate = value[0]
                initpower = value[1]
                initfreq = value[2]
            else:
                initstate = False
                initpower = MinPower
                initfreq = MaxFreq/2
            widget.setStateNoSignal(initstate)
            widget.setPowerNoSignal(initpower)
            widget.setFreqNoSignal(initfreq)
            widget.spinPower.valueChanged.connect(lambda value =  widget.spinPower.value(), port = port, channel = (chan, channel): self.powerChanged(value, port, channel))
            widget.spinFreq.valueChanged.connect(lambda value = widget.spinFreq.value(), port = port, channel = (chan, channel) : self.freqChanged(value, port, channel)) 
            widget.buttonSwitch.toggled.connect(lambda state = widget.buttonSwitch.isDown(), port = port, channel = (chan, channel) : self.switchChanged(state, port, channel))
            yield self.freqChanged(initfreq['MHz'], port, (chan, channel))
            yield self.powerChanged(initpower['dbm'], port, (chan, channel))
            self.d[port] = widget
            subLayout.addWidget(self.d[port], position[0], position[1])
        
        self.setLayout(layout)
    
    @inlineCallbacks
    def powerChanged(self, value, port, channel):
        value = self.U(value, 'dbm')
        name = channel[0]
        chan = channel[1]
        yield self.server.select_device(port)
        yield self.server.amplitude(chan, value)
        yield self.server.deselect_device()
        self.updateSettings(name, value, pos = 1)
        
    
    @inlineCallbacks
    def freqChanged(self, value, port, channel):
        value = self.U(value, 'MHz')
        name = channel[0]
        chan = channel[1]
        yield self.server.select_device(port)
        yield self.server.frequency(channel[1], value)
        yield self.server.deselect_device()
        self.updateSettings(name, value, pos = 2)
        
    @inlineCallbacks
    def switchChanged(self, state, port, channel):
        name = channel[0]
        chan = channel[1]
        yield self.server.select_device(port)
        yield self.server.output(channel[1], state)
        yield self.server.deselect_device()
        self.updateSettings(name, state, pos = 0)

    @inlineCallbacks
    def updateSettings(self, name, value, pos):
        if name in self.settings:
            setting = yield self.reg.get(name)
            setting = list(setting)
            setting[pos] = value
            setting = tuple(setting)
            yield self.reg.set(name, setting)
        
    def closeEvent(self, x):
        self.reactor.stop()
        
        
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    from common.lib.clients import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DDSWidget = DDSclient(reactor)
    DDSWidget.show()
    reactor.run()
        
        
