from BrewCalendar import BrewCalendar
from PyQt5 import QtCore, QtWidgets


class SaveDialogue(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        """ Popup dialogue to save the current brew, with calendar for 
        selecting brew-day/filename.
        """
        self.brew_calendar = BrewCalendar()
        self.parent = parent
        central_layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QVBoxLayout()
        grp_box_layout = QtWidgets.QVBoxLayout()
        name_box = QtWidgets.QGroupBox('Saving As:')
        self.button_save = QtWidgets.QPushButton('Save')
        self.name_disp = QtWidgets.QTextEdit()
        self.name_disp.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.name_disp.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.name_disp.setMaximumHeight(25)

        self.setLayout(central_layout)
        central_layout.addWidget(self.brew_calendar)
        central_layout.addLayout(button_layout)
        button_layout.addWidget(name_box)
        name_box.setLayout(grp_box_layout)
        grp_box_layout.addWidget(self.name_disp)
        button_layout.addWidget(self.button_save)

        self.button_save.clicked.connect(self.save)
        self.brew_calendar.clicked.connect(self.select_date)

        self.brew = ""
        self.date = ""

    def save(self):
        self.parent.save_brew(self.brew, self.date)
        self.parent.brew_dirty = False
        self.close()

    def select_date(self, date):
        """ Select date from calendar and generate filename."""
        day = date.day()
        month = date.month()
        month = date.shortMonthName(month)
        year = date.year()
        year = str(year - 2000)
        month = str(month)
        if day < 10:
            day = "0" + str(day)
        day = str(day)
        self.brew = day + month + year
        brew = "<html><head/><body><p align=center>" \
               + self.brew + "</p></body></html>"
        self.name_disp.setText(brew)
        self.date = date
