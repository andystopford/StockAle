import time
import itertools
import calendar


class Year:
    def __init__(self, year):
        """ Make list of the year's dates sorted by month """
        self.cal = calendar.Calendar()
        self.year = year

    def get_months(self):
        """Returns list of months; each month is a 37 member-long list of
        dates, padded with nulls to arrange the dates in the correct columns
        of the YearView"""
        month_list = []
        for month in range(1, 13):
            days = self.cal.monthdayscalendar(self.year, month)
            days = list(itertools.chain(*days))  # 12 lists of dates
            for n, i in enumerate(days):
                if i == 0:
                    days[n] = ''  # Removes Zeros at beginning of month
            days += [''] * (37 - len(days))  # pads list to fill table
            month_list.append(days)
        return month_list

    def get_column(self, month, day):
        """Gets the column for a specified date"""
        days = self.cal.monthdayscalendar(int(self.year), month)
        merged = list(itertools.chain.from_iterable(days))
        col = merged.index(day)
        return col

    def get_today(self):
        """Returns row and Column of today's date, to be highlighted in
        this year's model"""
        date = time.strftime("%d/%m/%Y")
        if int(date[6:10]) == self.year:
            day = int(date[0:2])
            month = int(date[3:5])
            col = self.get_column(month, day)
            row = month - 1
            return col, row




