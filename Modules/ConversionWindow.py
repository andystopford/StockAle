from PyQt4 import QtGui
from correctOG import Ui_Dialog


class ConversionWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        """ A dialogue box for temperature compensation calculation
        of hydrometer readings.
        """
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.resize(205, 200)
        self.ui.button_calc.clicked.connect(self.calc)
        self.ui.box_calTemp.setValue(20)
        self.setWindowTitle("Hydrometer Correction")

    def calc(self):
        mg = self.ui.box_mesrOG.value()     # measured sg
        tr = self.ui.box_mesrTemp.value()   # temp at measured sg
        tc = self.ui.box_calTemp.value()    # calibration temp

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
        self.ui.box_corrOG.setValue(cg)