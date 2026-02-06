from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QTreeWidget, QHeaderView,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt


class PrescriberSelectionView(QWidget):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Prescriber Selection")
        self.resize(1200, 800)
        self.setMinimumSize(1200, 800)

        # Styling handled by global theme

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        self.label = QLabel("Select a Prescriber:")
        self.line_edit = QLineEdit()
        self.button = QPushButton("Search")
        self.button.setProperty("cssClass", "primary")

        top_bar.addWidget(self.label)
        top_bar.addWidget(self.line_edit)
        top_bar.addWidget(self.button)
        top_bar.addStretch()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Specialty", "Location"])
        self.tree_widget.setColumnCount(3)
        self.tree_widget.setHeaderHidden(False)
        header = self.tree_widget.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.tree_widget)
