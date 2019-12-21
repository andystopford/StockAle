from PyQt4 import QtGui

class Calculators(QtGui.QGroupBox):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        """ Temperature compensation calculation
        of hydrometer readings.
        """
        self.setTitle('Calculators')
        container = QtGui.QVBoxLayout()
        OG_box = QtGui.QGridLayout()
        self.setLayout(container)
        container.addLayout(OG_box)
        OG_box.setMargin(10)

        self.OG_box_calTemp = QtGui.QSpinBox()
        OG_box.addWidget(self.OG_box_calTemp, 0, 0, 1, 1)
        label_calibT = QtGui.QLabel(
            "<html><head/><body><p>Calibration Temp °C</p></body></html>")
        OG_box.addWidget(label_calibT, 0, 1, 1, 1)

        self.OG_box_mesrTemp = QtGui.QSpinBox()
        OG_box.addWidget(self.OG_box_mesrTemp, 1, 0, 1, 1)
        label_mesrT = QtGui.QLabel(
            "<html><head/><body><p>Measured Temp °C</p></body></html>")
        OG_box.addWidget(label_mesrT, 1, 1, 1, 1)

        self.OG_box_mesrOG = QtGui.QSpinBox()
        OG_box.addWidget(self.OG_box_mesrOG, 2, 0, 1, 1)
        label_mesrOG = QtGui.QLabel('Measured OG')
        OG_box.addWidget(label_mesrOG, 2, 1, 1, 1)

        self.OG_box_corrOG = QtGui.QSpinBox()
        OG_box.addWidget(self.OG_box_corrOG, 3, 0, 1, 1)
        label_corrOG = QtGui.QLabel('Corrected OG')
        OG_box.addWidget(label_corrOG, 3, 1, 1, 1)

        self.button_calc = QtGui.QPushButton("Calculate")
        OG_box.addWidget(self.button_calc)
        
        self.button_calc.clicked.connect(self.calc)
        self.OG_box_calTemp.setValue(20)

        spare_box = QtGui.QWidget()
        container.addWidget(spare_box)


    def calc(self):
        mg = self.OG_box_mesrOG.value()     # measured sg
        tr = self.OG_box_mesrTemp.value()   # temp at measured sg
        tc = self.OG_box_calTemp.value()    # calibration temp

        mg = mg / float(1000) + 1
        tr = ((tr * 9) / 5) + 32
        tc = ((tc * 9) / 5) + 32
        # cg = Corrected gravity
        cg = mg * ((1.00130346 - 0.000134722124 * tr + 0.00000204052596
                    * tr**2 - 0.00000000232820948 * tr**3) /
                   (1.00130346 - 0.000134722124 * tc + 0.00000204052596
                    * tc**2 - 0.00000000232820948 * tc**3))
        cg = (cg - 1) * 1000
        cg = round(cg)
        self.OG_box_corrOG.setValue(cg)