from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QMenu, QHeaderView, QTableView


class YearView(QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        """Displays a year planner-like calendar populated with dates by a
        QAbstractItemModel for the currently selected year"""
        self.parent = parent
        horiz_header = self.horizontalHeader()
        horiz_header.setSectionResizeMode(QHeaderView.Stretch)
        vert_header = self.verticalHeader()
        vert_header.setSectionResizeMode(QHeaderView.Stretch)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click)

    def set_selection_model(self, model):
        """
        Set up a QItemSelectionModel - sends the current and previous selection
        - we want the current ([0]) selection
        """
        super().setModel(model)
        selection_model = self.selectionModel()
        selection_model.selectionChanged.connect(self.get_selection)

    def get_selection(self):
        try:
            index = self.selectedIndexes()[0]
            day = self.parent.model.itemFromIndex(index)
            date = day.child(0, 1)  # A QStandard item containing the QDate
            self.parent.select_brew(date.data())
        except:
            return

    def right_click(self):
        menu = QMenu(self)
        delete = QAction('Delete', self)
        menu.addAction(delete)
        menu.popup(QCursor.pos())
        delete.triggered.connect(self.delete_item)

    def delete_item(self):
        index = self.selectedIndexes()[0]
        date = self.parent.model.itemFromIndex(index)
        is_brew = date.child(0, 0)
        is_brew.data = False
        self.parent.delete_brew()
        self.parent.model.refresh_colours()
        self.clearSelection()

