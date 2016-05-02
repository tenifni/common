import sys
from PyQt4 import QtGui, QtCore
from common.lib.clients.qtui.QCustomPowerMeter import MQProgressBar
from common.lib.clients.qtui.QCustomSlideIndicator import SlideIndicator

class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setMinimumSize(QtCore.QSize(350, 100))

    def resizeEvent(self, evt):

        font = self.font()
        font.setPixelSize(self.width() * 0.14 - 14 )
        self.setFont(font)

class TextChangingButton(QtGui.QPushButton):
    """Button that changes its text to ON or OFF and colors when it's pressed"""
    def __init__(self, addtext = None, parent = None):
        super(TextChangingButton, self).__init__(parent)
        self.setCheckable(True)
        self.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=10))
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.setMaximumHeight(30)
        #connect signal for appearance changing
        self.addtext = addtext
        if self.addtext == None:
            self.addtext = ''
        else:
            self.addtext = self.addtext + '   '
        self.toggled.connect(self.setAppearance)
        self.setAppearance(self.isDown())

    def setAppearance(self, down, addtext = None):
        if down:
            self.setText(self.addtext + 'On')
            self.setPalette(QtGui.QPalette(QtCore.Qt.darkGreen))
        else:
            self.setText(self.addtext + 'Off')
            self.setPalette(QtGui.QPalette(QtCore.Qt.black))
    def sizeHint(self):
        return QtCore.QSize(37, 26)

class QCustomWavemeterChannel(QtGui.QFrame):
    def __init__(self, chanName, wmChannel, DACPort, frequency, stretchedlabel, displayPIDvoltage = None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout(chanName, wmChannel, DACPort, frequency, stretchedlabel, displayPIDvoltage)

    def makeLayout(self, name, wmChannel, DACPort, frequency, stretchedlabel, displayPIDvoltage):
        layout = QtGui.QGridLayout()
        
        chanName = QtGui.QLabel(name)
        chanName.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        chanName.setAlignment(QtCore.Qt.AlignCenter)
        
        configtitle = QtGui.QLabel('WLM Connections:')
        configtitle.setAlignment(QtCore.Qt.AlignBottom)
        configtitle.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=13))
        
        configLabel = QtGui.QLabel("Channel " + str(wmChannel) + '        ' + "DAC Port " + str(DACPort))
        configLabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=8))
        configLabel.setAlignment(QtCore.Qt.AlignCenter)
        

        self.PIDvoltage = QtGui.QLabel('DAC Voltage (mV)  -.-')
        self.PIDvoltage.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=12))
        
        if displayPIDvoltage:
            self.PIDindicator = SlideIndicator([-10.0,10.0])
        
        self.powermeter = MQProgressBar()
        self.powermeter.setOrientation(QtCore.Qt.Vertical)
        self.powermeter.setMeterColor("orange","red")
        self.powermeter.setMeterBorder("orange")
        
        if displayPIDvoltage == True:
            layout.addWidget(self.PIDvoltage,   6,2,1,1)
            layout.addWidget(self.PIDindicator, 5,2,1,1)
        if stretchedlabel == True:
            self.currentfrequency = StretchedLabel(frequency)
        else:
            self.currentfrequency = QtGui.QLabel(frequency)
            
        self.currentfrequency.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=60))
        self.currentfrequency.setAlignment(QtCore.Qt.AlignCenter)
        self.currentfrequency.setMinimumWidth(600)

        frequencylabel = QtGui.QLabel('Set Frequency')
        frequencylabel.setAlignment(QtCore.Qt.AlignBottom)
        frequencylabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=13))
        
        exposurelabel = QtGui.QLabel('Set Exposure (ms)')
        exposurelabel.setAlignment(QtCore.Qt.AlignBottom)
        exposurelabel.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=13))
        
        self.setPID = QtGui.QPushButton('Set PID')
        self.setPID.setMaximumHeight(30)
        self.setPID.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=10))
        
        self.measSwitch = TextChangingButton('WLM Measure')
        
        self.lockChannel = TextChangingButton('Lock Channel')
        self.lockChannel.setMinimumWidth(180)
        
        #editable fields
        self.spinFreq = QtGui.QDoubleSpinBox()
        self.spinFreq.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        self.spinFreq.setDecimals(6)
        self.spinFreq.setSingleStep(0.000001)
        self.spinFreq.setRange(100.0,1000.0)
        self.spinFreq.setKeyboardTracking(False)
        
        self.spinExp = QtGui.QDoubleSpinBox()
        self.spinExp.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        self.spinExp.setDecimals(0)
        self.spinExp.setSingleStep(1)
        self.spinExp.setRange(0, 2000.0)
        self.spinExp.setKeyboardTracking(False)
        
        layout.addWidget(self.spinFreq,         6, 0)
        layout.addWidget(self.spinExp,          6, 1)
        layout.addWidget(self.measSwitch,       0, 2)
        layout.addWidget(self.lockChannel,      1,2,1,1)
        layout.addWidget(self.setPID,           2,2,1,1)
        layout.addWidget(chanName,              0,0,1,2)
        layout.addWidget(configtitle,           3,2,1,1)        
        layout.addWidget(configLabel,           4,2,1,1)
        layout.addWidget(self.currentfrequency, 1, 0, 4, 2)
        layout.addWidget(frequencylabel,        5, 0, 1, 1)
        layout.addWidget(exposurelabel,         5, 1, 1, 1)
        layout.addWidget(self.powermeter,       0,3,7,1)

        layout.minimumSize()

        self.setLayout(layout)

    def setExpRange(self, exprange):
        self.spinExp.setRange(exprange)

    def setFreqRange(self, freqrange):
        self.spinFreq.setRange(freqrange)


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomWavemeterChannel('Repumper',1, 4, 'Under Exposed', False, True)
    icon.show()
    app.exec_()
