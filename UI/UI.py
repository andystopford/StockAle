import sys
sys.path.append("./Modules")
sys.path.append("./Data")

from PyQt4 import QtCore, QtGui, Qt
from ControlGroup import ControlGroup
from YearView import YearView
from Preferences import Preferences
from ColourSettings import ColourSettings
from Calculators import Calculators

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, parent_window):
        self.central_widget = QtGui.QWidget(parent_window)
        parent_window.setCentralWidget(self.central_widget)
        # the basic layout:
        central_layout = QtGui.QGridLayout()
        central_splitter = QtGui.QSplitter(Qt.Qt.Vertical)  # Below tabbed area
        central_splitter.setSizes([300, 800])
        central_layout.addWidget(central_splitter)
        self.central_widget.setLayout(central_layout)
        self.tabbed_area = QtGui.QTabWidget()
        central_splitter.addWidget(self.tabbed_area)

        # Tabbed Area
        # Stock group
        self.grain_stock = QtGui.QTableWidget()
        self.grain_stock.setColumnCount(4)
        self.grain_stock.setRowCount(12)
        self.grain_stock.setHorizontalHeaderLabels(['Grain', 'EBC',
                                                    'Extract L/Kg.', 'Kg.'])
        self.grain_stock.verticalHeader().setVisible(False)
        self.grain_stock.setAlternatingRowColors(True)
        self.grain_stock.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        gr_stck_header = self.grain_stock.horizontalHeader()
        gr_stck_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.hop_stock = QtGui.QTableWidget()
        self.hop_stock.setColumnCount(3)
        self.hop_stock.setRowCount(12)
        self.hop_stock.setHorizontalHeaderLabels(['Hop', 'Alpha', 'Grams'])
        self.hop_stock.verticalHeader().setVisible(False)
        self.hop_stock.setAlternatingRowColors(True)
        self.hop_stock.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        hop_stck_header = self.hop_stock.horizontalHeader()
        hop_stck_header.setResizeMode(QtGui.QHeaderView.Stretch)
        
        recipe_tab = QtGui.QWidget()
        self.tabbed_area.addTab(recipe_tab, 'Recipe')
        recipe_layout = QtGui.QVBoxLayout()
        recipe_tab.setLayout(recipe_layout)
        stock_layout = QtGui.QHBoxLayout()
        stock_layout.addWidget(self.grain_stock)
        stock_layout.addWidget(self.hop_stock)
        recipe_layout.addLayout(stock_layout)
        # Recipe
        self.recipe_box = QtGui.QGroupBox('Current Recipe')
        curr_recipe_layout = QtGui.QHBoxLayout()
        self.recipe_box.setLayout(curr_recipe_layout)
        self.rcg = ControlGroup('new')
        curr_recipe_layout.addWidget(self.rcg)
        recipe_layout.addWidget(self.recipe_box)

        # File group
        file_tab = QtGui.QWidget()
        self.tabbed_area.addTab(file_tab, 'Files')
        # Top button bar
        self.button_back = QtGui.QPushButton("<<")
        self.button_forward = QtGui.QPushButton(">>")
        self.label_year = QtGui.QLabel()
        top_button_widget = QtGui.QWidget()
        top_button_layout = QtGui.QHBoxLayout()
        top_button_widget.setLayout(top_button_layout)
        top_button_layout.addWidget(self.button_back)
        top_button_layout.addWidget(self.label_year)
        top_button_layout.addWidget(self.button_forward)
        self.label_year.setAlignment(Qt.Qt.AlignCenter)
        # Year view
        self.yearView = YearView(parent_window)

        file_layout = QtGui.QVBoxLayout()
        file_tab.setLayout(file_layout)
        file_layout.addWidget(top_button_widget)
        file_layout.addWidget(self.yearView)
        # Search
        search_layout = QtGui.QHBoxLayout()
        search_panel = QtGui.QWidget()
        label_search = QtGui.QLabel('Search For...')
        label_results = QtGui.QLabel('Results')
        label_filter = QtGui.QLabel('Filter By Rating')
        label_filter.setAlignment(QtCore.Qt.AlignRight)
        plus_minus = chr(0x00B1)
        label_plus_minus = QtGui.QLabel(plus_minus)
        font = label_plus_minus.font()
        font.setPixelSize(20)
        label_plus_minus.setFont(font)
        label_plus_minus.setAlignment(QtCore.Qt.AlignRight)
        self.search_box = QtGui.QLineEdit()
        self.results_box = QtGui.QLineEdit()
        self.button_clear = QtGui.QPushButton('Clear')
        self.rating_plus_minus = QtGui.QSpinBox()
        self.rating_input = QtGui.QSpinBox()
        self.button_search = QtGui.QPushButton('Search')
        self.button_search.setMinimumWidth(100)
        self.button_clear.setMinimumWidth(100)
        search_layout.addWidget(label_search)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.button_search)

        search_layout.addWidget(self.button_clear)
        search_layout.addWidget(label_filter)
        search_layout.addWidget(self.rating_input)
        search_layout.addWidget(label_plus_minus)
        search_layout.addWidget(self.rating_plus_minus)
        search_layout.addWidget(label_results)
        search_layout.addWidget(self.results_box)
        search_layout.addWidget(self.button_clear)

        search_panel.setLayout(search_layout)
        file_layout.addWidget(search_panel)

        # Settings Group
        settings_tab = QtGui.QWidget()
        self.tabbed_area.addTab(settings_tab, 'Settings')
        settings_layout = QtGui.QHBoxLayout()
        settings_tab.setLayout(settings_layout)
        # Next line has to be before preferences to all preferences to load
        # colour settings
        self.colourSettings = ColourSettings(parent_window)
        preferences = Preferences(parent_window)
        settings_layout.addWidget(preferences)
        preferences.setMaximumWidth(400)
        settings_layout.addWidget(self.colourSettings)
        self.colourSettings.setMaximumWidth(400)
        calculators = Calculators()
        settings_layout.addWidget(calculators)
        calculators.setMaximumWidth(400)

        spare_box = QtGui.QGroupBox()
        settings_layout.addWidget(spare_box)

    #######################################################################
        # History
        history_area = QtGui.QWidget()
        history_layout = QtGui.QVBoxLayout()
        history_area.setLayout(history_layout)
        central_splitter.addWidget(history_area)
        self.date_box = QtGui.QGroupBox('Date')
        date_layout = QtGui.QVBoxLayout()
        self.date_box.setLayout(date_layout)
        sel_recipe_layout = QtGui.QHBoxLayout()
        date_layout.addLayout(sel_recipe_layout)
        self.hcg = ControlGroup('history')
        sel_recipe_layout.addWidget(self.hcg)
        history_layout.addWidget(self.date_box)

        # Notes
        notes_layout = QtGui.QHBoxLayout()
        date_layout.addLayout(notes_layout)
        self.process_notes = QtGui.QTextEdit()
        proc_note_box = QtGui.QGroupBox('Process Notes')
        proc_notes_layout = QtGui.QVBoxLayout()
        proc_note_box.setLayout(proc_notes_layout)
        proc_notes_layout.addWidget(self.process_notes)
        notes_layout.addWidget(proc_note_box)

        self.tasting_notes = QtGui.QTextEdit()
        tast_note_box = QtGui.QGroupBox('Tasting Notes')
        tast_notes_layout = QtGui.QVBoxLayout()
        tast_note_box.setLayout(tast_notes_layout)
        tast_notes_layout.addWidget(self.tasting_notes)
        notes_layout.addWidget(tast_note_box)

        info_box = QtGui.QGroupBox()
        info_layout = QtGui.QVBoxLayout()
        info_box.setLayout(info_layout)
        notes_layout.addWidget(info_box)

        label_rating = QtGui.QLabel('Rating')
        self.rating = QtGui.QSpinBox()
        self.box_style = QtGui.QComboBox()
        self.box_style.setMinimumWidth(160)
        style_layout = QtGui.QHBoxLayout()
        style_layout.addWidget(self.box_style)
        style_layout.addWidget(label_rating)
        style_layout.addWidget(self.rating)
        info_layout.addLayout(style_layout)

        brew_date_box = QtGui.QGroupBox('Date Brewed')
        self.brew_date = QtGui.QLabel()
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        bold_font.setPixelSize(16)
        self.brew_date.setFont(bold_font)
        brew_date_layout = QtGui.QVBoxLayout()
        brew_date_box.setLayout(brew_date_layout)
        brew_date_layout.addWidget(self.brew_date)
        self.brew_date.setAlignment(QtCore.Qt.AlignCenter)
        since_brew_box = QtGui.QGroupBox('Time Since Brewing')
        self.since_brew = QtGui.QLabel()
        self.since_brew.setFont(bold_font)
        since_brew_layout = QtGui.QVBoxLayout()
        since_brew_box.setLayout(since_brew_layout)
        since_brew_layout.addWidget(self.since_brew)
        self.since_brew.setAlignment(QtCore.Qt.AlignCenter)
        info_layout.addWidget(brew_date_box)
        info_layout.addWidget(since_brew_box)
        self.brew_date.setStyleSheet("""QLabel{
                Background-color:#42464a}""")
        self.since_brew.setStyleSheet("""QLabel{
                Background-color:#42464a}""")



























