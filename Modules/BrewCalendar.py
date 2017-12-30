from PyQt4 import QtGui


class BrewCalendar(QtGui.QCalendarWidget):
    def __init__(self):
        QtGui.QCalendarWidget.__init__(self)
        """ Sub-classed QCalendar provides ability to colour code cells."""
        self.setHorizontalHeaderFormat(QtGui.QCalendarWidget.
                                       SingleLetterDayNames)
        self.color = QtGui.QColor(self.palette().
                                  color(QtGui.QPalette.Highlight))
        self.color.setRgb(0, 0, 255)
        self.color.setAlpha(64)
        self.dateList = []
        self.setGridVisible(True)

    def paintCell(self, painter, rect, date):
        """ Colour in cells."""
        QtGui.QCalendarWidget.paintCell(self, painter, rect, date)
        if date in self.dateList:
            painter.fillRect(rect, self.color)

    def dates(self, dateList):
        """ Set list of dates to colour."""
        self.dateList = dateList



