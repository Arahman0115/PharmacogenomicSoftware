from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QGroupBox, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QPushButton, QMessageBox, QDateEdit, QComboBox
)
from PyQt6.QtCore import Qt, QDate


class PrescriptionsTab(QWidget):
    """Prescriptions tab with refill functionality"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.current_prescription = None
        self.init_ui()
        if user_id:
            self.load_prescriptions_data()

    def init_ui(self):
        """Initialize the tab UI"""
        layout = QHBoxLayout(self)

        # Left side: Prescriptions table
        prescriptions_group = QGroupBox("Patient Prescriptions")
        pres_layout = QVBoxLayout()

        # Create table manually
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Rx #", "Medication", "Refills Left", "Qty Dispensed",
            "Last Fill", "Prescriber", "Status", "Instructions"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        pres_layout.addWidget(self.table)

        prescriptions_group.setLayout(pres_layout)

        # Right side: Refill form
        form_group = QGroupBox("Process Refill")
        form_layout = QFormLayout()

        self.med_name = QLineEdit()
        self.med_name.setReadOnly(True)
        form_layout.addRow("Medication:", self.med_name)

        self.prescriber_name = QLineEdit()
        self.prescriber_name.setReadOnly(True)
        form_layout.addRow("Prescriber:", self.prescriber_name)

        self.refills_remaining = QSpinBox()
        self.refills_remaining.setReadOnly(True)
        form_layout.addRow("Refills Remaining:", self.refills_remaining)

        self.instructions = QLineEdit()
        self.instructions.setReadOnly(True)
        form_layout.addRow("Instructions:", self.instructions)

        # Refill quantity
        self.refill_qty = QSpinBox()
        self.refill_qty.setMinimum(1)
        self.refill_qty.setMaximum(999)
        self.refill_qty.setValue(30)
        form_layout.addRow("Refill Quantity:", self.refill_qty)

        # Delivery method
        self.delivery_method = QComboBox()
        self.delivery_method.addItems(["Pick Up", "Delivery"])
        form_layout.addRow("Delivery Method:", self.delivery_method)

        # Promise date
        self.promise_date = QDateEdit()
        self.promise_date.setDate(QDate.currentDate().addDays(1))
        form_layout.addRow("Promise Date:", self.promise_date)

        # Buttons
        button_layout = QHBoxLayout()

        process_btn = QPushButton("Process Refill")
        process_btn.setProperty("cssClass", "success")
        process_btn.clicked.connect(self.process_refill)
        button_layout.addWidget(process_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setProperty("cssClass", "ghost")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)

        form_layout.addRow("", button_layout)
        form_group.setLayout(form_layout)

        layout.addWidget(prescriptions_group, 3)
        layout.addWidget(form_group, 1)

    def load_prescriptions_data(self):
        """Load patient prescriptions from database"""
        if not self.db_connection or not self.user_id:
            return

        try:
            query = """
                SELECT
                    p.prescription_id,
                    p.rx_store_num,
                    m.medication_name,
                    p.refills_remaining,
                    p.quantity_dispensed,
                    p.last_fill_date,
                    pr.prescriber_name,
                    p.status,
                    p.instructions
                FROM Prescriptions p
                LEFT JOIN medications m ON p.medication_id = m.medication_id
                LEFT JOIN Prescribers pr ON p.prescriber_id = pr.prescriber_id
                WHERE p.user_id = %s
                ORDER BY p.last_fill_date DESC
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            results = self.db_connection.cursor.fetchall()

            self.table.setRowCount(0)

            for row_idx, result in enumerate(results):
                self.table.insertRow(row_idx)

                # Store prescription data in first column
                rx_id = result.get('prescription_id')
                rx_num = result.get('rx_store_num', '')

                from PyQt6.QtWidgets import QTableWidgetItem

                item = QTableWidgetItem(rx_num)
                item.setData(Qt.ItemDataRole.UserRole, result)  # Store full data
                self.table.setItem(row_idx, 0, item)

                self.table.setItem(row_idx, 1, QTableWidgetItem(result.get('medication_name', '')))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(result.get('refills_remaining', 0))))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(result.get('quantity_dispensed', 0))))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(result.get('last_fill_date', ''))))
                self.table.setItem(row_idx, 5, QTableWidgetItem(result.get('prescriber_name', '')))
                self.table.setItem(row_idx, 6, QTableWidgetItem(result.get('status', '')))
                self.table.setItem(row_idx, 7, QTableWidgetItem(result.get('instructions', '')))

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load prescriptions: {e}")

    def on_row_selected(self):
        """Handle prescription row selection"""
        selected_rows = self.table.selectionModel().selectedRows()

        if not selected_rows:
            self.clear_form()
            return

        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        self.current_prescription = item.data(Qt.ItemDataRole.UserRole)

        if not self.current_prescription:
            return

        # Populate form
        self.med_name.setText(self.current_prescription.get('medication_name', ''))
        self.prescriber_name.setText(self.current_prescription.get('prescriber_name', ''))
        self.refills_remaining.setValue(self.current_prescription.get('refills_remaining', 0))
        self.instructions.setText(self.current_prescription.get('instructions', ''))
        self.refill_qty.setValue(self.current_prescription.get('quantity_dispensed', 30))

    def process_refill(self):
        """Process refill and add to ProductSelectionQueue"""
        if not self.current_prescription:
            QMessageBox.warning(self, "Error", "Please select a prescription to refill")
            return

        if self.refills_remaining.value() <= 0:
            QMessageBox.warning(self, "Error", "No refills remaining for this prescription")
            return

        if not self.db_connection:
            QMessageBox.critical(self, "Error", "No database connection")
            return

        try:
            cursor = self.db_connection.cursor
            prescription_id = self.current_prescription.get('prescription_id')
            med_name = self.current_prescription.get('medication_name', '')
            patient_first_name = ""
            patient_last_name = ""

            # Get patient name
            cursor.execute(
                "SELECT first_name, last_name FROM patientsinfo WHERE user_id = %s",
                (self.user_id,)
            )
            patient = cursor.fetchone()
            if patient:
                patient_first_name = patient.get('first_name', '')
                patient_last_name = patient.get('last_name', '')

            # Get medication ID
            med_id = None
            cursor.execute(
                "SELECT medication_id FROM medications WHERE medication_name = %s",
                (med_name,)
            )
            med_result = cursor.fetchone()
            if med_result:
                med_id = med_result.get('medication_id')

            # Insert into ProductSelectionQueue (reception/intake queue)
            insert_queue = """
                INSERT INTO ProductSelectionQueue
                (user_id, first_name, last_name, product, quantity, instructions,
                 delivery, promise_time, rx_store_num, status, refills)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 1)
            """

            promise_date = self.promise_date.date().toPyDate()
            promise_datetime = f"{promise_date} 14:00:00"

            cursor.execute(insert_queue, (
                self.user_id,
                patient_first_name,
                patient_last_name,
                med_name,
                self.refill_qty.value(),
                self.current_prescription.get('instructions', ''),
                self.delivery_method.currentText(),
                promise_datetime,
                self.current_prescription.get('rx_store_num', '03102-000')
            ))

            # Decrement refills remaining
            cursor.execute(
                "UPDATE Prescriptions SET refills_remaining = refills_remaining - 1 WHERE prescription_id = %s",
                (prescription_id,)
            )

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"Refill processed for {med_name}.\nItem added to Reception Queue."
            )

            # Reload prescriptions
            self.load_prescriptions_data()
            self.clear_form()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to process refill: {e}")

    def clear_form(self):
        """Clear the refill form"""
        self.current_prescription = None
        self.med_name.clear()
        self.prescriber_name.clear()
        self.refills_remaining.setValue(0)
        self.instructions.clear()
        self.refill_qty.setValue(30)
        self.delivery_method.setCurrentIndex(0)
        self.promise_date.setDate(QDate.currentDate().addDays(1))
        self.table.clearSelection()
