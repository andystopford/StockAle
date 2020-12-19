from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QCalendarWidget

class BrewCalendar(QCalendarWidget):
    def __init__(self):
        super().__init__()
        """ Sub-classed QCalendar provides ability to colour code cells.
        Used by SaveDialogue"""
        self.setHorizontalHeaderFormat(QCalendarWidget.
                                       SingleLetterDayNames)
        self.color = QColor(self.palette().
                                  color(QPalette.Highlight))
        self.color.setRgb(0, 0, 255)
        self.color.setAlpha(64)
        self.date_list = []
        self.setGridVisible(True)

    def paintCell(self, painter, rect, date):
        """ Colour in cells."""
        super().paintCell(painter, rect, date)
        if date in self.date_list:
            painter.fillRect(rect, self.color)

    def dates(self, date_list):
        """ Set list of dates to colour."""
        self.date_list = date_list



