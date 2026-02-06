"""Rx Number and NDC verification dialog after bottle selection"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt


class RxVerificationDialog(QDialog):
    """Dialog for verifying Rx number and NDC after bottle selection"""

    def __init__(self, db_connection, rx_data, bottle_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data  # Contains rx_number, patient_name, medication_name, etc.
        self.bottle_data = bottle_data  # Contains bottle_id, ndc, quantity, etc.
        self.verified = False

        self.setWindowTitle("Verify Prescription & Medication")
        self.setGeometry(200, 200, 500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Info section (read-only)
        info_group = QGroupBox("Prescription Information")
        info_layout = QFormLayout()
        info_layout.addRow("Patient:", QLabel(self.rx_data.get('patient_name', '')))
        info_layout.addRow("Medication:", QLabel(self.rx_data.get('medication_name', '')))
        info_layout.addRow("Bottle Selected:", QLabel(f"ID: {self.bottle_data.get('bottle_id')}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Verification section
        verify_group = QGroupBox("Verification Required")
        verify_layout = QFormLayout()

        # Rx Number verification
        verify_layout.addRow(QLabel("<b>Step 1: Verify Rx Number</b>"), QLabel(""))
        expected_rx = self.rx_data.get('rx_number', '')
        verify_layout.addRow("Expected Rx #:", QLabel(expected_rx))

        self.rx_input = QLineEdit()
        self.rx_input.setPlaceholderText(f"Enter: {expected_rx}")
        verify_layout.addRow("Enter Rx #:", self.rx_input)

        verify_layout.addRow(QLabel(""), QLabel(""))

        # NDC verification
        verify_layout.addRow(QLabel("<b>Step 2: Verify Medication NDC</b>"), QLabel(""))
        expected_ndc = self.bottle_data.get('ndc', '')
        verify_layout.addRow("Expected NDC:", QLabel(expected_ndc))

        self.ndc_input = QLineEdit()
        self.ndc_input.setPlaceholderText(f"Enter: {expected_ndc}")
        verify_layout.addRow("Enter NDC:", self.ndc_input)

        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        verify_btn = QPushButton("Verify & Continue")
        verify_btn.setProperty("cssClass", "success")
        verify_btn.clicked.connect(self.verify_and_continue)
        button_layout.addWidget(verify_btn)

        return_btn = QPushButton("Return to Bottle Selection")
        return_btn.setProperty("cssClass", "secondary")
        return_btn.clicked.connect(self.reject)
        button_layout.addWidget(return_btn)

        cancel_btn = QPushButton("Cancel Prescription")
        cancel_btn.setProperty("cssClass", "danger")
        cancel_btn.clicked.connect(self.cancel_prescription)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def verify_and_continue(self):
        """Verify inputs and proceed if valid"""
        rx_entered = self.rx_input.text().strip()
        ndc_entered = self.ndc_input.text().strip()

        expected_rx = self.rx_data.get('rx_number', '')
        expected_ndc = self.bottle_data.get('ndc', '')

        # Verify Rx number
        if not rx_entered:
            QMessageBox.warning(self, "Missing Input", "Please enter the Rx number")
            return

        if rx_entered.upper() != expected_rx.upper():
            QMessageBox.critical(
                self, "Rx Number Mismatch",
                f"Entered Rx number does not match.\n\n"
                f"Expected: {expected_rx}\n"
                f"Entered: {rx_entered}"
            )
            return

        # Verify NDC
        if not ndc_entered:
            QMessageBox.warning(self, "Missing Input", "Please enter the NDC")
            return

        if ndc_entered.upper() != expected_ndc.upper():
            QMessageBox.critical(
                self, "NDC Mismatch",
                f"Entered NDC does not match bottle.\n\n"
                f"Expected: {expected_ndc}\n"
                f"Entered: {ndc_entered}"
            )
            return

        # All verified - accept and proceed
        self.verified = True
        self.accept()

    def cancel_prescription(self):
        """Cancel the prescription and move to patient history"""
        result = QMessageBox.warning(
            self, "Cancel Prescription",
            "Are you sure you want to cancel this prescription?\n\n"
            "The prescription will be moved to the patient's history with "
            "the remaining refills available.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            self.move_to_patient_history()

    def move_to_patient_history(self):
        """Move prescription from ActivatedPrescriptions to Prescriptions table"""
        try:
            cursor = self.db_connection.cursor
            prescription_id = self.rx_data.get('prescription_id')
            user_id = self.rx_data.get('user_id')
            medication_id = self.rx_data.get('medication_id')

            # Get current prescription details
            cursor.execute(
                """SELECT quantity_dispensed, rx_store_num, first_name, last_name
                   FROM ActivatedPrescriptions WHERE prescription_id = %s""",
                (prescription_id,)
            )
            ap_data = cursor.fetchone()
            if not ap_data:
                raise Exception("Prescription not found in ActivatedPrescriptions")

            # Get medication details
            cursor.execute(
                "SELECT medication_name FROM medications WHERE medication_id = %s",
                (medication_id,)
            )
            med_data = cursor.fetchone()
            med_name = med_data.get('medication_name', '') if med_data else ''

            # Get bottle allocation info before deleting
            cursor.execute(
                "SELECT bottle_id, quantity_used FROM inusebottles WHERE prescription_id = %s",
                (prescription_id,)
            )
            bottle_allocation = cursor.fetchone()

            # Move to Prescriptions table (patient history)
            insert_query = """
                INSERT INTO Prescriptions
                (user_id, medication_id, quantity_dispensed, refills_remaining,
                 instructions, status, rx_store_num, fill_date, last_fill_date)
                VALUES (%s, %s, %s, 1, %s, 'cancelled_not_dispensed', %s, NOW(), NOW())
            """

            cursor.execute(insert_query, (
                user_id,
                medication_id,
                ap_data.get('quantity_dispensed', 0),
                '',  # instructions - not available in ActivatedPrescriptions
                ap_data.get('rx_store_num', '03102')
            ))

            # Restore bottle quantity if it was allocated
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
                "DELETE FROM ProductSelectionQueue WHERE user_id = %s AND product = %s AND status IN ('pending', 'in_progress')",
                (user_id, med_name)
            )

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"Prescription cancelled and moved to patient history.\n"
                f"Patient: {ap_data.get('first_name')} {ap_data.get('last_name')}\n"
                f"Medication: {med_name}"
            )

            # Set cancelled flag and close dialog
            self.verified = False
            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to cancel prescription: {e}")
