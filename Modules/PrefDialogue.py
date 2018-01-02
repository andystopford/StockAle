from PyQt4 import QtCore, QtGui
import os.path
import xml.etree.cElementTree as ET


class PrefDialogue(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        """ A pop-up dialogue allowing the user to set application 
        preferences.
        """
        self.resize(290, 330)
        self.setWindowTitle("Preferences")
        # Widgets
        self.label_days = QtGui.QLabel(self)
        self.label_days.setText("<html><head/><body><p>Max number of days "
                                "since brewing<br/>to display in timeline "
                                "calendar</p></body></html>")
        self.label_length = QtGui.QLabel(self)
        self.label_length.setText(
            "<html><head/><body><p>Brew Length (Litres)</p></body></html>")
        self.label_temp = QtGui.QLabel(self)
        self.label_temp.setText(
            "<html><head/><body><p>Mash Temp (&deg;C)</p></body></html>")
        self.label_eff = QtGui.QLabel(self)
        self.label_eff.setText(
            "<html><head/><body><p>Mash Efficiency %</p></body></html>")
        self.label_theme = QtGui.QLabel(self)
        self.label_theme.setText(
            "<html><head/><body><p>Use Dark Theme</p></body></html>")
        self.spinBox_days = QtGui.QSpinBox(self)
        self.spinBox_days.setValue(90)
        self.spinBox_length = QtGui.QSpinBox(self)
        self.spinBox_length.setValue(60)
        self.spinBox_temp = QtGui.QSpinBox(self)
        self.spinBox_temp.setValue(66)
        self.spinBox_eff = QtGui.QSpinBox(self)
        self.spinBox_eff.setValue(75)
        self.checkbox_theme = QtGui.QCheckBox(self)

        self.button_data_path = QtGui.QPushButton(self)
        self.button_data_path.setText("Data Path")
        self.button_data_path.clicked.connect(self.get_data_path)
        self.data_path_display = QtGui.QPlainTextEdit(self)
        self.data_path_display.setFixedHeight(35)
        default_path = './Data/'
        self.data_path_display.setPlainText(default_path)

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
        box = QtGui.QGridLayout()
        self.setLayout(container)
        container.addLayout(box)
        box.addWidget(self.spinBox_days, 0, 0)
        box.addWidget(self.label_days, 0, 1)
        box.addWidget(self.spinBox_length, 1, 0)
        box.addWidget(self.label_length, 1, 1)
        box.addWidget(self.spinBox_temp, 2, 0)
        box.addWidget(self.label_temp, 2, 1)
        box.addWidget(self.spinBox_eff, 3, 0)
        box.addWidget(self.label_eff, 3, 1)
        box.addWidget(self.checkbox_theme, 4, 0)
        box.addWidget(self.label_theme, 4, 1)
        box.addWidget(self.button_data_path, 5, 0)
        box.addWidget(self.data_path_display, 5, 1)
        container.addWidget(self.styleTable)
        container.addWidget(self.button_apply)

        self.path = './prefs.xml'
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
        sel = dialogue.getExistingDirectory()
        self.data_path_display.setPlainText(sel)

    def init_params(self):
        """ Populates the dialogue with values from prefs.xml."""
        try:
            with open(self.path, "r") as fo:
                tree = ET.ElementTree(file=self.path)
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
            self.styleTable_update()
        except:
            print("No Preference File Found (prefDialogue)")

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
        par = self.parent()
        par.set_prefs(days, length, temp, eff, self.styleList, theme)
        self.save(days, length, temp, eff, theme, path)
        self.close()

    def save(self, days, length, temp, eff, theme, path):
        """Writes preferences to prefs.xml file."""
        root = ET.Element('Root')
        days_tag = ET.SubElement(root, 'Days')
        len_tag = ET.SubElement(root, 'Length')
        temp_tag = ET.SubElement(root, 'Temp')
        eff_tag = ET.SubElement(root, 'Eff')
        styles = ET.SubElement(root, 'Styles')
        ui_theme = ET.SubElement(root, 'Theme')
        path_tag = ET.SubElement(root, 'Path')
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
        with open(self.path, "wb") as fo:
            tree = ET.ElementTree(root)
            tree.write(fo)

