
import sys
sys.path.append("./Modules")
sys.path.append("./Data")

from PyQt4 import QtCore, QtGui, Qt
from BrewCalendar import*
from ControlGroup import*

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
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.central_widget = QtGui.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.central_widget)
        bar = QtGui.QMenuBar()
        tools = bar.addMenu("Tools")
        self.prefs = QtGui.QAction("Preferences", tools)
        tools.addAction(self.prefs)
        self.hyd_corr = QtGui.QAction("Hydrometer Correction", tools)
        tools.addAction(self.hyd_corr)
        MainWindow.setMenuBar(bar)

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

        # the basic layout:
        central_layout = QtGui.QGridLayout()
        central_splitter = QtGui.QSplitter(Qt.Qt.Vertical)
        central_layout.addWidget(central_splitter)
        self.central_widget.setLayout(central_layout)

        # Stock group
        stock_box = QtGui.QGroupBox('Stock')
        central_splitter.addWidget(stock_box)
        stock_layout = QtGui.QHBoxLayout()
        stock_box.setLayout(stock_layout)
        stock_layout.addWidget(self.grain_stock)
        stock_layout.addWidget(self.hop_stock)

        # Brewery area
        brew_grp_split = QtGui.QSplitter(Qt.Qt.Horizontal)
        central_splitter.addWidget(brew_grp_split)
        brew_grp_split.setMinimumHeight(200)

        # File search group
        search_splitter = QtGui.QSplitter(Qt.Qt.Vertical)
        self.file_search = QtGui.QTabWidget()
        # Tabs - file
        tab_file = QtGui.QWidget()
        tab_file_layout = QtGui.QGridLayout()
        tab_file.setLayout(tab_file_layout)
        self.file_list = QtGui.QListWidget()
        tab_file_layout.addWidget(self.file_list)
        self.file_search.addTab(tab_file, 'File')
        # Tabs - search
        tab_search = QtGui.QWidget()
        tab_search_layout = QtGui.QVBoxLayout()
        tsl_filter_layout = QtGui.QHBoxLayout()
        tsl_filter = QtGui.QWidget()
        label_filter = QtGui.QLabel('Filter By Rating')
        label_filter.setAlignment(QtCore.Qt.AlignRight)
        plus_minus = chr(0x00B1)
        label_plus_minus = QtGui.QLabel(plus_minus)
        font = label_plus_minus.font()
        font.setPixelSize(20)
        label_plus_minus.setFont(font)
        label_plus_minus.setAlignment(QtCore.Qt.AlignRight)
        self.rating_plus_minus = QtGui.QSpinBox()
        self.rating_input = QtGui.QSpinBox()
        self.search_box = QtGui.QTextEdit()
        self.button_search = QtGui.QPushButton('Search')
        tsl_filter_layout.addWidget(label_filter)
        tsl_filter_layout.addWidget(self.rating_input)
        tsl_filter_layout.addWidget(label_plus_minus)
        tsl_filter_layout.addWidget(self.rating_plus_minus)
        tsl_filter.setLayout(tsl_filter_layout)
        tab_search_layout.addWidget(self.search_box)
        tab_search_layout.addWidget(tsl_filter)
        tab_search_layout.addWidget(self.button_search)
        self.file_search.addTab(tab_search, 'Search')
        tab_search.setLayout(tab_search_layout)
        # Tabs - calendar
        self.calendar = BrewCalendar()
        self.file_search.addTab(self.calendar, 'Calendar')

        # search results list
        self.search_results = QtGui.QListWidget()
        self.button_clear = QtGui.QPushButton('Clear')
        search_res_box = QtGui.QGroupBox('Search Results')
        search_res_box.setMaximumWidth(400)
        search_res_box.setMaximumHeight(300)
        search_res_layout = QtGui.QVBoxLayout()
        search_res_box.setLayout(search_res_layout)
        search_res_layout.addWidget(self.search_results)
        search_res_layout.addWidget(self.button_clear)
        search_splitter.addWidget(self.file_search)
        search_splitter.addWidget(search_res_box)
        brew_grp_split.addWidget(search_splitter)

        # Work group
        work_area = QtGui.QWidget()
        work_layout = QtGui.QVBoxLayout()
        work_area.setLayout(work_layout)
        work_splitter = QtGui.QSplitter(Qt.Qt.Vertical)
        work_layout.addWidget(work_splitter)
        brew_grp_split.addWidget(work_area)
        # Recipe
        self.recipe_box = QtGui.QGroupBox('Current Recipe')
        recipe_layout = QtGui.QHBoxLayout()
        self.recipe_box.setLayout(recipe_layout)
        self.rcg = ControlGroup('new')
        recipe_layout.addWidget(self.rcg)
        work_splitter.addWidget(self.recipe_box)
        # History
        self.history_box = QtGui.QGroupBox('Date')
        history_layout = QtGui.QHBoxLayout()
        self.history_box.setLayout(history_layout)
        self.hcg = ControlGroup('history')
        history_layout.addWidget(self.hcg)
        work_splitter.addWidget(self.history_box)
        # Notes
        notes_box = QtGui.QGroupBox()
        notes_layout = QtGui.QHBoxLayout()
        notes_box.setLayout(notes_layout)
        work_splitter.addWidget(notes_box)
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



























