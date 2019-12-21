#!/usr/bin/python3.6
import sys

from PyQt4 import QtGui, Qt
from StockAle import MainWindow


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    splash_pix = QtGui.QPixmap("./Pint_splash.png")
    splash = QtGui.QSplashScreen(splash_pix, Qt.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    myapp = MainWindow()
    myapp.show()
    myapp.load_data()
    myapp.startup()
    splash.finish(myapp)
    sys.exit(app.exec_())
