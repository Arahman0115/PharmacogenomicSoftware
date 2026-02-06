from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtCore import pyqtSignal
from config import Theme


class PrescriptionTable(QWidget):
    """Reusable prescription table component

    Used in:
    - patient_profile.py (Prescriptions tab)
    - CreateOrderReception.py (prescription table)
    """

    refill_requested = pyqtSignal(dict)  # prescription data
    prescription_selected = pyqtSignal(dict)
    prescription_double_clicked = pyqtSignal(dict)

    def __init__(self, parent=None, db_connection=None, show_refill_button=False, editable=False, user_id=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.show_refill_button = show_refill_button
        self.editable = editable
        self.user_id = user_id
        self.prescriptions = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Prescription table - card style
        self.table = QTableWidget()
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(Theme.TABLE_ROW_HEIGHT)
        self.table.verticalHeader().setVisible(False)

        # Set columns based on configuration
        columns = [
            "Rx # - Store #", "Product Name", "RR", "Disp. Qty",
            "Last Fill", "Prescriber", "Status", "Instructions"
        ]

        if self.show_refill_button:
            columns.append("Action")

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_row_double_clicked)

        # Header configuration
        header = self.table.horizontalHeader()
        header.setHighlightSections(False)

        layout.addWidget(self.table)

    def load_prescriptions(self, user_id=None):
        """Load prescriptions for given patient"""
        if user_id is None and self.user_id is None:
            return

        user_id = user_id or self.user_id

        if not self.db_connection:
            return

        try:
            query = """
                SELECT p.*, m.medication_name
                FROM Prescriptions p
                LEFT JOIN medications m ON p.medication_id = m.medication_id
                WHERE p.user_id = %s
                ORDER BY p.last_fill_date DESC
            """
            self.db_connection.cursor.execute(query, (user_id,))
            self.prescriptions = self.db_connection.cursor.fetchall()
            self.display_prescriptions()
        except Exception as e:
            print(f"Error loading prescriptions: {e}")

    def display_prescriptions(self):
        """Display loaded prescriptions in table"""
        self.table.setRowCount(len(self.prescriptions))

        for row, prescription in enumerate(self.prescriptions):
            # Rx # - Store #
            rx_item = QTableWidgetItem(
                f"{prescription.get('prescription_id', '')}-{prescription.get('store_number', '')}"
            )
            self.table.setItem(row, 0, rx_item)

            # Product Name
            product_item = QTableWidgetItem(prescription.get('medication_name', ''))
            self.table.setItem(row, 1, product_item)

            # RR (Remaining Refills)
            rr_item = QTableWidgetItem(str(prescription.get('refills_remaining', 0)))
            self.table.setItem(row, 2, rr_item)

            # Dispensed Quantity
            disp_qty_item = QTableWidgetItem(str(prescription.get('quantity_dispensed', '')))
            self.table.setItem(row, 3, disp_qty_item)

            # Last Fill
            last_fill_item = QTableWidgetItem(str(prescription.get('last_fill_date', '')))
            self.table.setItem(row, 4, last_fill_item)

            # Prescriber
            prescriber_item = QTableWidgetItem(prescription.get('prescriber_name', ''))
            self.table.setItem(row, 5, prescriber_item)

            # Status
            status_item = QTableWidgetItem(prescription.get('status', ''))
            self.table.setItem(row, 6, status_item)

            # Instructions
            instructions_item = QTableWidgetItem(prescription.get('instructions', ''))
            self.table.setItem(row, 7, instructions_item)

            # Action button (if enabled)
            if self.show_refill_button:
                btn = QPushButton("Refill")
                btn.setProperty("cssClass", "warning")
                btn.clicked.connect(lambda checked, r=row: self.on_refill_clicked(r))
                self.table.setCellWidget(row, 8, btn)

            # Store prescription data in item for retrieval
            self.table.item(row, 0).setData(256, prescription)

    def on_selection_changed(self):
        """Handle row selection"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            prescription_data = item.data(256)
            if prescription_data:
                self.prescription_selected.emit(prescription_data)

    def on_row_double_clicked(self, item):
        """Handle row double-click"""
        row = item.row()
        prescription_item = self.table.item(row, 0)
        prescription_data = prescription_item.data(256)
        if prescription_data:
            self.prescription_double_clicked.emit(prescription_data)

    def on_refill_clicked(self, row):
        """Handle refill button click"""
        item = self.table.item(row, 0)
        prescription_data = item.data(256)
        if prescription_data:
            self.refill_requested.emit(prescription_data)

    def add_prescription(self, prescription_data):
        """Add a prescription to the table"""
        self.prescriptions.append(prescription_data)
        self.display_prescriptions()

    def clear(self):
        """Clear all prescriptions from table"""
        self.table.setRowCount(0)
        self.prescriptions = []

    def get_selected_prescription(self):
        """Get currently selected prescription"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            return item.data(256)
        return None
