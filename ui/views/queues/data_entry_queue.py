"""Data Entry Queue - Edit prescription details and verify before drug review"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QDialog, QFormLayout, QLineEdit, QSpinBox, QDateEdit, QTextEdit,
    QMessageBox, QLabel, QGroupBox, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from .base_queue_view import BaseQueueView
from ui.views.audit_log_dialog import log_transition
from services.contact_service import ContactService


class DataEntryQueueView(BaseQueueView):
    """Data Entry Queue - Edit prescription details before drug review"""

    TABLE_NAME = "ProductSelectionQueue"
    WINDOW_TITLE = "Data Entry Queue"
    COLUMNS = [
        "ID", "Patient", "Medication", "Qty",
        "Instructions", "Status", "Date Added"
    ]
    COLUMN_KEYS = [
        "id", "patient_name", "product", "quantity",
        "instructions", "status", "promise_time"
    ]

    def __init__(self, db_connection, parent=None):
        super().__init__(db_connection, parent)
        self.setWindowTitle(self.WINDOW_TITLE)

    def load_data(self):
        """Load pending prescriptions from ProductSelectionQueue"""
        if not self.db_connection:
            return

        try:
            query = """
                SELECT
                    id,
                    user_id,
                    CONCAT(first_name, ' ', last_name) as patient_name,
                    product,
                    quantity,
                    delivery,
                    promise_time,
                    status,
                    instructions,
                    rx_store_num,
                    created_date,
                    refills
                FROM ProductSelectionQueue
                WHERE status IN ('pending', 'in_progress')
                ORDER BY created_date ASC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            self.db_connection.cursor.execute(query, (self.page_size, offset))
            rows = self.db_connection.cursor.fetchall()

            # Get total count
            self.db_connection.cursor.execute(
                "SELECT COUNT(*) as count FROM ProductSelectionQueue WHERE status IN ('pending', 'in_progress')"
            )
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading data entry queue: {e}")

    def display_data(self, rows):
        """Display queue data in table"""
        self.table.setRowCount(0)

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)

            # Store full data in UserRole
            item = QTableWidgetItem(str(row.get('id', '')))
            item.setData(Qt.ItemDataRole.UserRole, row)
            self.table.setItem(row_idx, 0, item)

            self.table.setItem(row_idx, 1, QTableWidgetItem(row.get('patient_name', '')))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row.get('product', '')))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(row.get('quantity', ''))))
            self.table.setItem(row_idx, 4, QTableWidgetItem(row.get('instructions', '')[:50]))
            self.table.setItem(row_idx, 5, QTableWidgetItem(row.get('status', '')))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(row.get('created_date', ''))))

    def on_row_double_clicked(self, item):
        """Open prescription editor on double-click"""
        row = item.row()
        row_item = self.table.item(row, 0)
        rx_data = row_item.data(Qt.ItemDataRole.UserRole)

        if rx_data:
            dialog = DataEntryEditorDialog(self.db_connection, rx_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Reload data after successful edit
                self.load_data()

    def open_prescription_modal(self, prescription_id: int):
        """Open prescription modal for a specific prescription ID (from search)"""
        try:
            # Query ActivatedPrescriptions to get prescription data by ID
            query = """
                SELECT
                    ap.prescription_id as id,
                    ap.user_id,
                    CONCAT(pi.first_name, ' ', pi.last_name) as patient_name,
                    m.medication_name as product,
                    ap.quantity_dispensed as quantity,
                    '' as instructions,
                    ap.status,
                    ap.fill_date as promise_time,
                    0 as refills,
                    ap.medication_id,
                    'Pick Up' as delivery
                FROM ActivatedPrescriptions ap
                JOIN patientsinfo pi ON ap.user_id = pi.user_id
                LEFT JOIN medications m ON ap.medication_id = m.medication_id
                WHERE ap.prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            rx_data = self.db_connection.cursor.fetchone()

            if rx_data:
                dialog = DataEntryEditorDialog(self.db_connection, rx_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_data()
            else:
                QMessageBox.warning(self, "Not Found", f"Prescription {prescription_id} not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open prescription: {e}")


class DataEntryEditorDialog(QDialog):
    """Dialog for editing prescription details in data entry queue"""

    def __init__(self, db_connection, rx_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data
        self.rx_id = rx_data.get('id')
        self.user_id = rx_data.get('user_id')

        self.setWindowTitle(f"Data Entry - {rx_data.get('patient_name')}")
        self.setGeometry(100, 100, 700, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Patient information (read-only)
        patient_group = QGroupBox("Patient Information")
        patient_layout = QFormLayout()

        patient_name = QLineEdit()
        patient_name.setText(self.rx_data.get('patient_name', ''))
        patient_name.setReadOnly(True)
        patient_layout.addRow("Patient:", patient_name)

        patient_id = QLineEdit()
        patient_id.setText(str(self.user_id))
        patient_id.setReadOnly(True)
        patient_layout.addRow("Patient ID:", patient_id)

        patient_group.setLayout(patient_layout)
        layout.addWidget(patient_group)

        # Editable prescription details
        details_group = QGroupBox("Prescription Details")
        details_layout = QFormLayout()

        # Medication name (read-only)
        self.medication = QLineEdit()
        self.medication.setText(self.rx_data.get('product', ''))
        self.medication.setReadOnly(True)
        details_layout.addRow("Medication:", self.medication)

        # Date written
        self.date_written = QDateEdit()
        self.date_written.setDate(QDate.currentDate())
        self.date_written.setCalendarPopup(True)
        details_layout.addRow("Date Written:", self.date_written)

        # Quantity written (read-only - from prescription)
        self.quantity_written = QSpinBox()
        self.quantity_written.setMinimum(1)
        self.quantity_written.setMaximum(9999)
        self.quantity_written.setValue(self.rx_data.get('quantity', 30))
        self.quantity_written.setReadOnly(True)
        details_layout.addRow("Quantity Written:", self.quantity_written)

        # Quantity dispensed (editable - what pharmacist will dispense)
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(9999)
        self.quantity.setValue(self.rx_data.get('quantity', 30))
        details_layout.addRow("Quantity Dispensing:", self.quantity)

        # Refills
        self.refills = QSpinBox()
        self.refills.setMinimum(0)
        self.refills.setMaximum(999)
        self.refills.setValue(self.rx_data.get('refills', 0))
        details_layout.addRow("Refills Remaining:", self.refills)

        # Instructions
        self.instructions = QTextEdit()
        self.instructions.setText(self.rx_data.get('instructions', ''))
        self.instructions.setMaximumHeight(100)
        details_layout.addRow("Instructions (SIG):", self.instructions)

        # Delivery method
        self.delivery = QComboBox()
        self.delivery.addItems(["Pick Up", "Delivery", "Mail"])
        current_delivery = self.rx_data.get('delivery', 'Pick Up')
        self.delivery.setCurrentText(current_delivery)
        details_layout.addRow("Delivery Method:", self.delivery)

        # Promise date
        self.promise_date = QDateEdit()
        self.promise_date.setCalendarPopup(True)
        if self.rx_data.get('promise_time'):
            promise_str = str(self.rx_data.get('promise_time', '')).split()[0]
            try:
                self.promise_date.setDate(QDate.fromString(promise_str, 'yyyy-MM-dd'))
            except:
                self.promise_date.setDate(QDate.currentDate().addDays(1))
        else:
            self.promise_date.setDate(QDate.currentDate().addDays(1))
        details_layout.addRow("Promise Date:", self.promise_date)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Action buttons
        button_layout = QHBoxLayout()

        # Status info - dynamic routing message
        self.status_label = QLabel("After saving, prescription routes based on drug-gene conflicts")
        self.status_label.setProperty("cssClass", "text-secondary")
        button_layout.addWidget(self.status_label)

        button_layout.addStretch()

        clarification_btn = QPushButton("Request Clarification")
        clarification_btn.setProperty("cssClass", "warning")
        clarification_btn.clicked.connect(self.request_clarification)
        button_layout.addWidget(clarification_btn)

        cancel_prescription_btn = QPushButton("Cancel Prescription")
        cancel_prescription_btn.setProperty("cssClass", "danger")
        cancel_prescription_btn.clicked.connect(self.cancel_prescription)
        button_layout.addWidget(cancel_prescription_btn)

        save_btn = QPushButton("Save & Continue")
        save_btn.setProperty("cssClass", "primary")
        save_btn.clicked.connect(self.save_and_continue)
        button_layout.addWidget(save_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "ghost")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def cancel_prescription(self):
        """Cancel the prescription and move to patient history"""
        if QMessageBox.question(
            self, "Cancel Prescription",
            "Are you sure you want to cancel this prescription?\n\nIt will be moved to the patient's prescription history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self._move_to_patient_history()

    def _move_to_patient_history(self):
        """Move prescription from ActivatedPrescriptions to Prescriptions table"""
        try:
            cursor = self.db_connection.cursor
            prescription_id = self.rx_id
            user_id = self.user_id
            medication_id = self.rx_data.get('medication_id')

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

    def request_clarification(self):
        """Create a clarification request with prescriber"""
        try:
            cursor = self.db_connection.cursor
            prescription_id = self.rx_id
            medication_name = self.rx_data.get('product', '')

            # Get prescriber_id and medication_id from ActivatedPrescriptions
            cursor.execute("""
                SELECT prescriber_id, medication_id FROM ActivatedPrescriptions
                WHERE prescription_id = %s
            """, (prescription_id,))
            ap_data = cursor.fetchone()

            if not ap_data or not ap_data.get('prescriber_id'):
                QMessageBox.warning(
                    self, "Cannot Create Request",
                    "Prescriber information is not available for this prescription."
                )
                return

            # Open dialog to get clarification reason
            reason, ok = self.get_clarification_reason()
            if not ok or not reason:
                return

            # Create the clarification request
            contact_service = ContactService(self.db_connection)
            success = contact_service.create_clarification_request(
                user_id=self.user_id,
                prescriber_id=ap_data.get('prescriber_id'),
                prescription_id=prescription_id,
                medication_id=ap_data.get('medication_id'),
                reason=reason
            )

            if success:
                QMessageBox.information(
                    self, "Request Created",
                    f"Clarification request created for {medication_name}.\n\n"
                    "The prescriber will be contacted to provide the needed clarification.\n"
                    "You can track this request in the Contact Queue."
                )
                self.reject()
            else:
                QMessageBox.critical(self, "Error", "Failed to create clarification request")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating clarification request: {e}")

    def get_clarification_reason(self):
        """Open dialog to get reason for clarification"""
        from PyQt6.QtWidgets import QInputDialog
        reason, ok = QInputDialog.getMultiLineText(
            self,
            "Request Clarification",
            "What clarification is needed from the prescriber?\n\n"
            "Examples:\n"
            "- Dosage unclear\n"
            "- Frequency not specified\n"
            "- Interaction concern\n"
            "- Patient allergy question",
            ""
        )
        return reason, ok

    def save_and_continue(self):
        """Save edited prescription and route based on drug-gene conflicts"""
        try:
            cursor = self.db_connection.cursor

            # Update ProductSelectionQueue with edited details
            update_query = """
                UPDATE ProductSelectionQueue
                SET quantity = %s,
                    instructions = %s,
                    delivery = %s,
                    promise_time = %s,
                    refills = %s,
                    status = 'data_entry_complete'
                WHERE id = %s
            """

            promise_datetime = f"{self.promise_date.date().toPyDate()} 14:00:00"

            cursor.execute(update_query, (
                self.quantity.value(),
                self.instructions.toPlainText(),
                self.delivery.currentText(),
                promise_datetime,
                self.refills.value(),
                self.rx_id
            ))

            # Move to ActivatedPrescriptions if not already there
            # Get medication ID
            cursor.execute(
                "SELECT medication_id FROM medications WHERE medication_name = %s",
                (self.medication.text(),)
            )
            med_result = cursor.fetchone()
            med_id = med_result.get('medication_id') if med_result else None

            if med_id:
                # Check if already in ActivatedPrescriptions
                cursor.execute(
                    "SELECT COUNT(*) as count FROM ActivatedPrescriptions WHERE user_id = %s AND medication_id = %s",
                    (self.user_id, med_id)
                )
                count = cursor.fetchone().get('count', 0)

                if count == 0:
                    # Insert into ActivatedPrescriptions
                    insert_query = """
                        INSERT INTO ActivatedPrescriptions
                        (user_id, medication_id, quantity_dispensed, rx_store_num, store_number, status, fill_date)
                        VALUES (%s, %s, %s, %s, '1618', 'data_entry_complete', CURDATE())
                    """
                    cursor.execute(insert_query, (
                        self.user_id,
                        med_id,
                        self.quantity.value(),
                        self.rx_data.get('rx_store_num', '03102-000')
                    ))

                    # Get the prescription_id just inserted and generate rx_number
                    prescription_id = cursor.lastrowid
                    rx_number = f"RX{str(prescription_id).zfill(6)}"

                    # Update with rx_number
                    cursor.execute(
                        "UPDATE ActivatedPrescriptions SET rx_number = %s WHERE prescription_id = %s",
                        (rx_number, prescription_id)
                    )
                else:
                    # Get existing prescription_id
                    cursor.execute(
                        "SELECT prescription_id, rx_number FROM ActivatedPrescriptions WHERE user_id = %s AND medication_id = %s LIMIT 1",
                        (self.user_id, med_id)
                    )
                    result = cursor.fetchone()
                    prescription_id = result.get('prescription_id') if result else None

                    # Generate rx_number if not already set
                    if prescription_id:
                        existing_rx = result.get('rx_number')
                        if not existing_rx:
                            rx_number = f"RX{str(prescription_id).zfill(6)}"
                            cursor.execute(
                                "UPDATE ActivatedPrescriptions SET rx_number = %s WHERE prescription_id = %s",
                                (rx_number, prescription_id)
                            )

                # Drug-drug interaction check
                self._check_drug_drug_interactions(cursor, med_id)

                # Check for drug-gene interactions
                cursor.execute("""
                    SELECT COUNT(*) as count FROM drug_review
                    WHERE user_id = %s AND medication_id = %s AND status = 'active'
                """, (self.user_id, med_id))

                has_conflicts = cursor.fetchone().get('count', 0) > 0

                if has_conflicts:
                    # Create drugreviewqueue entry
                    cursor.execute("""
                        INSERT INTO drugreviewqueue
                        (prescription_id, user_id, medication_id, risk_level, status)
                        SELECT %s, %s, %s, risk_level, 'pending'
                        FROM drug_review
                        WHERE user_id = %s AND medication_id = %s AND status = 'active'
                        LIMIT 1
                    """, (prescription_id, self.user_id, med_id, self.user_id, med_id))

                    log_transition(
                        self.db_connection, prescription_id,
                        'data_entry_complete', 'drug_review_pending',
                        'Data entry complete - drug-gene conflict detected'
                    )
                    self.db_connection.connection.commit()

                    QMessageBox.information(
                        self, "Success",
                        f"Prescription updated.\n"
                        f"Drug-gene conflict detected - moving to Drug Review Queue..."
                    )
                else:
                    # No drug-gene conflicts - skip drug review, go to product dispensing
                    cursor.execute("""
                        UPDATE ActivatedPrescriptions
                        SET status = 'product_dispensing_pending'
                        WHERE prescription_id = %s
                    """, (prescription_id,))

                    log_transition(
                        self.db_connection, prescription_id,
                        'data_entry_complete', 'product_dispensing_pending',
                        'Data entry complete - no conflicts, skipping drug review'
                    )
                    self.db_connection.connection.commit()

                    QMessageBox.information(
                        self, "Success",
                        f"Prescription updated.\n"
                        f"No drug-gene conflicts - moving to Product Dispensing Queue..."
                    )
            else:
                self.db_connection.connection.commit()
                QMessageBox.information(
                    self, "Success",
                    "Prescription updated (medication not found in catalog)."
                )

            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to save prescription: {e}")
            print(f"Error: {e}")

    def _check_drug_drug_interactions(self, cursor, med_id):
        """Check for drug-drug interactions with patient's other active medications"""
        try:
            # Ensure the drug_drug_interactions table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drug_drug_interactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    medication_id_1 INT NOT NULL,
                    medication_id_2 INT NOT NULL,
                    severity VARCHAR(50) NOT NULL,
                    description TEXT,
                    INDEX idx_med1 (medication_id_1),
                    INDEX idx_med2 (medication_id_2)
                )
            """)

            # Get patient's other active medications
            cursor.execute("""
                SELECT DISTINCT ap.medication_id, m.medication_name
                FROM ActivatedPrescriptions ap
                JOIN medications m ON ap.medication_id = m.medication_id
                WHERE ap.user_id = %s
                  AND ap.medication_id != %s
                  AND ap.status NOT IN ('rejected', 'released_to_pickup', 'completed')
            """, (self.user_id, med_id))
            active_meds = cursor.fetchall()

            if not active_meds:
                return

            active_med_ids = [m.get('medication_id') for m in active_meds]

            # Check for interactions
            placeholders = ','.join(['%s'] * len(active_med_ids))
            cursor.execute(f"""
                SELECT ddi.severity, ddi.description,
                       m1.medication_name as med1_name, m2.medication_name as med2_name
                FROM drug_drug_interactions ddi
                JOIN medications m1 ON ddi.medication_id_1 = m1.medication_id
                JOIN medications m2 ON ddi.medication_id_2 = m2.medication_id
                WHERE (ddi.medication_id_1 = %s AND ddi.medication_id_2 IN ({placeholders}))
                   OR (ddi.medication_id_2 = %s AND ddi.medication_id_1 IN ({placeholders}))
            """, (med_id, *active_med_ids, med_id, *active_med_ids))
            interactions = cursor.fetchall()

            if interactions:
                warning_text = "Drug-Drug Interactions Detected:\n\n"
                for inter in interactions:
                    warning_text += (
                        f"[{inter.get('severity', 'Unknown')}] "
                        f"{inter.get('med1_name', '')} + {inter.get('med2_name', '')}\n"
                        f"  {inter.get('description', 'No description')}\n\n"
                    )
                warning_text += "Continue with this prescription?"

                result = QMessageBox.warning(
                    self, "Drug-Drug Interaction Warning",
                    warning_text,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if result == QMessageBox.StandardButton.No:
                    raise InterruptedError("Pharmacist declined due to drug-drug interaction")

        except InterruptedError:
            raise
        except Exception as e:
            # Don't block workflow if interaction check fails
            print(f"Drug-drug interaction check error: {e}")
