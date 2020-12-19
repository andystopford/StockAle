from itertools import cycle, islice

from PyQt5 import Qt
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from Year import Year


class Model(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        """Data for one year - generates date numbers to display in YearView,
        and colours them according to weekday/weekend, is a brew day, and 
        searched for"""
        self.setRowCount(12)
        self.setColumnCount(37)
        self.colourSettings = parent.ui.colourSettings

    def setup(self):
        """Labels headers and inserts QStandardItems in each cell. Each
        day item contains two child items - one for an 'is searched for' flag
        and one for the search background colour. This allows future
        implementation of multiple search colours"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                  "Sep", "Oct", "Nov", "Dec"]
        self.setVerticalHeaderLabels(months)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        days_cycle = cycle(days)
        nth = lambda i, n, d=None: next(islice(i, n, None), d)
        day_labels = [nth(days_cycle, 0) for _ in range(37)]
        self.setHorizontalHeaderLabels(day_labels)
        # Colour weekends and weekdays differently and insert
        # QStandardItems in each:
        for row in range(12):
            for col in range(37):
                if (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
                    # Weekends
                    day = QStandardItem()
                    self.setItem(row, col, day)
                    is_brew = QStandardItem()
                    is_brew.data = False
                    day.setChild(0, 0, is_brew)
                    is_searched = QStandardItem()
                    is_searched.setData(False)
                    day.setChild(0, 1, is_searched)
                    search_bground = QStandardItem()
                    search_bground.setData(self.colourSettings.searchday_col)
                    self.item(row, col).setBackground(self.colourSettings.
                                                      weekend_col)
                else:
                    # Weekdays
                    day = QStandardItem()
                    self.setItem(row, col, day)
                    is_brew = QStandardItem()
                    is_brew.data = False
                    day.setChild(0, 0, is_brew)
                    is_searched = QStandardItem()
                    is_searched.setData(False)
                    day.setChild(0, 1, is_searched)
                    search_bground = QStandardItem()
                    search_bground.setData(self.colourSettings.searchday_col)
                    self.item(row, col).setBackground(self.colourSettings.
                                                      weekday_col)

    def set_year(self, year):
        """Fills in date numbers and colours background of brews and searched
        for dates"""
        year_instance = Year(year)
        months = year_instance.get_months()
        today = False
        colour = Qt.QColor('black')
        if year_instance.get_today():
            today = year_instance.get_today()
        for month_num in range(12):
            curr_month = month_num
            month = months[month_num]
            for date in range(len(month)):
                curr_date = date
                date = month[date]
                item = self.item(curr_month, curr_date)
                item_text = str(date)
                if item is not None:
                    if item.child(0, 0) == True:
                        # Is a brew
                        item.setBackground(self.colourSettings.brewday_col)
                    if item.child(0, 1).data == True:
                        # Identified in search
                        item.setBackground(self.colourSettings.searchday_col)
                    # Set text
                    if today:
                        if today[0] == curr_date and today[1] == curr_month:
                            # Highlight today
                            colour = Qt.QColor('red')
                            item.setFont(QFont('Sans Serif', 15, QFont.Bold))
                        else:
                            colour = Qt.QColor('black')
                    item.setForeground(colour)
                    item.setText(item_text)
                    item.setTextAlignment(Qt.Qt.AlignCenter)
                    # Make the QDate a child of the day
                    if date is not '':
                        date = int(date)
                        now = QDate(year, curr_month + 1, date)
                        date = QStandardItem()
                        item.setChild(0, 1, date)
                        date.setData(now)

    def refresh_colours(self):
        """Redraws cell backgrounds after changes applied in colourSettings"""
        for row in range(12):
            for col in range(37):
                item = self.item(row, col)
                if item.child(0, 0).data == True:
                    item.setBackground(self.colourSettings.brewday_col)
                elif item.child(0, 1).data == True:
                    item.setBackground(self.colourSettings.searchday_col)
                elif (col % 7) - 6 == 0 or (col % 7) - 5 == 0:
                    # Weekends
                    item.setBackground(self.colourSettings.weekend_col)
                else:
                    # Weekdays
                    item.setBackground(self.colourSettings.weekday_col)

    def add_brew(self, date):
        """Colour in brew dates and construct QStandardItem for is_brew flag"""
        year = date.year()
        month = date.month()
        day = date.day()
        colour = self.colourSettings.brewday_col
        year = Year(year)
        col = year.get_column(month, day)
        item = self.item(month-1, col)
        item.setBackground(colour)
        is_brew = item.child(0, 0)
        is_brew.data = True

    def display_search(self, date):
        """Colour search result backgrounds"""
        year = date.year()
        month = date.month()
        day = date.day()
        year = Year(year)
        col = year.get_column(month, day)
        item = self.item(month - 1, col)
        item.child(0, 1).data = True    # Flag for colouring background
        item.setBackground(self.colourSettings.searchday_col)

    def clear_search(self):
        """Sets search flag to false"""
        for index in range(self.rowCount()):
            item = self.item(index)
            item.child(0, 1).data = False


