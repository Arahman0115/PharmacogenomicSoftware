"""Verification Queue - Final pharmacist verification before release to patient"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QDialog, QGroupBox, QFormLayout, QTextEdit, QCheckBox, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from .base_queue_view import BaseQueueView
from ui.views.audit_log_dialog import log_transition


class VerificationQueueView(BaseQueueView):
    """Verification queue - pharmacist final check before release"""

    TABLE_NAME = "ActivatedPrescriptions"
    WINDOW_TITLE = "Verification Queue"
    COLUMNS = [
        "Rx #", "Patient", "Medication", "Quantity",
        "Bottle Info", "Status", "Last Updated"
    ]
    COLUMN_KEYS = [
        "rx_id", "patient_name", "medication_name", "quantity_dispensed",
        "bottle_info", "status", "last_updated"
    ]

    def __init__(self, db_connection, parent=None):
        super().__init__(db_connection, parent)

    def load_data(self):
        """Load prescriptions pending verification"""
        if not self.db_connection:
            return

        try:
            query = """
                SELECT
                    p.prescription_id as rx_id,
                    CONCAT(pt.first_name, ', ', pt.last_name) as patient_name,
                    COALESCE(m.medication_name, 'Unknown') as medication_name,
                    p.quantity_dispensed,
                    COALESCE(CONCAT('Bottle #', ib.bottle_id, ' (NDC: ', b.ndc, ')'), 'N/A') as bottle_info,
                    p.status,
                    p.last_updated,
                    pt.user_id,
                    p.medication_id,
                    p.rx_store_num,
                    p.store_number,
                    ib.bottle_id
                FROM ActivatedPrescriptions p
                JOIN patientsinfo pt ON p.user_id = pt.user_id
                LEFT JOIN medications m ON p.medication_id = m.medication_id
                LEFT JOIN inusebottles ib ON p.prescription_id = ib.prescription_id
                LEFT JOIN bottles b ON ib.bottle_id = b.bottle_id
                WHERE p.status = 'verification_pending'
                ORDER BY p.last_updated ASC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            self.db_connection.cursor.execute(query, (self.page_size, offset))
            rows = self.db_connection.cursor.fetchall()

            # Get total count
            self.db_connection.cursor.execute(
                "SELECT COUNT(*) as count FROM ActivatedPrescriptions WHERE status = 'verification_pending'"
            )
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading verification queue: {e}")

    def on_row_double_clicked(self, item):
        """Open verification dialog"""
        row = item.row()
        row_item = self.table.item(row, 0)
        if not row_item:
            return

        row_data = row_item.data(256)

        if row_data:
            dialog = VerificationDialog(self.db_connection, row_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()


class VerificationDialog(QDialog):
    """Dialog for pharmacist verification of prescription before release"""

    def __init__(self, db_connection, rx_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data
        self.rx_id = rx_data.get('rx_id')
        self.user_id = rx_data.get('user_id')
        self.medication_id = rx_data.get('medication_id')

        self.setWindowTitle(f"Verify - {rx_data.get('patient_name')}")
        self.setGeometry(100, 100, 700, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Prescription info (read-only)
        info_group = QGroupBox("Prescription Information")
        info_layout = QFormLayout()
        info_layout.addRow("Patient:", QLabel(self.rx_data.get('patient_name', '')))
        info_layout.addRow("Medication:", QLabel(self.rx_data.get('medication_name', '')))
        info_layout.addRow("Quantity:", QLabel(str(self.rx_data.get('quantity_dispensed', ''))))
        info_layout.addRow("Bottle:", QLabel(self.rx_data.get('bottle_info', 'N/A')))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Drug-gene warnings (if any)
        warnings_group = QGroupBox("Drug-Gene Warnings")
        warnings_layout = QVBoxLayout()
        self.warnings_label = QLabel("Loading...")
        warnings_layout.addWidget(self.warnings_label)
        warnings_group.setLayout(warnings_layout)
        layout.addWidget(warnings_group)
        self.load_warnings()

        # Verification checklist
        checklist_group = QGroupBox("Verification Checklist")
        checklist_layout = QVBoxLayout()

        self.check_patient = QCheckBox("Correct patient identified")
        self.check_medication = QCheckBox("Correct medication verified")
        self.check_quantity = QCheckBox("Correct quantity confirmed")
        self.check_interactions = QCheckBox("Drug interactions reviewed")
        self.check_sig = QCheckBox("SIG / Instructions verified")

        checklist_layout.addWidget(self.check_patient)
        checklist_layout.addWidget(self.check_medication)
        checklist_layout.addWidget(self.check_quantity)
        checklist_layout.addWidget(self.check_interactions)
        checklist_layout.addWidget(self.check_sig)

        checklist_group.setLayout(checklist_layout)
        layout.addWidget(checklist_group)

        # Pharmacist notes
        notes_group = QGroupBox("Pharmacist Notes")
        notes_layout = QVBoxLayout()
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Optional verification notes...")
        notes_layout.addWidget(self.notes_edit)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        return_btn = QPushButton("Return to Dispensing")
        return_btn.setProperty("cssClass", "warning")
        return_btn.clicked.connect(self.return_to_dispensing)
        button_layout.addWidget(return_btn)

        verify_btn = QPushButton("Verify & Release")
        verify_btn.setProperty("cssClass", "success")
        verify_btn.clicked.connect(self.verify_and_release)
        button_layout.addWidget(verify_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_warnings(self):
        """Load drug-gene warnings for this patient + medication"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                SELECT gene, variant, risk_level, description
                FROM drug_review
                WHERE user_id = %s AND medication_id = %s AND status = 'active'
            """, (self.user_id, self.medication_id))
            warnings = cursor.fetchall()

            if warnings:
                warning_text = ""
                for w in warnings:
                    warning_text += (
                        f"Gene: {w.get('gene', 'N/A')} | "
                        f"Variant: {w.get('variant', 'N/A')} | "
                        f"Risk: {w.get('risk_level', 'N/A')}\n"
                        f"  {w.get('description', '')}\n\n"
                    )
                self.warnings_label.setText(warning_text.strip())
                self.warnings_label.setProperty("cssClass", "error-text")
                self.warnings_label.style().unpolish(self.warnings_label)
                self.warnings_label.style().polish(self.warnings_label)
            else:
                self.warnings_label.setText("No drug-gene warnings for this prescription.")
                self.warnings_label.setProperty("cssClass", "text-secondary")
                self.warnings_label.style().unpolish(self.warnings_label)
                self.warnings_label.style().polish(self.warnings_label)

        except Exception as e:
            self.warnings_label.setText(f"Could not load warnings: {e}")

    def verify_and_release(self):
        """Verify all checks and release prescription"""
        # Validate all checkboxes are checked
        checks = [
            self.check_patient, self.check_medication,
            self.check_quantity, self.check_interactions, self.check_sig
        ]
        if not all(cb.isChecked() for cb in checks):
            QMessageBox.warning(
                self, "Incomplete Verification",
                "All verification items must be checked before releasing."
            )
            return

        try:
            cursor = self.db_connection.cursor

            # Insert into ReadyForPickUp
            cursor.execute("""
                INSERT INTO ReadyForPickUp
                (user_id, medication_id, rx_store_num, quantity, ready_date, payment_status, status)
                SELECT user_id, medication_id, rx_store_num, quantity_dispensed, NOW(), 'Pending', 'ready'
                FROM ActivatedPrescriptions
                WHERE prescription_id = %s
            """, (self.rx_id,))

            # Update ActivatedPrescriptions status
            cursor.execute("""
                UPDATE ActivatedPrescriptions
                SET status = 'released_to_pickup'
                WHERE prescription_id = %s
            """, (self.rx_id,))

            notes = self.notes_edit.toPlainText() or None
            log_transition(
                self.db_connection, self.rx_id,
                'verification_pending', 'released_to_pickup',
                'Pharmacist verification complete - released to pickup',
                notes=notes
            )
            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Verified",
                f"Prescription verified for {self.rx_data.get('patient_name')}.\n"
                f"Released to pickup queue."
            )
            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to verify: {e}")

    def return_to_dispensing(self):
        """Return prescription back to product dispensing"""
        try:
            cursor = self.db_connection.cursor

            cursor.execute("""
                UPDATE ActivatedPrescriptions
                SET status = 'product_dispensing_pending'
                WHERE prescription_id = %s
            """, (self.rx_id,))

            log_transition(
                self.db_connection, self.rx_id,
                'verification_pending', 'product_dispensing_pending',
                'Returned to dispensing from verification'
            )
            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Returned",
                f"Prescription returned to Product Dispensing Queue."
            )
            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to return: {e}")
