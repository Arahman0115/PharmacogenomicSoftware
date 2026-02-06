from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox
)
from services import PrescriptionService


class EditPrescriptionView(QWidget):
    """Prescription editing and workflow"""

    def __init__(self, db_connection, prescription_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.prescription_id = prescription_id
        self.service = PrescriptionService(db_connection)
        self.prescription = None
        self.available_bottles = []
        self.init_ui()
        if prescription_id:
            self.load_prescription_data()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Prescription Details
        details_group = QGroupBox("Prescription Details")
        details_layout = QFormLayout()

        self.rx_id_field = QLineEdit()
        self.rx_id_field.setReadOnly(True)
        details_layout.addRow("Rx ID:", self.rx_id_field)

        self.patient_field = QLineEdit()
        self.patient_field.setReadOnly(True)
        details_layout.addRow("Patient:", self.patient_field)

        self.medication_field = QLineEdit()
        self.medication_field.setReadOnly(True)
        details_layout.addRow("Medication:", self.medication_field)

        self.quantity_field = QSpinBox()
        self.quantity_field.setMinimum(1)
        details_layout.addRow("Quantity:", self.quantity_field)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Bottle Selection
        bottle_group = QGroupBox("Bottle Selection")
        bottle_layout = QVBoxLayout()

        self.bottle_table = QTableWidget()
        self.bottle_table.setColumnCount(4)
        self.bottle_table.setHorizontalHeaderLabels(["Bottle ID", "NDC", "Expiration", "Quantity"])
        self.bottle_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bottle_table.itemSelectionChanged.connect(self.on_bottle_selected)
        bottle_layout.addWidget(self.bottle_table)

        select_bottle_btn = QPushButton("Select Bottle")
        select_bottle_btn.setProperty("cssClass", "primary")
        select_bottle_btn.clicked.connect(self.select_bottle)
        bottle_layout.addWidget(select_bottle_btn)

        bottle_group.setLayout(bottle_layout)
        layout.addWidget(bottle_group)

        # Workflow Actions
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.review_btn = QPushButton("Send to Drug Review")
        self.review_btn.setProperty("cssClass", "warning")
        self.review_btn.clicked.connect(self.process_to_drug_review)
        action_layout.addWidget(self.review_btn)

        self.complete_btn = QPushButton("Complete Prescription")
        self.complete_btn.setProperty("cssClass", "success")
        self.complete_btn.clicked.connect(self.complete_prescription)
        action_layout.addWidget(self.complete_btn)

        layout.addLayout(action_layout)

    def load_prescription_data(self):
        """Load prescription data using service"""
        if not self.prescription_id:
            return

        try:
            self.prescription = self.service.load_prescription_data(self.prescription_id)
            if self.prescription:
                self.rx_id_field.setText(str(self.prescription.get('prescription_id', '')))
                self.patient_field.setText(f"{self.prescription.get('first_name', '')} {self.prescription.get('last_name', '')}")
                self.medication_field.setText(self.prescription.get('medication_name', ''))
                self.quantity_field.setValue(self.prescription.get('quantity_dispensed', 1))

                # Load available bottles
                self.load_available_bottles()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load prescription: {e}")

    def load_available_bottles(self):
        """Load available bottles for medication"""
        if not self.prescription:
            return

        try:
            medication_id = self.prescription.get('medication_id')
            self.available_bottles = self.service.check_inventory(medication_id)

            self.bottle_table.setRowCount(len(self.available_bottles))
            for row, bottle in enumerate(self.available_bottles):
                self.bottle_table.setItem(row, 0, QTableWidgetItem(str(bottle.get('bottle_id', ''))))
                self.bottle_table.setItem(row, 1, QTableWidgetItem(bottle.get('ndc', '')))
                self.bottle_table.setItem(row, 2, QTableWidgetItem(str(bottle.get('expiration_date', ''))))
                self.bottle_table.setItem(row, 3, QTableWidgetItem(str(bottle.get('quantity', ''))))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bottles: {e}")

    def on_bottle_selected(self):
        """Handle bottle selection"""
        selected = self.bottle_table.selectionModel().selectedRows()
        if selected:
            self.selected_bottle = self.available_bottles[selected[0].row()]

    def select_bottle(self):
        """Select bottle for prescription"""
        if not hasattr(self, 'selected_bottle'):
            QMessageBox.warning(self, "Error", "Please select a bottle")
            return

        try:
            bottle_id = self.selected_bottle.get('bottle_id')
            if self.service.select_bottle(self.prescription_id, bottle_id):
                QMessageBox.information(self, "Success", "Bottle assigned to prescription")
            else:
                QMessageBox.critical(self, "Error", "Failed to assign bottle")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def process_to_drug_review(self):
        """Move to drug review using service"""
        try:
            if self.service.process_to_drug_review(self.prescription_id):
                QMessageBox.information(self, "Success", "Prescription sent to drug review")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to send to drug review")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def complete_prescription(self):
        """Complete and dispense prescription"""
        try:
            if self.service.complete_prescription(self.prescription_id):
                QMessageBox.information(self, "Success", "Prescription completed and dispensed")
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to complete prescription")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
