from PyQt5 import QtWidgets

class Calculators(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        """ Temperature compensation calculation
        of hydrometer readings.
        """
        self.setTitle('Calculators')
        container = QtWidgets.QVBoxLayout()
        OG_box = QtWidgets.QGridLayout()
        OG_box.setColumnStretch(1, 1)
        self.setLayout(container)
        container.addWidget(QtWidgets.QLabel('OG and Temperature Correction'))
        container.addLayout(OG_box)
        #OG_box.setMargin(10)

        self.OG_box_calTemp = QtWidgets.QLineEdit()
        OG_box.addWidget(self.OG_box_calTemp, 0, 0, 1, 1)
        label_calibT = QtWidgets.QLabel(
            "<html><head/><body><p>Calibration Temp °C</p></body></html>")
        OG_box.addWidget(label_calibT, 0, 1, 1, 1)

        self.OG_box_mesrTemp = QtWidgets.QLineEdit()
        OG_box.addWidget(self.OG_box_mesrTemp, 1, 0, 1, 1)
        label_mesrT = QtWidgets.QLabel(
            "<html><head/><body><p>Measured Temp °C</p></body></html>")
        OG_box.addWidget(label_mesrT, 1, 1, 1, 1)

        self.box_brix = QtWidgets.QLineEdit()
        OG_box.addWidget(self.box_brix, 2, 0, 1, 1)
        self.box_brix.setToolTip('Enter measured refractometer value')
        label_brix = QtWidgets.QLabel('Brix')
        OG_box.addWidget(label_brix, 2, 1, 1, 1)

        self.OG_box_mesrOG = QtWidgets.QLineEdit()
        OG_box.addWidget(self.OG_box_mesrOG, 3, 0, 1, 1)
        self.OG_box_mesrOG.setToolTip('Enter measured hydrometer value. '
                                      'Brix entry takes priority')
        label_mesrOG = QtWidgets.QLabel('OG')
        OG_box.addWidget(label_mesrOG, 3, 1, 1, 1)

        self.OG_box_corrOG = QtWidgets.QLineEdit()
        OG_box.addWidget(self.OG_box_corrOG, 4, 0, 1, 1)
        label_corrOG = QtWidgets.QLabel('Corrected OG')
        OG_box.addWidget(label_corrOG, 4, 1, 1, 1)

        self.button_calc_og = QtWidgets.QPushButton("Calculate")
        OG_box.addWidget(self.button_calc_og)

        self.button_calc_og.clicked.connect(self.calc_og)
        self.OG_box_calTemp.setText('20')
        self.OG_box_mesrTemp.setText('20')

        container.addWidget(QtWidgets.QLabel('Alcohol By Volume - '
                                             'Enter Gravity or Brix'))
        abv_box = QtWidgets.QGridLayout()
        abv_box.setColumnStretch(1, 1)
        container.addLayout(abv_box)

        self.abv_box_og = QtWidgets.QLineEdit()
        abv_box.addWidget(self.abv_box_og, 0, 0)
        self.abv_box_og.setToolTip('If Gravity > 1.100, use Brix')
        label_abv_og = QtWidgets.QLabel('OG')
        abv_box.addWidget(label_abv_og, 0, 1)

        self.abv_box_fg = QtWidgets.QLineEdit()
        abv_box.addWidget(self.abv_box_fg, 1, 0)
        self.abv_box_fg.setToolTip('If Brix <= 1.1, use SG')
        label_abv_fg = QtWidgets.QLabel('FG')
        abv_box.addWidget(label_abv_fg, 1, 1)

        self.abv_box_abv = QtWidgets.QLineEdit()
        abv_box.addWidget(self.abv_box_abv, 2, 0)
        label_abv_abv = QtWidgets.QLabel('ABV')
        abv_box.addWidget(label_abv_abv, 2, 1)

        self.button_calc_abv = QtWidgets.QPushButton("Calculate")
        abv_box.addWidget(self.button_calc_abv, 3, 0)

        self.button_calc_abv.clicked.connect(self.calc_abv)

        spare_box = QtWidgets.QWidget()
        container.addWidget(spare_box)

    def calc_og(self):
        """Calculates temperature corrected OG. Measured gravity can be
        entered in either the Brix or OG boxes, the empty box will be filled;
        if both boxes are already filled, the Brix entry will take priority,
        modifying the value in OG"""
        try:
            brix = float(self.box_brix.text())  # Measured gravity in Brix
            mg = self.brix_to_sg(brix)
            self.OG_box_mesrOG.setText(str(mg))
        except:
            try:
                mg = float(self.OG_box_mesrOG.text())
                brix = self.sg_to_brix(mg)
                brix = round(brix, 1)
                self.box_brix.setText(str(brix))
            except:
                return
        tr = float(self.OG_box_mesrTemp.text())   # temp at measured sg
        tc = float(self.OG_box_calTemp.text())    # calibration temp
        # Convert to fahrenheit for formula
        tr = ((tr * 9) / 5) + 32
        tc = ((tc * 9) / 5) + 32
        # cg = Corrected gravity
        cg = mg * ((1.00130346 - 0.000134722124 * tr + 0.00000204052596
                    * tr**2 - 0.00000000232820948 * tr**3) /
                   (1.00130346 - 0.000134722124 * tc + 0.00000204052596
                    * tc**2 - 0.00000000232820948 * tc**3))
        cg = round(cg, 3)
        self.OG_box_corrOG.setText(str(cg))


    def brix_to_sg(self, brix):
        """Convert Brix measurement from refractometer to SG"""
        sg = (brix/(258.6-((brix/258.2)*227.1)))+1
        sg = round(sg, 3)
        return sg

    def sg_to_brix(self, sg):
        brix = (((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622)
        return brix

    def calc_abv(self):
        """Formula from here: https://www.brewersfriend.com/2011/06/16/alcohol
        -by-volume-calculator-updated/
        Brix or SG can be entered: if the value is greater than 1.1 Brix
        will be used, SG if <= 1.1"""
        try:
            try:
                og = float(self.abv_box_og.text())
                if og > 1.1:
                    og = self.brix_to_sg(og)
            except:
                self.abv_box_og.setText('Enter OG')
            try:
                fg = float(self.abv_box_fg.text())
                if fg > 1.1:
                    fg = self.brix_to_sg(fg)
            except:
                self.abv_box_fg.setText('Enter FG')
            abv = (76.08 * (og-fg) / (1.775-og)) * (fg / 0.794)
            abv = round(abv, 1)
            self.abv_box_abv.setText(str(abv))
        except:
            return

