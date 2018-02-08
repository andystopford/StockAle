#!/usr/bin/python3.4
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
# StockAle version 3.1  27/12/17
#######################################################################
import sys, math, os.path
import xml.etree.cElementTree as ET
sys.path.append("./Modules")
sys.path.append("./Data")
sys.path.append("./UI")
from PyQt4 import QtCore, QtGui, Qt
from UI import Ui_MainWindow
from IO import*
from operator import itemgetter
from ingredients import*
from SaveDialogue import SaveDialogue
from PrefDialogue import PrefDialogue
from ConversionWindow import ConversionWindow
import DarkStyle


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.default_style_sheet = self.styleSheet()
        self.setWindowTitle("StockAle v.3.1")
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
        #QtGui.QApplication.setStyle(Qt.QStyleFactory.create('cleanlooks'))

        # Connect signals to slots
        self.ui.rcg.button_write_notes.clicked.connect(self.write_notes)
        self.ui.hcg.button_use_recipe.clicked.connect(self.use_recipe)
        self.ui.rcg.button_save_brew.clicked.connect(self.open_save_dlg)
        self.ui.rcg.button_commit.clicked.connect(self.commit)
        self.ui.button_clear.clicked.connect(self.clear_search)
        self.ui.prefs.triggered.connect(self.prefs)
        self.ui.hyd_corr.triggered.connect(self.hydr_corr)
        self.ui.rcg.grain_use.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.rcg.grain_use.connect(self.ui.rcg.grain_use, QtCore.SIGNAL
            ("customContextMenuRequested(QPoint)"), self.grain_use_rclick)
        self.ui.grain_stock.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.grain_stock.connect(self.ui.grain_stock, QtCore.SIGNAL
            ("customContextMenuRequested(QPoint)"), self.grain_stock_rclick)
        self.ui.hop_stock.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.hop_stock.connect(self.ui.hop_stock, QtCore.SIGNAL
            ("customContextMenuRequested(QPoint)"), self.hop_stock_rclick)
        self.ui.rcg.hop_use.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.rcg.hop_use.connect(self.ui.rcg.hop_use, QtCore.SIGNAL
            ("customContextMenuRequested(QPoint)"), self.hop_use_rclick)
        self.ui.button_search.clicked.connect(self.search)
        self.ui.search_results.itemClicked.connect(self.load_search)
        self.ui.file_list.itemClicked.connect(self.load_selecn)
        self.ui.calendar.clicked.connect(self.cell_clicked)

        # Sub-classed qt widgets, etc
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setStyleSheet("""QTextEdit{Background-color:#1d1e1f;
         color: #eff0f1}""")
        self.saveDialogue = SaveDialogue(self)
        self.prefDialogue = PrefDialogue(self)
        self.conversionWindow = ConversionWindow(self)

        self.showMaximized()

    ########################################################################
    # Initialise some stuff
    def init_params(self):
        self.ui.rcg.button_commit.setEnabled(False)
        self.read_prefs()
        self.highlight_date()
        self.ui.tasting_notes.installEventFilter(self)
        self.ui.process_notes.installEventFilter(self)

    def read_prefs(self):
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
                            theme = True
                        else:
                            theme = False
            self.set_prefs(max_display, length, mash_temp,
                           mash_eff, style_list, theme)
        except:
            with open('prefs.xml', 'wb') as fo:
                root = ET.Element('Root')
                tree = ET.ElementTree(root)
                tree.write(fo)
                self.error_message("No Preferences Set")
                self.prefs()

    def set_prefs(self, days, length, temp, eff, styles, theme):
        self.max_display = days
        self.ui.rcg.vol_disp.setText(length)
        self.ui.rcg.mash_temp_disp.setText(temp)
        self.ui.rcg.mash_eff_disp.setText(eff)
        self.ui.box_style.clear()
        styles.sort()
        for item in styles:
            self.ui.box_style.addItem(item)
        if theme:
            self.setStyleSheet(DarkStyle.load_stylesheet())
        else:
            self.setStyleSheet(self.default_style_sheet)
    ###########################################################################
    # Miscellaneous
    def prefs(self):
        """ Show the Preferences dialogue."""
        self.prefDialogue.exec_()

    def hydr_corr(self):
        """ Show the hydrometer correction window."""
        self.conversionWindow.exec_()

    def eventFilter(self, source, event):
        """Detect notes losing focus and save contents"""
        if (event.type() == QtCore.QEvent.FocusOut and source is
                self.ui.tasting_notes):
            self.save_notes()
        if (event.type() == QtCore.QEvent.FocusOut and source is
                self.ui.process_notes):
            self.save_notes()
        return super(MainWindow, self).eventFilter(source, event)

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
                                total = QtGui.QTableWidgetItem(total)
                                table.setItem(row, col, total)
            self.use_grain()
            self.used_grain_update()
            self.grain_grp_update()
            self.use_hop()
            self.used_hop_update()
            self.hop_grp_update()
            self.brew_dirty = True
            self.stock_dirty = True

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
                    wgt = QtGui.QTableWidgetItem()
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
                perCent = QtGui.QTableWidgetItem(perCent)
                self.ui.rcg.grain_use.setItem(pos, 2, perCent)
        row_count = len(self.used_grain_list)  # Ensure extra rows available
        if row_count > 6:
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
        from grain_list.
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
            name = QtGui.QTableWidgetItem(name)
            self.ui.grain_stock.setItem(pos, 0, name)
            col = QtGui.QTableWidgetItem(ebc)
            self.ui.grain_stock.setItem(pos, 1, col)
            extr = QtGui.QTableWidgetItem(extr)
            self.ui.grain_stock.setItem(pos, 2, extr)
            qty = QtGui.QTableWidgetItem(wgt)
            self.ui.grain_stock.setItem(pos, 3, qty)

    def grain_stock_rclick(self):
        """ select entry to delete from grain stock table."""
        menu = QtGui.QMenu(self)
        delete = QtGui.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_grain)

    def delete_grain(self):
        """ Delete stock grain."""
        # Get the value in the right-clicked cell
        row = self.ui.grain_stock.currentRow()
        row = int(row)
        self.grain_list.pop(row)
        self.grain_table_update()
        self.stock_dirty = True

    def grain_use_rclick(self):
        """ select entry to delete from used grain table."""
        menu = QtGui.QMenu(self)
        delete = QtGui.QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_used_grain)

    def delete_used_grain(self):
        """ Delete used grain."""
        row = self.ui.rcg.grain_use.currentRow()
        row = int(row)
        self.used_grain_list.pop(row)
        self.used_grain_update()

    def used_grain_update(self):
        """ Re-populate used grain table."""
        self.ui.rcg.grain_use.clearContents()
        for item in self.used_grain_list:
            pos = self.used_grain_list.index(item)
            name = Grain.get_name(item)
            wgt = str(Grain.get_wgt(item))
            name = QtGui.QTableWidgetItem(name)
            self.ui.rcg.grain_use.setItem(pos, 0, name)
            wgt = QtGui.QTableWidgetItem(wgt)
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
            name = QtGui.QTableWidgetItem(name)
            self.ui.hcg.grain_use.setItem(pos, 0, name)
            wgt = QtGui.QTableWidgetItem(wgt)
            self.ui.hcg.grain_use.setItem(pos, 1, wgt)
            percent = QtGui.QTableWidgetItem(percent)
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
            name = QtGui.QTableWidgetItem(name)
            self.ui.hop_stock.setItem(pos, 0, name)
            alpha = QtGui.QTableWidgetItem(alpha)
            self.ui.hop_stock.setItem(pos, 1, alpha)
            wgt = QtGui.QTableWidgetItem(wgt)
            self.ui.hop_stock.setItem(pos, 2, wgt)

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
                    wgt = QtGui.QTableWidgetItem()
                    self.ui.rcg.hop_use.setItem(row, 1, wgt)
                    wgt.setText(str(0))
                if self.ui.rcg.hop_use.item(row, 2) is None:
                    time = QtGui.QTableWidgetItem()
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
        if row_count > 6:
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
                boil_comp = 1 - math.e ** (curve * time)
                ut = base_utn * boil_comp
                ebu = (wgt * alpha * ut) / (vol * 10)
                total_ebu += int(ebu)
            self.ui.rcg.ebu_disp.setText(str(total_ebu))

    def hop_stock_rclick(self):
        """ Select entry to delete from hop stock table."""
        menu = QtGui.QMenu(self)
        action = QtGui.QAction('Delete', self)
        menu.addAction(action)
        menu.popup(QtGui.QCursor.pos())
        action.triggered.connect(self.delete_hop)

    def delete_hop(self):
        """ Delete hop from stock table."""
        row = self.ui.hop_stock.currentRow()
        row = int(row)
        self.hop_list.pop(row)
        self.hop_table_update()
        self.stock_dirty = True

    def hop_use_rclick(self):
        """ Select entry to delete from hop use table or adjust alpha
        for selected hop instance.
        """
        menu = QtGui.QMenu(self)
        del_action = QtGui.QAction('Delete', self)
        alpha_action = QtGui.QAction('Adjust Alpha', self)
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
                alpha, ok = QtGui.QInputDialog.getText(self, "Adjust Alpha",
                                                       "Enter Alpha",
                                                       QtGui.QLineEdit.Normal,
                                                       curr_alpha)
                if ok:
                    hop.set_alpha(alpha)
        self.hop_info_calc()

    def delete_used_hop(self):
        """ Remove hop instance from used hop table."""
        row = self.ui.rcg.hop_use.currentRow()
        row = int(row)
        self.used_hop_list.pop(row)
        self.used_hop_update()

    def used_hop_update(self):
        """ Re-populate used hop table"""
        self.ui.rcg.hop_use.clearContents()
        for item in self.used_hop_list:
            pos = self.used_hop_list.index(item)
            name = Hop.get_name(item)
            wgt = str(Hop.get_wgt(item))
            time = str(Hop.get_time(item))
            name = QtGui.QTableWidgetItem(name)
            self.ui.rcg.hop_use.setItem(pos, 0, name)
            wgt = QtGui.QTableWidgetItem(wgt)
            self.ui.rcg.hop_use.setItem(pos, 1, wgt)
            time = QtGui.QTableWidgetItem(time)
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
            name = QtGui.QTableWidgetItem(name)
            self.ui.hcg.hop_use.setItem(pos, 0, name)
            wgt = QtGui.QTableWidgetItem(wgt)
            self.ui.hcg.hop_use.setItem(pos, 1, wgt)
            time = QtGui.QTableWidgetItem(time)
            self.ui.hcg.hop_use.setItem(pos, 2, time)
        row_count = len(self.hopRecipe_list)  # Ensure extra rows available
        if len(self.hopRecipe_list) > 4:
            self.ui.hcg.hop_use.setRowCount(row_count + 1)

    ###########################################################################

    def commit_enable(self):
        self.ui.rcg.button_commit.setEnabled(True)

    def commit(self):
        """ Subtract used grain and hops from stock and command data
        save.
        """
        reply = QtGui.QMessageBox.question(self, "Commit Changes",
                                           "Commit changes to Database?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Cancel)
        if reply == QtGui.QMessageBox.Cancel:
            return False
        elif reply == QtGui.QMessageBox.No:
            return True
        elif reply == QtGui.QMessageBox.Yes:
            for used_grain in self.used_grain_list:
                used_name = Grain.get_name(used_grain)
                used_wgt = float(Grain.get_wgt(used_grain))
                for grain in self.grain_list:
                    grain_name = Grain.get_name(grain)
                    if grain_name == used_name:
                        grain.wgt = float(grain.wgt)
                        grain.wgt -= used_wgt
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
        posn = (QtGui.QCursor.pos())
        self.textEdit.setGeometry((posn.x()) - 460, posn.y(), 400, 200)
        self.textEdit.setWindowTitle("Process Notes")
        self.textEdit.show()
        self.brew_dirty = True

    def save_notes(self):
        io = IO(self)
        io.save_notes()

    def open_save_dlg(self):
        self.saveDialogue.setGeometry(780, 290, 300, 220)
        self.saveDialogue.exec_()

    def save_brew(self, fname, date):
        io = IO(self)
        io.save_brew(fname, date)

    def load_brew(self, name, sr_flag):
        self.ui.process_notes.clear()
        self.ui.tasting_notes.clear()
        io = IO(self)
        io.load_brew(name, sr_flag)

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
                name = QtGui.QTableWidgetItem(name)
                self.ui.rcg.grain_use.setItem(pos, 0, name)
                wgt = QtGui.QTableWidgetItem(wgt)
                self.ui.rcg.grain_use.setItem(pos, 1, wgt)
            self.use_grain()
            for item in self.hopRecipe_list:
                pos = self.hopRecipe_list.index(item)
                name = Hop.get_name(item)
                wgt = str(Hop.get_wgt(item))
                time = str(Hop.get_time(item))
                name = QtGui.QTableWidgetItem(name)
                self.ui.rcg.hop_use.setItem(pos, 0, name)
                wgt = QtGui.QTableWidgetItem(wgt)
                self.ui.rcg.hop_use.setItem(pos, 1, wgt)
                time = QtGui.QTableWidgetItem(time)
                self.ui.rcg.hop_use.setItem(pos, 2, time)
            self.use_hop()
            temp = self.ui.hcg.mash_temp_disp.text()
            self.ui.rcg.mash_temp_disp.setText(temp)
            self.ui.recipe_box.setTitle("Unsaved Brew")

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
        mb = QtGui.QMessageBox()
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

    def highlight_date(self):
        """ Reads list of brews in brew folder to populate File List and
        Search Calendar.
        """
        brew_path = self.get_brew_path()
        if brew_path:
            brew_list = []
            file_list = []
            for brewFile in os.listdir(brew_path):
                if not brewFile.startswith('.'):  # filter unix hidden files
                    day = int(brewFile[0:2])
                    month = str(brewFile[2:5])
                    year = int('20' + brewFile[5:7])
                    num_month = int(self.months[month])
                    date = QtCore.QDate(year, num_month, day)
                    brew_list.append(date)  # list of dates for calendar
                    date_tuple = (day, num_month, year, brewFile) # for sorting
                    file_list.append(date_tuple)  # in file list pane
            self.ui.calendar.dates(brew_list)  # adds dates to calendar
            # sort by year, month, day
            for item in sorted(file_list, key=itemgetter(2, 1, 0)):
                self.ui.file_list.addItem(item[3])  # sorted list

    def load_selecn(self):
        """ Load a saved brew."""
        basename = self.ui.file_list.currentItem()
        basename = basename.text()
        self.load_brew(basename, False)

    def search(self):
        """ Search by keyword and/or rating in brew files, and display
        search results.
        """
        brew_path = self.get_brew_path()
        word_list = []
        search_word = str(self.ui.search_box.toPlainText())
        for item in search_word.split():
            word_list.append(item)
        result = []
        rating_list = []
        rating = int(self.ui.rating_input.value())
        rating_range = self.ui.rating_plus_minus.value()
        if rating != 0:
            for brew_file in os.listdir(brew_path):
                if not brew_file.startswith('.'):  # filter unix hidden files
                    with open(brew_path + brew_file) as brew:
                        tree = ET.parse(brew)
                        root = tree.getroot()
                        for elem in root.iter():
                            if elem.tag == 'Rating':
                                if elem.text is None:
                                    elem.text = 0
                                brew_rating = int(elem.text)
                                if rating - rating_range <= brew_rating <= \
                                        rating + rating_range:
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
        if search_word == "":
            filler = ''
        else:
            filler = ' '
        heading = search_word + filler + '(' + 'Rating' + ' ' + str(rating) + \
            ' ' + u"\u00B1" + str(rating_range) + ')'
        heading = QtGui.QListWidgetItem(heading)
        heading.setFont(QtGui.QFont('Sans Serif', 9, QtGui.QFont.Bold))
        self.ui.search_results.addItem(heading)
        if result != []:
            self.ui.search_results.addItems(result)
            self.ui.search_results.addItem("")
        else:
            self.ui.search_results.addItem("Not Found")
            self.ui.search_results.addItem("")

    def load_search(self):
        """ Select brew from search results."""
        base_name = self.ui.search_results.currentItem()
        base_name = base_name.text()
        self.load_brew(base_name, True)

    def clear_search(self):
        self.ui.search_results.clear()
        self.ui.search_box.clear()

    ###########################################################################
    # Brew calendar
    def select_brew(self, date):
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
        self.load_brew(brew, False)

    def cell_clicked(self, date):
        self.select_brew(date)

    ###########################################################################
    def closeEvent(self, event):
        """ On closing application window, save notes from open recipe, check
        if data save required."""
        if self.recipe_filename:
            self.save_notes()
        if self.used_grain_list != [] and self.brew_dirty:
            reply = QtGui.QMessageBox.question(self, "UnSaved Brew",
                                               "Save Brew?",
                                               QtGui.QMessageBox.Yes |
                                               QtGui.QMessageBox.No |
                                               QtGui.QMessageBox.Cancel)
            if reply == QtGui.QMessageBox.Cancel:
                event.ignore()
            elif reply == QtGui.QMessageBox.Yes:
                event.ignore()
                self.open_save_dlg()
            elif reply == QtGui.QMessageBox.No:
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
