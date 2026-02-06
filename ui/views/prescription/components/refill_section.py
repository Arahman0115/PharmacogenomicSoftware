from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import pyqtSignal


class RefillSection(QWidget):
    """Refill section for order creation"""

    refill_selected = pyqtSignal(dict)

    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("Refill Prescription")
        group_layout = QVBoxLayout(group)

        # Search controls
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLineEdit())
        self.search_btn = QPushButton("Search Refills")
        self.search_btn.setProperty("cssClass", "primary")
        search_layout.addWidget(self.search_btn)
        group_layout.addLayout(search_layout)

        # Refill options table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Rx #", "Medication", "Refills Remaining", "Last Filled"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        group_layout.addWidget(self.table)

        layout.addWidget(group)

    def on_selection_changed(self):
        """Handle selection from refill table"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            if item:
                # Emit selection signal
                pass

    def load_refills(self, patient_id):
        """Load available refills for patient"""
        if not self.db_connection or not patient_id:
            return

        try:
            query = """
                SELECT p.prescription_id, m.medication_name, p.refills_remaining, p.last_fill_date
                FROM Prescriptions p
                JOIN medications m ON p.medication_id = m.medication_id
                WHERE p.user_id = %s AND p.refills_remaining > 0
                ORDER BY p.last_fill_date DESC
            """
            self.db_connection.cursor.execute(query, (patient_id,))
            refills = self.db_connection.cursor.fetchall()

            self.table.setRowCount(len(refills))
            for row, refill in enumerate(refills):
                self.table.setItem(row, 0, QTableWidgetItem(str(refill.get('prescription_id', ''))))
                self.table.setItem(row, 1, QTableWidgetItem(refill.get('medication_name', '')))
                self.table.setItem(row, 2, QTableWidgetItem(str(refill.get('refills_remaining', ''))))
                self.table.setItem(row, 3, QTableWidgetItem(str(refill.get('last_fill_date', ''))))

        except Exception as e:
            print(f"Error loading refills: {e}")
