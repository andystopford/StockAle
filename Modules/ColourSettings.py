from PyQt4 import QtGui

class ColourSettings(QtGui.QGroupBox):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        """User-changeable colours for YearView"""
        self.setTitle('File View Colours')
        self.setToolTip('Choose Colours For File View, Search Results, etc.')
        colours = Colours()
        self.parent = parent
        self.weekday_col = colours.get_weekday()
        self.weekend_col = colours.get_weekend()
        self.brewday_col = colours.get_brewday()
        self.searchday_col = colours.get_searchday()

        self.weekday_swatch = QtGui.QPushButton()
        self.weekday_swatch.clicked.connect(self.set_weekday)
        self.weekend_swatch = QtGui.QPushButton()
        self.weekend_swatch.clicked.connect(self.set_weekend)
        self.brewday_swatch = QtGui.QPushButton()
        self.brewday_swatch.clicked.connect(self.set_brew)
        self.search_swatch = QtGui.QPushButton()
        self.search_swatch.clicked.connect(self.set_search)
        self.button_apply = QtGui.QPushButton('Apply')
        self.button_apply.clicked.connect(self.apply)
        self.button_defaults = QtGui.QPushButton('Reset Defaults')
        self.button_defaults.clicked.connect(self.defaults)

        # Layout
        container = QtGui.QVBoxLayout()
        box = QtGui.QGridLayout()
        self.setLayout(container)
        container.addLayout(box)
        container.setMargin(10)

        box.addWidget(self.weekday_swatch, 0, 0)
        box.addWidget(QtGui.QLabel('Weekdays'), 0, 1)

        box.addWidget(self.weekend_swatch, 1, 0)
        box.addWidget(QtGui.QLabel('Weekends'), 1, 1)

        box.addWidget(self.brewday_swatch, 2, 0)
        box.addWidget(QtGui.QLabel('Brew Day'), 2, 1)

        box.addWidget(self.search_swatch, 3, 0)
        box.addWidget(QtGui.QLabel('Search Result'), 3, 1)

        spare_box = QtGui.QWidget()
        container.addWidget(spare_box)

        button_layout = QtGui.QHBoxLayout()
        container.addLayout(button_layout)
        button_layout.addWidget(self.button_apply)
        button_layout.addWidget(self.button_defaults)

    def set_weekday(self):
        """Use QColorDialog to set background colour"""
        colour = QtGui.QColorDialog.getColor(self.weekday_col)
        ss = "background-color:rgb" + str(colour.getRgb())
        self.weekday_swatch.setStyleSheet(ss)
        self.weekday_col = colour

    def set_weekend(self):
        """Use QColorDialog to set background colour"""
        colour = QtGui.QColorDialog.getColor(self.weekend_col)
        ss = "background-color:rgb" + str(colour.getRgb())
        self.weekend_swatch.setStyleSheet(ss)
        self.weekend_col = colour

    def set_brew(self):
        """Use QColorDialog to set background colour"""
        colour = QtGui.QColorDialog.getColor(self.brewday_col)
        ss = "background-color:rgb" + str(colour.getRgb())
        self.brewday_swatch.setStyleSheet(ss)
        self.brewday_col = colour

    def set_search(self):
        """Use QColorDialog to set background colour"""
        colour = QtGui.QColorDialog.getColor(self.searchday_col)
        ss = "background-color:rgb" + str(colour.getRgb())
        self.search_swatch.setStyleSheet(ss)
        self.searchday_col = colour

    def apply(self):
        """Apply new colours to models"""
        for year in self.parent.model_dict:
            model = self.parent.model_dict[year]
            model.refresh_colours()
            self.parent.search()

    def defaults(self):
        colours = Colours()
        self.weekday_swatch.setStyleSheet(colours.get_weekday_ss())
        self.weekend_swatch.setStyleSheet(colours.get_weekend_ss())
        self.brewday_swatch.setStyleSheet(colours.get_brewday_ss())
        self.search_swatch.setStyleSheet(colours.get_searchday_ss())
        self.weekday_col = colours.get_weekday()
        self.weekend_col = colours.get_weekend()
        self.brewday_col = colours.get_brewday()
        self.searchday_col = colours.get_searchday()
        
        
class Colours:
    def __init__(self):
        """Default UI colours"""
        self.weekday = QtGui.QColor("#C3DAFF")
        self.weekend = QtGui.QColor("#A0C3FF")
        self.brewday = QtGui.QColor("#FDA07F")
        self.searchday = QtGui.QColor("#95FF99")
        self.weekday_ss = "background-color:#C3DAFF"
        self.weekend_ss = "background-color:#A0C3FF"
        self.brewday_ss = "background-color:#FDA07F"
        self.searchday_ss = "background-color:#95FF99"
       
    # get QColors 
    def get_weekday(self):
        return self.weekday
    
    def get_weekend(self):
        return self.weekend
    
    def get_brewday(self):
        return self.brewday
    
    def get_searchday(self):
        return self.searchday
    
    # Get Stylesheets
    def get_weekday_ss(self):
        return self.weekday_ss

    def get_weekend_ss(self):
        return self.weekend_ss

    def get_brewday_ss(self):
        return self.brewday_ss

    def get_searchday_ss(self):
        return self.searchday_ss
