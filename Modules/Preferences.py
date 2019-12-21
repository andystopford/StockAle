from PyQt4 import QtCore, QtGui
import os.path
import xml.etree.cElementTree as ET

class Preferences(QtGui.QGroupBox):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        """UI for setting application preferences"""
        #self.colourSettings = parent.ui.colourSettings
        self.parent = parent
        self.setTitle('Preferences')
        self.setToolTip('Set application preferences here')
        # Widgets
        label_theme = QtGui.QLabel(self)
        label_theme.setText(
            "<html><head/><body><p>Use Dark Theme</p></body></html>")
        label_days = QtGui.QLabel(self)
        label_days.setText("<html><head/><body><p>Max days since brewing"
                                "<br/>to display</p></body></html>")
        label_length = QtGui.QLabel(self)
        label_length.setText(
            "<html><head/><body><p>Brew Length (Litres)</p></body></html>")
        label_temp = QtGui.QLabel(self)
        label_temp.setText(
            "<html><head/><body><p>Mash Temp (&deg;C)</p></body></html>")
        label_eff = QtGui.QLabel(self)
        label_eff.setText(
            "<html><head/><body><p>Mash Efficiency %</p></body></html>")
        label_styles = QtGui.QLabel(self)
        label_styles.setText(
            "<html><head/><body><p>User Specified Styles</p></body></html>")
        self.checkbox_theme = QtGui.QCheckBox(self)
        self.spinBox_days = QtGui.QSpinBox(self)
        self.spinBox_days.setValue(90)
        self.spinBox_length = QtGui.QSpinBox(self)
        self.spinBox_length.setValue(60)
        self.spinBox_temp = QtGui.QSpinBox(self)
        self.spinBox_temp.setValue(66)
        self.spinBox_eff = QtGui.QSpinBox(self)
        self.spinBox_eff.setValue(75)

        self.button_data_path = QtGui.QPushButton(self)
        self.button_data_path.setText("Data Path")
        self.button_data_path.clicked.connect(self.get_data_path)
        self.data_path_display = QtGui.QPlainTextEdit(self)
        self.data_path_display.setFixedHeight(35)
        default_path = './Data/'
        self.data_path_display.setPlainText(default_path)
        self.data_path_display.setToolTip(self.data_path_display.toPlainText())

        self.styleTable = QtGui.QTableWidget(self)
        self.styleTable.setColumnCount(1)
        self.styleTable.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem(
            "Beer Styles"))
        style_header = self.styleTable.horizontalHeader()
        style_header.setResizeMode(QtGui.QHeaderView.Stretch)
        self.styleTable.verticalHeader().setVisible(False)
        self.styleTable.setRowCount(1)
        self.styleTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.styleTable.connect(self.styleTable, QtCore.SIGNAL
        ("customContextMenuRequested(QPoint)"), self.styleTable_RClick)
        self.button_apply = QtGui.QPushButton(self)
        self.button_apply.setText("Apply")
        self.button_apply.clicked.connect(self.apply)

        # Layout
        container = QtGui.QVBoxLayout()
        container.setMargin(10)
        box = QtGui.QGridLayout()
        self.setLayout(container)
        container.addLayout(box)
        box.addWidget(self.checkbox_theme, 0, 0)
        box.addWidget(label_theme, 0, 1)
        box.addWidget(self.spinBox_days, 1, 0)
        box.addWidget(label_days, 1, 1)
        box.addWidget(self.spinBox_length, 2, 0)
        box.addWidget(label_length, 2, 1)
        box.addWidget(self.spinBox_temp, 3, 0)
        box.addWidget(label_temp, 3, 1)
        box.addWidget(self.spinBox_eff, 4, 0)
        box.addWidget(label_eff, 4, 1)
        box.addWidget(self.styleTable, 5, 0)
        box.addWidget(label_styles, 5, 1)
        box.addWidget(self.button_data_path, 6, 0)
        box.addWidget(self.data_path_display, 6, 1)
        container.addWidget(self.button_apply)

        path = os.getcwd()
        self.path = path + '/prefs.xml'
        self.styleList = []
        self.init_params()

    def keyPressEvent(self, qKeyEvent):
        """ Press Enter to add a new, empty row to the style table so that
        multiple entries can be made in one session.
        """
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            rows = 0
            for row in range(self.styleTable.rowCount()):
                if self.styleTable.item(row, 0) is not None:
                    rows += 1
            self.styleTable.setRowCount(rows + 1)

    def get_data_path(self):
        """" Set path for data/brew save."""
        dialogue = QtGui.QFileDialog(self)
        dialogue.setFileMode(QtGui.QFileDialog.AnyFile)
        # dialogue.setOption(QtGui.QFileDialog.DontUseNativeDialog) win/OSX?
        sel = dialogue.getExistingDirectory()
        self.data_path_display.setPlainText(sel)
        self.data_path_display.setToolTip(self.data_path_display.toPlainText())

    def init_params(self):
        """ Populates the dialogue with values from prefs.xml."""
        colourSettings = self.parent.ui.colourSettings
        try:
            with open(self.path, "r") as fo:
                tree = ET.ElementTree(file=fo)
                root = tree.getroot()
                for elem in root.iter():
                    if elem.tag == 'Days':
                        self.spinBox_days.setValue(int(elem.text))
                    if elem.tag == 'Length':
                        self.spinBox_length.setValue(int(elem.text))
                    if elem.tag == 'Temp':
                        self.spinBox_temp.setValue(int(elem.text))
                    if elem.tag == 'Eff':
                        self.spinBox_eff.setValue(int(elem.text))
                    if elem.tag == 'Styles':
                        for style in elem:
                            style = style.tag.replace('_', ' ')
                            self.styleList.append(style)
                    if elem.tag == 'Theme':
                        if elem.text == 'dark':
                            self.checkbox_theme.setChecked(True)
                    if elem.tag == 'Path':
                        data_path = elem.text
                        self.data_path_display.setPlainText(data_path)
                    if elem.tag == 'WkDay':
                        # TODO load at startup
                        colourSettings.weekday_col = elem.text
            self.styleTable_update()
        except:
            print("No Preference File Found (Preferences)")

    def styleTable_update(self):
        """ Adjusts table to number of entries."""
        pos = 0
        rows = 1
        self.styleList.sort()
        for item in self.styleList:
            self.styleTable.setRowCount(rows)
            item = QtGui.QTableWidgetItem(item)
            self.styleTable.setItem(0, pos, item)
            pos += 1
            rows += 1
        self.styleTable.setRowCount(rows)

    def styleTable_RClick(self):
        """ R Click menu to delete unwanted entries."""
        self.menu = QtGui.QMenu(self)
        delete = QtGui.QAction('Delete', self)
        self.menu.addAction(delete)
        self.menu.popup(QtGui.QCursor.pos())
        delete.triggered.connect(self.delete_style)

    def delete_style(self):
        """Delete unwanted entries"""
        row = self.styleTable.currentRow()
        row = int(row)
        self.styleList.pop(row)
        self.styleTable_update()

    def apply(self):
        """ Sets preferences in parent window, saves to file, and
        closes the Preferences dialogue.
        """
        self.styleList = []
        pos = 0
        rows = 1
        for row in range(self.styleTable.rowCount()):
            if self.styleTable.item(row, 0) is not None:
                style = self.styleTable.item(row, 0).text()
                self.styleList.append(style)
        self.styleList.sort()
        for item in self.styleList:
            self.styleTable.setRowCount(rows)
            item = QtGui.QTableWidgetItem(item)
            self.styleTable.setItem(0, pos, item)
            pos += 1
            rows += 1
        self.styleTable.setRowCount(rows)
        days = str(self.spinBox_days.text())
        length = str(self.spinBox_length.text())
        temp = str(self.spinBox_temp.text())
        eff = str(self.spinBox_eff.text())
        theme = self.checkbox_theme.checkState()
        path = str(self.data_path_display.toPlainText())
        par = self.parent
        par.set_prefs(days, length, temp, eff, self.styleList, theme)
        self.save(days, length, temp, eff, theme, path)

    def save(self, days, length, temp, eff, theme, path):
        """Writes preferences to prefs.xml file."""
        colourSettings = self.parent.ui.colourSettings
        root = ET.Element('Root')
        days_tag = ET.SubElement(root, 'Days')
        len_tag = ET.SubElement(root, 'Length')
        temp_tag = ET.SubElement(root, 'Temp')
        eff_tag = ET.SubElement(root, 'Eff')
        styles = ET.SubElement(root, 'Styles')
        ui_theme = ET.SubElement(root, 'Theme')
        path_tag = ET.SubElement(root, 'Path')
        wkday_col = ET.SubElement(root, 'WkDay')
        wkend_col = ET.SubElement(root, 'WkEnd')
        brday_col = ET.SubElement(root, 'BrDay')
        srchday_col = ET.SubElement(root, 'SrchDay')
        days_tag.text = str(days)
        len_tag.text = str(length)
        temp_tag.text = str(temp)
        eff_tag.text = str(eff)
        path_tag.text = path
        if theme:
            ui_theme.text = str('dark')
        else:
            ui_theme.text = str('def')
        for row in range(self.styleTable.rowCount()):
            if self.styleTable.item(row, 0) is not None:
                style = str(self.styleTable.item(row, 0).text())
                style = style.replace(' ', '_')  # Prevent XML errors
                style = ET.SubElement(styles, style)
        wkday_col.text = colourSettings.weekday_col.name()
        wkend_col.text = colourSettings.weekend_col.name()
        brday_col.text = colourSettings.brewday_col.name()
        srchday_col.text = colourSettings.searchday_col.name()
        with open(self.path, "wb") as fo:
            tree = ET.ElementTree(root)
            tree.write(fo)
