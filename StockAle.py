#!/usr/bin/python3.6
######################################################################
# Copyright (C)2017 Andy Stopford
# This is free software: you can redistribute it and/or modify
# under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 3.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# StockAle version 5.0.0  16/12/20
#######################################################################
import math
import os.path
import sys
import xml.etree.cElementTree as ET

sys.path.append("./Modules")
sys.path.append("./Data")
sys.path.append("./UI")
from PyQt5 import QtCore, QtGui, Qt, QtWidgets
from UI import Ui_MainWindow
from IO import IO
from ingredients import Grain, Hop
from SaveDialogue import SaveDialogue
import DarkStyle.pyqt5_style_rc
from Model import Model
import datetime
from decimal import Decimal


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.default_style_sheet = self.styleSheet()
        self.setWindowTitle("StockAle v.5.0.0")
        self.setWindowIcon(QtGui.QIcon('./pint_icon.png'))
        self.max_display = 90
        self.grain_list = []
        self.sel_grain = 0
        self.used_grain_list = []
        self.grainRecipe_list = []
        self.hop_list = []
        self.used_hop_list = []
        self.hopRecipe_list = []
        self.grain_select = 0
        self.hop_select = 0
        self.total_ebu = 0
        self.pkt_use = 0
        self.process_notes = ""
        self.brew_dirty = False
        self.stock_dirty = False
        self.recipe_filename = None
        self.path = ""
        self.dateList = []
        self.months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5,
                       'Jun': 6, 'Jul': 7,
                       'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        self.palette = QtGui.QPalette()

        # Connect signals to slots
        self.ui.button_back.clicked.connect(self.year_back)
        self.ui.button_forward.clicked.connect(self.year_forward)
        self.ui.rcg.button_write_notes.clicked.connect(self.write_notes)
        self.ui.hcg.button_use_recipe.clicked.connect(self.use_recipe)
        self.ui.rcg.button_save_brew.clicked.connect(self.open_save_dlg)
        self.ui.rcg.button_commit.clicked.connect(self.commit)
        self.ui.button_clear.clicked.connect(self.clear_search)

        self.ui.rcg.grain_use.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.rcg.grain_use.setSelectionMode(QtWidgets.QAbstractItemView.
                                               NoSelection)
        self.ui.rcg.grain_use.customContextMenuRequested.connect\
            (self.grain_use_rclick)

        self.ui.grain_stock.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.grain_stock.customContextMenuRequested.connect\
            (self.grain_stock_rclick)

        self.ui.hop_stock.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.hop_stock.customContextMenuRequested.connect\
            (self.hop_stock_rclick)

        self.ui.rcg.hop_use.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.rcg.hop_use.customContextMenuRequested.connect\
            (self.hop_use_rclick)

        self.ui.button_search.clicked.connect(self.search)

        # Sub-classed qt widgets, etc
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setStyleSheet("""QTextEdit{Background-color:#1d1e1f;
         color: #eff0f1}""")
        self.saveDialogue = SaveDialogue(self)
        self.showMaximized()

        self.model_dict = {}
        self.year = 0
        self.dirty = False

    ########################################################################
    # Initialise some stuff
    def startup(self):
        self.ui.rcg.button_commit.setEnabled(False)
        self.read_prefs()
        self.ui.tasting_notes.installEventFilter(self)
        self.ui.process_notes.installEventFilter(self)
        self.ui.box_style.currentIndexChanged.connect(self.save_notes)
        self.ui.rating.valueChanged.connect(self.save_notes)
        today = datetime.date.today()
        self.year = today.year
        self.dirty = False
        self.setup_year()

    def setup_year(self):
        """Populates current year from brew files"""
        io = IO(self)
        io.open_brews()
        try:
            self.model = self.model_dict[self.year]
        except:
            self.model = Model(self)
            self.model.setup()
        self.model.set_year(self.year)
        self.ui.yearView.setModel(self.model)
        self.ui.yearView.set_selection_model(self.model)
        self.ui.label_year.setText(str(self.year))

    def year_back(self):
        """YearView back button"""
        self.year -= 1
        self.setup_year()

    def year_forward(self):
        """YearView forward button"""
        self.year += 1
        self.setup_year()

    def read_prefs(self):
        """Reads preferences saved in 'prefx.xml' file"""
        self.ui.colourSettings.defaults()
        style_list = []
        try:
            path = './prefs.xml'
            with open(path, "r") as fo:
                tree = ET.ElementTree(file=fo)
                root = tree.getroot()
                for elem in root.iter():
                    if elem.tag == 'Days':
                        max_display = (int(elem.text))
                    if elem.tag == 'Length':
                        length = (str(elem.text))
                    if elem.tag == 'Temp':
                        mash_temp = (str(elem.text))
                    if elem.tag == 'Eff':
                        mash_eff = (str(elem.text))
                    if elem.tag == 'Styles':
                        for style in elem:
                            style = style.tag.replace('_', ' ')
                            style_list.append(style)
                    if elem.tag == 'Theme':
                        if elem.text == 'dark':
                            dark_theme = True
                        else:
                            dark_theme = False
            self.set_prefs(max_display, length, mash_temp,
                           mash_eff, style_list, dark_theme)
        except:
            with open('prefs.xml', 'wb') as fo:
                root = ET.Element('Root')
                tree = ET.ElementTree(root)
                tree.write(fo)
                self.error_message("No Preferences Set")
                #self.prefs()

    def set_prefs(self, days, length, temp, eff, styles, dark_theme):
        """Applies preferences"""
        self.max_display = days
        self.ui.rcg.vol_disp.setText(length)
        self.ui.rcg.mash_temp_disp.setText(temp)
        self.ui.rcg.mash_eff_disp.setText(eff)
        self.ui.box_style.clear()
        styles.sort()
        for item in styles:
            self.ui.box_style.addItem(item)
        # Available QStyle keys: 'Breeze', 'Windows', 'Motif', 'CDE',
        # 'Plastique', 'GTK+', 'Cleanlooks'
        if dark_theme:
            self.setStyleSheet(DarkStyle.load_stylesheet())
            QtWidgets.QApplication.setStyle(Qt.QStyleFactory.create('Breeze'))
        else:
            self.setStyleSheet(self.default_style_sheet)
            QtWidgets.QApplication.setStyle(Qt.QStyleFactory.create('cleanlooks'))

    ###########################################################################
    # Event handlers

    def eventFilter(self, source, event):
        """Detect notes losing focus and save contents"""
        if (event.type() == QtCore.QEvent.FocusOut and source is
                self.ui.tasting_notes):
            self.save_notes()
        if (event.type() == QtCore.QEvent.FocusOut and source is
                self.ui.process_notes):
            self.save_notes()
        return super().eventFilter(source, event)

    def keyPressEvent(self, qKeyEvent):
        """
        Triggers calculation of stock and used items, and sorts tables to
        eliminate blank lines. Arithmetic operators in stock tables are
        calculated.
        """
        add = "+"
        sub = "-"
        mult = "*"
        div = "/"
        tables = [self.ui.grain_stock, self.ui.hop_stock]
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            for table in tables:
                for row in range(table.rowCount()):
                    if table.item(row, 0) is not None:
                        for col in range(table.columnCount()):
                            if table.item(row, col) is not None:
                                inpt = str(table.item(row, col).text())
                                total = inpt
                                if inpt.find(add) != -1:
                                    op = inpt.split(add)
                                    total = float(op[0]) + float(op[1])
                                if inpt.find(sub) != -1:
                                    op = inpt.split(sub)
                                    total = float(op[0]) - float(op[1])
                                if inpt.find(mult) != -1:
                                    op = inpt.split(mult)
                                    total = float(op[0]) * float(op[1])
                                if inpt.find(div) != -1:
                                    op = inpt.split(div)
                                    total = float(op[0]) / float(op[1])
                                total = str(total)
                                total = QtWidgets.QTableWidgetItem(total)
                                table.setItem(row, col, total)
            self.update_all()

    ###########################################################################
    # Grain
    def grain_grp_update(self):
        """ Add an instance of class Grain to grain_list list of
        instances, sorts the list by EBC value and calls grain_table_update.
        """
        self.grain_list = []
        for row in range(self.ui.grain_stock.rowCount()):
            if self.ui.grain_stock.item(row, 0) is not None:
                if self.ui.grain_stock.item(row, 0).text() != "":
                    name = self.ui.grain_stock.item(row, 0).text()
                    ebc = self.ui.grain_stock.item(row, 1).text()
                    extr = self.ui.grain_stock.item(row, 2).text()
                    wgt = self.ui.grain_stock.item(row, 3).text()
                    a_grain = Grain(name, ebc, extr, wgt)
                    if name != "":
                        self.grain_list.append(a_grain)
        num = -1 + len(self.grain_list)
        if len(self.grain_list) > 5:
            self.ui.grain_stock.setRowCount(num + 1)
        # sort using int or 3, 10, 1 sorts to 1, 10, 3
        self.grain_list.sort(key=lambda Grain: int(Grain.ebc))
        self.grain_table_update()

    def use_grain(self):
        """ Populate used_grain_list and calculate percentage use."""
        total = 0
        self.used_grain_list = []
        stock_list = []
        for row in range(self.ui.rcg.grain_use.rowCount()):
            if self.ui.rcg.grain_use.item(row, 0) is not None:
                if self.ui.rcg.grain_use.item(row, 1) is None:
                    wgt = QtWidgets.QTableWidgetItem()
                    self.ui.rcg.grain_use.setItem(row, 1, wgt)
                    wgt.setText(str(0))

                name = self.ui.rcg.grain_use.item(row, 0).text()
                wgt = float(self.ui.rcg.grain_use.item(row, 1).text())
                for item in self.grain_list:
                    if name == item.get_name():
                        stock_name = item.get_name()
                        stock_list.append(stock_name)
                        extr = item.get_extr()
                        ebc = item.get_ebc()
                if name not in stock_list:
                    self.error_message("Warning: " + name +
                                       " not in stock")
                    self.ui.rcg.grain_use.removeRow(row)
                else:
                    total += wgt
                    a_used_grain = Grain(name, ebc, extr, wgt)
                    self.used_grain_list.append(a_used_grain)
        if total > 0:  # Calculate percentages in table
            for item in self.used_grain_list:
                pos = self.used_grain_list.index(item)
                wgt = float(Grain.get_wgt(item))
                perCent = int((wgt / total) * 100)
                perCent = str(perCent)
                perCent = QtWidgets.QTableWidgetItem(perCent)
                self.ui.rcg.grain_use.setItem(pos, 2, perCent)
        row_count = len(self.used_grain_list)  # Ensure extra rows available
        if row_count > 5:
            self.ui.rcg.grain_use.setRowCount(row_count + 1)
        self.ui.rcg.grain_use.clearSelection()
        self.grain_info_calc()

    def grain_info_calc(self):
        """ Calculate wort OG and EBC."""
        if len(self.used_grain_list) > 0:
            mash_deg = 0
            total_col = 0
            mash_eff = int(self.ui.rcg.mash_eff_disp.text())
            vol = float(self.ui.rcg.vol_disp.text())
            for item in self.used_grain_list:
                wgt = float(Grain.get_wgt(item))
                extr = float(Grain.get_extr(item))
                col = int(Grain.get_ebc(item))
                deg = (extr * wgt *
                       (float(mash_eff) / 100)) / vol
                mash_deg += deg
                col *= wgt
                total_col += col
            OG = int(mash_deg)
            OG = str(OG)
            total_col = int(total_col * 10 * (float(mash_eff) / 100)) / vol
            colour = int(total_col)
            self.ui.rcg.ebc_disp.setText(str(colour))
            self.ui.rcg.og_disp.setText(OG)

    def grain_table_update(self):
        """ Fill cells in the grain stock table with instances
        from grain_list. If grain not in stock the text is greyed.
        """
        self.ui.grain_stock.clearContents()
        row_count = len(self.grain_list)  # Ensure extra rows available
        if row_count > 6:
            self.ui.grain_stock.setRowCount(row_count + 1)
        for item in self.grain_list:
            pos = self.grain_list.index(item)
            name = Grain.get_name(item)
            ebc = Grain.get_ebc(item)
            extr = Grain.get_extr(item)
            wgt = Grain.get_wgt(item)
            name = QtWidgets.QTableWidgetItem(name)
            if float(wgt) <= 0:
                in_stock = False
            else:
                in_stock = True
            self.ui.grain_stock.setItem(pos, 0, name)
            col = QtWidgets.QTableWidgetItem(ebc)
            self.ui.grain_stock.setItem(pos, 1, col)
            extr = QtWidgets.QTableWidgetItem(extr)
            self.ui.grain_stock.setItem(pos, 2, extr)
            qty = QtWidgets.QTableWidgetItem(wgt)
            self.ui.grain_stock.setItem(pos, 3, qty)
            if not in_stock:
                for col in range(4):
                    self.ui.grain_stock.item(pos, col).setForeground\
                        (QtGui.QColor('#697076'))

    def grain_stock_rclick(self):
        """ select entry to delete from grain stock table."""
        menu = QtWidgets.QMenu(self)
        delete = QtWidgets.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_grain)

    def delete_grain(self):
        """ Delete stock grain."""
        # Get the value in the right-clicked cell
        row = self.ui.grain_stock.currentRow()
        row = int(row)
        try:
            self.grain_list.pop(row)
        except IndexError:
            pass
        self.grain_table_update()
        self.stock_dirty = True

    def grain_use_rclick(self):
        """ select entry to delete from used grain table."""
        menu = QtWidgets.QMenu(self)
        delete = QtWidgets.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_used_grain)

    def delete_used_grain(self):
        """ Delete used grain."""
        row = self.ui.rcg.grain_use.currentRow()
        row = int(row)
        try:
            self.used_grain_list.pop(row)
        except IndexError:
            pass
        self.used_grain_update()

    def used_grain_update(self):
        """ Re-populate used grain table."""
        self.ui.rcg.grain_use.clearContents()
        for item in self.used_grain_list:
            pos = self.used_grain_list.index(item)
            name = Grain.get_name(item)
            wgt = str(Grain.get_wgt(item))
            name = QtWidgets.QTableWidgetItem(name)
            #name.setFlags(name.flags() & ~QtCore.Qt.ItemIsEditable)
            #name.setFlags(name.flags() & ~QtCore.Qt.ItemIsDropEnabled)
            self.ui.rcg.grain_use.setItem(pos, 0, name)
            wgt = QtWidgets.QTableWidgetItem(wgt)
            self.ui.rcg.grain_use.setItem(pos, 1, wgt)
        self.use_grain()

    def grain_recipe_update(self):
        """ Re-populate used grain table and adjusts row count to allow
        new entries."""
        self.ui.hcg.grain_use.clearContents()
        total = 0
        for item in self.grainRecipe_list:
            pos = self.grainRecipe_list.index(item)
            name = Grain.get_name(item)
            wgt = str(Grain.get_wgt(item))
            calc_wgt = float(Grain.get_wgt(item))
            total += calc_wgt
            percent = int((calc_wgt / total) * 100)
            percent = str(percent)
            name = QtWidgets.QTableWidgetItem(name)
            self.ui.hcg.grain_use.setItem(pos, 0, name)
            wgt = QtWidgets.QTableWidgetItem(wgt)
            self.ui.hcg.grain_use.setItem(pos, 1, wgt)
            percent = QtWidgets.QTableWidgetItem(percent)
            self.ui.hcg.grain_use.setItem(pos, 2, percent)
        row_count = len(self.grainRecipe_list)  # Ensure extra rows available
        if len(self.grainRecipe_list) > 4:
            self.ui.hcg.grain_use.setRowCount(row_count + 1)

    ###########################################################################
    # Hops
    def hop_grp_update(self):
        """ Add an instance of class Hop to hop_list list of
        instances, sorts the list alphabetically and calls hop_table_update.
        """
        self.hop_list = []
        for row in range(self.ui.hop_stock.rowCount()):
            if self.ui.hop_stock.item(row, 0) is not None:
                if self.ui.hop_stock.item(row, 0).text() != "":
                    name = self.ui.hop_stock.item(row, 0).text()
                    alpha = self.ui.hop_stock.item(row, 1).text()
                    wgt = self.ui.hop_stock.item(row, 2).text()
                    a_hop = Hop(name, alpha, wgt, 0)
                    if name != "":
                        self.hop_list.append(a_hop)
        num = -1 + len(self.hop_list)
        if len(self.hop_list) > 5:
            self.ui.hop_stock.setRowCount(num + 1)
        self.hop_list.sort(key=lambda Hop: Hop.name)
        self.hop_table_update()

    def hop_table_update(self):
        """Re-populate hop_stock table after changes to self.hop_list"""
        self.ui.hop_stock.clearContents()
        row_count = len(self.hop_list)  # Ensure extra rows available
        if row_count > 6:
            self.ui.hop_stock.setRowCount(row_count + 1)
        for item in self.hop_list:
            pos = self.hop_list.index(item)
            name = Hop.get_name(item)
            alpha = Hop.get_alpha(item)
            wgt = Hop.get_wgt(item)
            name = QtWidgets.QTableWidgetItem(name)
            if float(wgt) <= 0:
                in_stock = False
            else:
                in_stock = True
            self.ui.hop_stock.setItem(pos, 0, name)
            alpha = QtWidgets.QTableWidgetItem(alpha)
            self.ui.hop_stock.setItem(pos, 1, alpha)
            wgt = QtWidgets.QTableWidgetItem(wgt)
            self.ui.hop_stock.setItem(pos, 2, wgt)
            if not in_stock:
                for col in range(3):
                    self.ui.hop_stock.item(pos, col).setForeground\
                        (QtGui.QColor('#697076'))

    def use_hop(self):
        """Reads entries in the hop_use table. If the weight or time
        columns are empty, it automatically enters default values: 0g
        and 0 minutes. If an adjustment has been made to the entry's
        alpha, this value is used for the calculation.
        """
        temp_used_hops = self.used_hop_list
        self.used_hop_list = []
        total = 0
        stock_list = []
        adj_alpha = None
        for row in range(self.ui.rcg.hop_use.rowCount()):
            if self.ui.rcg.hop_use.item(row, 0) is not None:
                if self.ui.rcg.hop_use.item(row, 1) is None:
                    wgt = QtWidgets.QTableWidgetItem()
                    self.ui.rcg.hop_use.setItem(row, 1, wgt)
                    wgt.setText(str(0))
                if self.ui.rcg.hop_use.item(row, 2) is None:
                    time = QtWidgets.QTableWidgetItem()
                    self.ui.rcg.hop_use.setItem(row, 2, time)
                    time.setText(str(0))
                name = self.ui.rcg.hop_use.item(row, 0).text()
                wgt = float(self.ui.rcg.hop_use.item(row, 1).text())
                time = float(self.ui.rcg.hop_use.item(row, 2).text())
                for hop in temp_used_hops:
                    if hop.get_name() == name:
                        adj_alpha = hop.get_alpha()
                for item in self.hop_list:
                    if name == item.get_name():
                        stock_name = item.get_name()
                        stock_list.append(stock_name)
                        alpha = item.get_alpha()
                if name not in stock_list:
                    self.error_message("Warning: " + name + " not in stock")
                    self.ui.rcg.hop_use.removeRow(row)
                else:
                    total += wgt
                    if adj_alpha:
                        alpha = adj_alpha
                    a_used_hop = Hop(name, alpha, wgt, time)
                    self.used_hop_list.append(a_used_hop)
                    adj_alpha = None
        row_count = len(self.used_hop_list)  # Ensure extra rows available
        if row_count > 5:
            self.ui.rcg.hop_use.setRowCount(row_count + 1)
        self.ui.rcg.hop_use.clearSelection()
        self.hop_info_calc()

    def hop_info_calc(self):
        """Calculates wort EBU"""
        if len(self.used_hop_list) > 0:
            base_utn = float(37)
            curve = float(15)
            curve *= -0.001
            total_ebu = 0
            vol = float(self.ui.rcg.vol_disp.text())
            for item in self.used_hop_list:
                wgt = float(Hop.get_wgt(item))
                alpha = float(Hop.get_alpha(item))
                time = float(Hop.get_time(item))
                # Negative time represents hop stand at 80 C
                if time < 0:
                    time = - time
                    time = time * 0.25
                boil_comp = 1 - math.e ** (curve * time)
                ut = base_utn * boil_comp
                ebu = (wgt * alpha * ut) / (vol * 10)
                total_ebu += int(ebu)
            self.ui.rcg.ebu_disp.setText(str(total_ebu))

    def hop_stock_rclick(self):
        """ Select entry to delete from hop stock table."""
        menu = QtWidgets.QMenu(self)
        action = QtWidgets.QAction('Delete', self)
        menu.addAction(action)
        menu.popup(QtGui.QCursor.pos())
        action.triggered.connect(self.delete_hop)

    def delete_hop(self):
        """ Delete hop from stock table."""
        row = self.ui.hop_stock.currentRow()
        row = int(row)
        try:
            self.hop_list.pop(row)
        except IndexError:
            pass
        self.hop_table_update()
        self.stock_dirty = True

    def hop_use_rclick(self):
        """ Select entry to delete from hop use table or adjust alpha
        for selected hop instance.
        """
        menu = QtWidgets.QMenu(self)
        del_action = QtWidgets.QAction('Delete', self)
        alpha_action = QtWidgets.QAction('Adjust Alpha', self)
        menu.addAction(del_action)
        menu.addAction(alpha_action)
        menu.popup(QtGui.QCursor.pos())
        del_action.triggered.connect(self.delete_used_hop)
        alpha_action.triggered.connect(self.adj_used_hop)

    def adj_used_hop(self):
        """For making local adjustment to alpha value"""
        row = self.ui.rcg.hop_use.currentRow()
        row = int(row)
        for hop in self.used_hop_list:
            if hop.get_name() == self.ui.rcg.hop_use.item(row, 0).text():
                curr_alpha = hop.get_alpha()
                alpha, ok = QtWidgets.QInputDialog.getText(self, "Adjust Alpha",
                                                       "Enter Alpha",
                                                       QtWidgets.QLineEdit.Normal,
                                                       curr_alpha)
                if ok:
                    hop.set_alpha(alpha)
        self.hop_info_calc()

    def delete_used_hop(self):
        """ Remove hop instance from used hop table."""
        row = self.ui.rcg.hop_use.currentRow()
        row = int(row)
        try:
            self.used_hop_list.pop(row)
        except IndexError:
            pass
        self.used_hop_update()

    def used_hop_update(self):
        """ Re-populate used hop table"""
        self.ui.rcg.hop_use.clearContents()
        for item in self.used_hop_list:
            pos = self.used_hop_list.index(item)
            name = Hop.get_name(item)
            wgt = str(Hop.get_wgt(item))
            time = str(Hop.get_time(item))
            name = QtWidgets.QTableWidgetItem(name)
            #name.setFlags(QtCore.Qt.ItemIsEditable)
            #name.setFlags(QtCore.Qt.ItemIsDropEnabled)
            self.ui.rcg.hop_use.setItem(pos, 0, name)
            wgt = QtWidgets.QTableWidgetItem(wgt)
            self.ui.rcg.hop_use.setItem(pos, 1, wgt)
            time = QtWidgets.QTableWidgetItem(time)
            self.ui.rcg.hop_use.setItem(pos, 2, time)
        self.use_hop()

    def hop_recipe_update(self):
        """ Re-populate used hop table and adjusts row count to allow
        new entries.
        """
        self.ui.hcg.hop_use.clearContents()
        for item in self.hopRecipe_list:
            pos = self.hopRecipe_list.index(item)
            name = Hop.get_name(item)
            wgt = str(Hop.get_wgt(item))
            time = str(Hop.get_time(item))
            name = QtWidgets.QTableWidgetItem(name)
            self.ui.hcg.hop_use.setItem(pos, 0, name)
            wgt = QtWidgets.QTableWidgetItem(wgt)
            self.ui.hcg.hop_use.setItem(pos, 1, wgt)
            time = QtWidgets.QTableWidgetItem(time)
            self.ui.hcg.hop_use.setItem(pos, 2, time)
        row_count = len(self.hopRecipe_list)  # Ensure extra rows available
        if len(self.hopRecipe_list) > 4:
            self.ui.hcg.hop_use.setRowCount(row_count + 1)

    ###########################################################################

    def update_all(self):
        self.use_grain()
        self.used_grain_update()
        self.grain_grp_update()
        self.use_hop()
        self.used_hop_update()
        self.hop_grp_update()
        self.brew_dirty = True
        self.stock_dirty = True

    ###########################################################################

    def commit_enable(self):
        self.ui.rcg.button_commit.setEnabled(True)

    def commit(self):
        """ Subtract used grain and hops from stock and command data
        save.
        """
        reply = QtWidgets.QMessageBox.question(self, "Commit Changes",
                                           "Commit changes to Database?",
                                           QtWidgets.QMessageBox.Yes |
                                           QtWidgets.QMessageBox.No |
                                           QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Cancel:
            return False
        elif reply == QtWidgets.QMessageBox.No:
            return True
        elif reply == QtWidgets.QMessageBox.Yes:
            for used_grain in self.used_grain_list:
                used_name = Grain.get_name(used_grain)
                used_wgt = float(Grain.get_wgt(used_grain))
                for grain in self.grain_list:
                    grain_name = Grain.get_name(grain)
                    if grain_name == used_name:
                        grain.wgt = float(grain.wgt)
                        grain.wgt -= used_wgt
                        grain.wgt = Decimal(grain.wgt)
                        grain.wgt = round(grain.wgt, 2)
                        if grain.wgt < 0:
                            grain.wgt = 0
                        grain.wgt = str(grain.wgt)
                        self.grain_table_update()
            for used_hop in self.used_hop_list:
                used_name = Hop.get_name(used_hop)
                used_wgt = float(Hop.get_wgt(used_hop))
                for hop in self.hop_list:
                    hop_name = Hop.get_name(hop)
                    if hop_name == used_name:
                        hop.wgt = float(hop.wgt)
                        hop.wgt -= used_wgt
                        hop.wgt = Decimal(hop.wgt)
                        hop.wgt = round(hop.wgt, 1)
                        if hop.wgt < 0:
                            hop.wgt = 0
                            hop.wgt = str(hop.wgt)
                        self.hop_table_update()
            self.ui.rcg.button_commit.setEnabled(False)
            self.save_data()
            self.stock_dirty = False
            return True

    ###########################################################################
    # Save/Load stock data
    def save_data(self):
        io = IO(self)
        io.save_data()

    def load_data(self):
        io = IO(self)
        io.load_data()

    ###########################################################################
    # Save/Load brew
    def write_notes(self):
        """Opens process notes floating window"""
        posn = (QtGui.QCursor.pos())
        self.textEdit.setGeometry((posn.x()) - 460, posn.y(), 400, 200)
        self.textEdit.setWindowTitle("Process Notes")
        self.textEdit.show()
        self.brew_dirty = True

    def save_notes(self):
        io = IO(self)
        io.save_notes()

    def open_save_dlg(self):
        self.update_all()
        self.saveDialogue.setGeometry(780, 290, 300, 220)
        self.saveDialogue.exec_()

    def save_brew(self, fname, date):
        io = IO(self)
        io.save_brew(fname, date)
        self.setup_year()

    def load_brew(self, name):
        """Displays selected brew in history area"""
        self.ui.process_notes.clear()
        self.ui.tasting_notes.clear()
        io = IO(self)
        io.load_brew(name)

    def delete_brew(self):
        """Deletion using YearView RClick menu"""
        io = IO(self)
        io.delete_brew()

###########################################################################
    def use_recipe(self):
        """ Load recipe from history panel into recipe panel."""
        if self.grain_list == []:
            msg = "Error: no stock data"
            self.errorMessage(msg)
        elif self.hop_list == []:
            msg = "Error: no stock data"
            self.errorMessage(msg)
        else:
            self.ui.rcg.grain_use.clearContents()
            self.ui.rcg.hop_use.clearContents()
            for item in self.grainRecipe_list:
                pos = self.grainRecipe_list.index(item)
                name = Grain.get_name(item)
                wgt = str(Grain.get_wgt(item))
                name = QtWidgets.QTableWidgetItem(name)
                self.ui.rcg.grain_use.setItem(pos, 0, name)
                wgt = QtWidgets.QTableWidgetItem(wgt)
                self.ui.rcg.grain_use.setItem(pos, 1, wgt)
            self.use_grain()
            for item in self.hopRecipe_list:
                pos = self.hopRecipe_list.index(item)
                name = Hop.get_name(item)
                wgt = str(Hop.get_wgt(item))
                time = str(Hop.get_time(item))
                name = QtWidgets.QTableWidgetItem(name)
                self.ui.rcg.hop_use.setItem(pos, 0, name)
                wgt = QtWidgets.QTableWidgetItem(wgt)
                self.ui.rcg.hop_use.setItem(pos, 1, wgt)
                time = QtWidgets.QTableWidgetItem(time)
                self.ui.rcg.hop_use.setItem(pos, 2, time)
            self.use_hop()
            temp = self.ui.hcg.mash_temp_disp.text()
            self.ui.rcg.mash_temp_disp.setText(temp)
            self.ui.recipe_box.setTitle("Unsaved Brew")
            self.ui.tabbed_area.setCurrentIndex(0)

    def time_ago(self):
        """ Calculate and display time since brewed."""
        date_string = self.recipe_filename
        day = int(date_string[0:2])
        month = str(date_string[2:5])
        year = int('20' + date_string[5:7])
        num_month = int(self.months[month])
        brew_date = QtCore.QDate(year, num_month, day)
        curr_date = QtCore.QDate.currentDate()
        days = brew_date.daysTo(curr_date)
        if days < int(self.max_display):
            if days < 0:
                days = 0
            weeks = int(days / 7)
            rem_days = days % 7
            self.ui.since_brew.setText(
                '{0} Weeks {1} Days'.format(str(weeks), str(rem_days)))
        else:
            self.ui.since_brew.setText('Out of Range')

    def error_message(self, msg):
        """Show a message box"""
        mb = QtWidgets.QMessageBox()
        mb.setText(msg)
        mb.exec_()

    ###########################################################################
    # Search
    def get_brew_path(self):
        path = IO.get_path(self)
        if path:
            brew_path = path + '/Brews/'
            os.makedirs(brew_path, exist_ok=True)
            return brew_path

    def search(self):
        """ Search by keyword and/or rating in brew files, and display
        search results.
        """
        brew_path = self.get_brew_path()
        word_list = []
        search_word = str(self.ui.search_box.text())
        if not search_word:
            pass
        else:
            for item in search_word.split():
                word_list.append(item)
            result = []
            rating_list = []
            rating = int(self.ui.rating_input.value())
            rating_range = self.ui.rating_plus_minus.value()
            if rating != 0:
                for brew_file in os.listdir(brew_path):
                    if not brew_file.startswith('.'):# filter unix hidden files
                        with open(brew_path + brew_file) as brew:
                            tree = ET.parse(brew)
                            root = tree.getroot()
                            for elem in root.iter():
                                if elem.tag == 'Rating':
                                    if elem.text is None:
                                        elem.text = 0
                                    brew_rating = int(elem.text)
                                    if rating - rating_range <= brew_rating \
                                            <= rating + rating_range:
                                        rating_list.append(brew_file)
                # now search only the files in rating_list
                for brew_file in rating_list:
                    with open(brew_path + brew_file) as brew:
                        for line in brew:
                            if search_word.lower() in line.lower():
                                if brew_file not in result:
                                    result.append(brew_file)
                                    # condition if rating not entered
            else:
                for brew_file in os.listdir(brew_path):
                    if not brew_file.startswith('.'):
                        with open(brew_path + brew_file) as brew:
                            for line in brew:
                                for item in word_list:
                                    if item.lower() in line.lower():
                                        if brew_file not in result:
                                            result.append(brew_file)
            if result != []:
                results_all = ''
                for item in result:
                    results_all = results_all + item + ', '
                # Remove last comma
                results_all = results_all[0:len(results_all) - 2]
                self.ui.results_box.setText(results_all)
                self.convert_search(result)
            else:
                self.error_message("No Result Found")

    def convert_search(self, result):
        """Converts brew file names to QDates and sends date to the
        appropriate model"""
        for date in result:
            day = int(date[0:2])
            month = date[2:5]
            month = self.months[month]  # Convert month name to number
            year = date[5:7]
            year = int(str(20) + year)
            date = QtCore.QDate(year, month, day)
            if year not in self.model_dict:
                model = Model(self)
                model.set_year(year)
                self.model_dict[self.year] = model
            model = self.model_dict[year]
            model.display_search(date)

    def clear_search(self):
        """Clears search from all models"""
        for key in self.model_dict:
            model = self.model_dict[key]
            model.clear_search()
            model.setup()
            model.set_year(key)
            self.ui.search_box.clear()
            self.ui.results_box.clear()
        self.setup_year()

    ###########################################################################
    # YearView
    #def cell_clicked(self, date):
    #    self.select_brew(date)

    def select_brew(self, date):
        if date:
            day = date.day()
            month = date.month()
            month = date.shortMonthName(month)
            year = date.year()
            year = str(year - 2000)
            month = str(month)
            if day < 10:
                day = "0" + str(day)
            day = str(day)
            brew = day + month + year
            self.load_brew(brew)

    ###########################################################################
    def closeEvent(self, event):
        """ On closing application window, save notes from open recipe, check
        if data save required."""
        if self.recipe_filename:
            self.save_notes()
        if self.used_grain_list != [] and self.brew_dirty:
            reply = QtWidgets.QMessageBox.question(self, "UnSaved Brew",
                                               "Save Brew?",
                                               QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No |
                                               QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
            elif reply == QtWidgets.QMessageBox.Yes:
                event.ignore()
                self.open_save_dlg()
            elif reply == QtWidgets.QMessageBox.No:
                self.save_data()
        if self.ui.rcg.button_commit.isEnabled():
            commit = self.commit()
            if commit is True:
                event.accept()
            elif commit is False:
                event.ignore()
                return
        if self.stock_dirty:
            self.save_data()
            event.accept()
        else:
            event.accept()
