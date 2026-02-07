"""Product Dispensing Queue - Bottle selection and inventory management"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
    QDialog, QFormLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from .base_queue_view import BaseQueueView
from ui.views.audit_log_dialog import log_transition
from .components.rx_verification_dialog import RxVerificationDialog


class ProductDispensingQueueView(BaseQueueView):
    """Product Dispensing queue - bottle selection and inventory management"""

    TABLE_NAME = "ActivatedPrescriptions"
    WINDOW_TITLE = "Product Dispensing Queue"
    COLUMNS = [
        "Rx #", "Patient", "Medication", "Quantity",
        "Store #", "Status", "Last Updated"
    ]
    COLUMN_KEYS = [
        "rx_id", "patient_name", "medication_name", "quantity_dispensed",
        "store_number", "status", "last_updated"
    ]

    def __init__(self, db_connection, parent=None):
        self.medication_filter = None
        self.patient_filter = None
        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create filters for product dispensing queue"""
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Medication:"))
        self.medication_filter = QLineEdit()
        self.medication_filter.setMinimumWidth(300)
        row1_layout.addWidget(self.medication_filter)
        row1_layout.addStretch()
        parent_layout.addLayout(row1_layout)

        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("Patient:"))
        self.patient_filter = QLineEdit()
        self.patient_filter.setMinimumWidth(300)
        row2_layout.addWidget(self.patient_filter)
        row2_layout.addStretch()
        parent_layout.addLayout(row2_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        filter_btn = QPushButton("Filter")
        filter_btn.setProperty("cssClass", "primary")
        filter_btn.clicked.connect(self.apply_filters_clicked)
        button_layout.addWidget(filter_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setProperty("cssClass", "secondary")
        reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_btn)

        parent_layout.addLayout(button_layout)

    def load_data(self):
        """Load product dispensing queue data"""
        if not self.db_connection:
            return

        try:
            query = """
                SELECT
                    p.prescription_id as rx_id,
                    CONCAT(pt.first_name, ', ', pt.last_name) as patient_name,
                    m.medication_name,
                    p.quantity_dispensed,
                    p.store_number,
                    p.status,
                    p.last_updated,
                    pt.user_id,
                    p.medication_id,
                    p.rx_number
                FROM ActivatedPrescriptions p
                JOIN patientsinfo pt ON p.user_id = pt.user_id
                LEFT JOIN medications m ON p.medication_id = m.medication_id
                WHERE p.status IN ('product_dispensing_pending', 'bottle_selected')
                ORDER BY p.last_updated DESC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            self.db_connection.cursor.execute(query, (self.page_size, offset))
            rows = self.db_connection.cursor.fetchall()

            # Get total count
            self.db_connection.cursor.execute(
                "SELECT COUNT(*) as count FROM ActivatedPrescriptions WHERE status IN ('product_dispensing_pending', 'bottle_selected')"
            )
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading product dispensing queue: {e}")

    def apply_filters_clicked(self):
        """Apply filters and reload queue"""
        self.current_page = 0
        self.load_data()

    def reset_filters(self):
        """Reset all filters"""
        self.medication_filter.clear()
        self.patient_filter.clear()
        self.current_page = 0
        self.load_data()

    def on_row_double_clicked(self, item):
        """Open bottle selection dialog"""
        row = item.row()
        row_item = self.table.item(row, 0)
        if not row_item:
            return

        row_data = row_item.data(256)

        if row_data:
            dialog = BottleSelectionDialog(self.db_connection, row_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()

    def open_prescription_modal(self, prescription_id: int):
        """Open prescription modal for a specific prescription ID (from search)"""
        try:
            # Query ActivatedPrescriptions to get prescription data by ID
            query = """
                SELECT
                    ap.prescription_id as rx_id,
                    ap.user_id,
                    CONCAT(pi.first_name, ', ', pi.last_name) as patient_name,
                    m.medication_name,
                    ap.quantity_dispensed,
                    ap.status,
                    ap.medication_id,
                    ap.rx_number
                FROM ActivatedPrescriptions ap
                JOIN patientsinfo pi ON ap.user_id = pi.user_id
                LEFT JOIN medications m ON ap.medication_id = m.medication_id
                WHERE ap.prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            rx_data = self.db_connection.cursor.fetchone()

            if rx_data:
                from PyQt6.QtWidgets import QMessageBox
                dialog = BottleSelectionDialog(self.db_connection, rx_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_data()
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Not Found", f"Prescription {prescription_id} not found")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to open prescription: {e}")


class BottleSelectionDialog(QDialog):
    """Dialog for selecting a bottle from available stock"""

    def __init__(self, db_connection, rx_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data
        self.rx_id = rx_data.get('rx_id')
        self.user_id = rx_data.get('user_id')
        self.medication_id = rx_data.get('medication_id')
        self.selected_bottle = None

        self.setWindowTitle(f"Select Bottle - {rx_data.get('patient_name')}")
        self.setGeometry(100, 100, 750, 500)
        self.init_ui()
        self.load_bottles()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Prescription info (read-only)
        info_group = QGroupBox("Prescription Information")
        info_layout = QFormLayout()
        info_layout.addRow("Patient:", QLabel(self.rx_data.get('patient_name', '')))
        info_layout.addRow("Medication:", QLabel(self.rx_data.get('medication_name', '')))
        info_layout.addRow("Quantity Needed:", QLabel(str(self.rx_data.get('quantity_dispensed', ''))))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Available bottles table
        bottles_group = QGroupBox("Available Bottles")
        bottles_layout = QVBoxLayout()

        self.bottles_table = QTableWidget()
        self.bottles_table.setColumnCount(5)
        self.bottles_table.setHorizontalHeaderLabels([
            "Bottle ID", "NDC", "Quantity Available", "Expiration Date", "Status"
        ])
        self.bottles_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bottles_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.bottles_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bottles_table.setShowGrid(False)
        self.bottles_table.verticalHeader().setVisible(False)

        bottles_layout.addWidget(self.bottles_table)
        bottles_group.setLayout(bottles_layout)
        layout.addWidget(bottles_group)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_prescription_btn = QPushButton("Cancel Prescription")
        cancel_prescription_btn.setProperty("cssClass", "danger")
        cancel_prescription_btn.clicked.connect(self.cancel_prescription)
        button_layout.addWidget(cancel_prescription_btn)

        select_btn = QPushButton("Select Bottle")
        select_btn.setProperty("cssClass", "success")
        select_btn.clicked.connect(self.select_bottle)
        button_layout.addWidget(select_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "ghost")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def cancel_prescription(self):
        """Cancel the prescription and move to patient history"""
        from PyQt6.QtWidgets import QMessageBox
        if QMessageBox.question(
            self, "Cancel Prescription",
            "Are you sure you want to cancel this prescription?\n\nIt will be moved to the patient's prescription history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self._move_to_patient_history()

    def _move_to_patient_history(self):
        """Move prescription from ActivatedPrescriptions to Prescriptions table"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            cursor = self.db_connection.cursor
            prescription_id = self.rx_id
            user_id = self.user_id
            medication_id = self.medication_id

            # Get current prescription details
            cursor.execute(
                """SELECT quantity_dispensed FROM ActivatedPrescriptions WHERE prescription_id = %s""",
                (prescription_id,)
            )
            ap_data = cursor.fetchone()
            if not ap_data:
                raise Exception("Prescription not found in ActivatedPrescriptions")

            # Move to Prescriptions table (patient history)
            insert_query = """
                INSERT INTO Prescriptions
                (user_id, medication_id, quantity_dispensed, refills_remaining,
                 instructions, status, rx_store_num, fill_date, last_fill_date)
                VALUES (%s, %s, %s, 1, '', 'cancelled_not_dispensed', '', NOW(), NOW())
            """

            cursor.execute(insert_query, (
                user_id,
                medication_id,
                ap_data.get('quantity_dispensed', 0)
            ))

            # Restore bottle quantity if it was allocated
            cursor.execute(
                "SELECT bottle_id, quantity_used FROM inusebottles WHERE prescription_id = %s",
                (prescription_id,)
            )
            bottle_allocation = cursor.fetchone()

            if bottle_allocation:
                cursor.execute(
                    "UPDATE bottles SET quantity = quantity + %s WHERE bottle_id = %s",
                    (bottle_allocation.get('quantity_used', 0), bottle_allocation.get('bottle_id'))
                )

            # Delete from inusebottles (if bottle was allocated)
            cursor.execute(
                "DELETE FROM inusebottles WHERE prescription_id = %s",
                (prescription_id,)
            )

            # Delete from ActivatedPrescriptions
            cursor.execute(
                "DELETE FROM ActivatedPrescriptions WHERE prescription_id = %s",
                (prescription_id,)
            )

            # Delete from ProductSelectionQueue if still there
            cursor.execute(
                "DELETE FROM ProductSelectionQueue WHERE user_id = %s AND status IN ('pending', 'in_progress') LIMIT 1",
                (user_id,)
            )

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"Prescription cancelled and moved to patient history."
            )

            self.reject()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to cancel prescription: {e}")

    def load_bottles(self):
        """Load available bottles matching the medication"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                SELECT bottle_id, ndc, quantity, expiration_date, status
                FROM bottles
                WHERE medication_id = %s AND quantity > 0 AND status = 'in_stock'
                ORDER BY expiration_date ASC
            """, (self.medication_id,))
            bottles = cursor.fetchall()

            self.bottles_table.setRowCount(len(bottles))
            for i, bottle in enumerate(bottles):
                item = QTableWidgetItem(str(bottle.get('bottle_id', '')))
                item.setData(Qt.ItemDataRole.UserRole, bottle)
                self.bottles_table.setItem(i, 0, item)
                self.bottles_table.setItem(i, 1, QTableWidgetItem(str(bottle.get('ndc', ''))))
                self.bottles_table.setItem(i, 2, QTableWidgetItem(str(bottle.get('quantity', ''))))
                exp_date = bottle.get('expiration_date', '')
                self.bottles_table.setItem(i, 3, QTableWidgetItem(str(exp_date)))
                self.bottles_table.setItem(i, 4, QTableWidgetItem(bottle.get('status', '')))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load bottles: {e}")

    def select_bottle(self):
        """Select the highlighted bottle and show Rx verification dialog"""
        selected_rows = self.bottles_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a bottle first.")
            return

        row = selected_rows[0].row()
        bottle_data = self.bottles_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        bottle_id = bottle_data.get('bottle_id')
        quantity_needed = self.rx_data.get('quantity_dispensed', 0)

        try:
            cursor = self.db_connection.cursor

            # Record in inusebottles
            cursor.execute("""
                INSERT INTO inusebottles
                (bottle_id, prescription_id, quantity_used, start_date, status)
                VALUES (%s, %s, %s, NOW(), 'in_use')
            """, (bottle_id, self.rx_id, quantity_needed))

            # Decrement bottle quantity
            cursor.execute("""
                UPDATE bottles
                SET quantity = quantity - %s
                WHERE bottle_id = %s
            """, (quantity_needed, bottle_id))

            self.db_connection.connection.commit()

            # Show Rx verification dialog
            rx_data_for_verify = self.rx_data.copy()
            rx_data_for_verify['prescription_id'] = self.rx_id

            verify_dialog = RxVerificationDialog(
                self.db_connection,
                rx_data_for_verify,
                bottle_data,
                self
            )

            if verify_dialog.exec() == QDialog.DialogCode.Accepted:
                if verify_dialog.verified:
                    # Rx and NDC verified - move to verification queue
                    cursor.execute("""
                        UPDATE ActivatedPrescriptions
                        SET status = 'verification_pending'
                        WHERE prescription_id = %s
                    """, (self.rx_id,))

                    log_transition(
                        self.db_connection, self.rx_id,
                        'product_dispensing_pending', 'verification_pending',
                        f'Bottle #{bottle_id} selected and verified for dispensing'
                    )
                    self.db_connection.connection.commit()

                    QMessageBox.information(
                        self, "Success",
                        "Verification passed. Moving to Verification Queue..."
                    )
                    self.accept()
                else:
                    # Prescription was cancelled - show success and close
                    QMessageBox.information(
                        self, "Cancelled",
                        "Prescription has been cancelled and moved to patient history."
                    )
                    self.accept()
            else:
                # User returned to bottle selection - revert the bottle allocation
                cursor.execute(
                    "DELETE FROM inusebottles WHERE bottle_id = %s AND prescription_id = %s",
                    (bottle_id, self.rx_id)
                )
                cursor.execute(
                    "UPDATE bottles SET quantity = quantity + %s WHERE bottle_id = %s",
                    (quantity_needed, bottle_id)
                )
                self.db_connection.connection.commit()
                # Dialog closed - stay in bottle selection

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to process bottle selection: {e}")
