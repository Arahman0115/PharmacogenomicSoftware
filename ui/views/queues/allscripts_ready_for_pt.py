"""All Scripts Ready for Patient - Shows all patient prescriptions with one ready for pickup"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
from ui.views.audit_log_dialog import log_transition


class AllScriptsReadyForPtView(QDialog):
    """Dialog showing all patient prescriptions with one ready for pickup"""

    def __init__(self, db_connection, ready_prescription_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.ready_prescription_data = ready_prescription_data
        self.user_id = ready_prescription_data.get('user_id')
        self.ready_rx_id = ready_prescription_data.get('rx_id')
        self.selected_row = None
        self.parent_view = parent

        self.setWindowTitle(f"Release Prescription - {ready_prescription_data.get('patient_name')}")
        self.setGeometry(100, 100, 1000, 600)
        self.init_ui()
        self.load_all_prescriptions()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Header with patient info
        header_group = QGroupBox("Patient Information")
        header_layout = QFormLayout()
        header_layout.addRow(
            "Patient:",
            QLabel(self.ready_prescription_data.get('patient_name', ''))
        )
        header_layout.addRow(
            "Ready Prescription:",
            QLabel(
                f"{self.ready_prescription_data.get('medication_name', '')} "
                f"(Qty: {self.ready_prescription_data.get('quantity', 0)})"
            )
        )
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # All prescriptions table
        table_group = QGroupBox("All Prescriptions for Patient")
        table_layout = QVBoxLayout()

        self.prescriptions_table = QTableWidget()
        self.prescriptions_table.setColumnCount(6)
        self.prescriptions_table.setHorizontalHeaderLabels([
            "Medication", "Quantity", "Status", "Created Date", "Refills", "Ready for Release"
        ])
        self.prescriptions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.prescriptions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.prescriptions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.prescriptions_table.setShowGrid(False)
        self.prescriptions_table.verticalHeader().setVisible(False)
        self.prescriptions_table.itemSelectionChanged.connect(self.on_row_selected)

        table_layout.addWidget(self.prescriptions_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group, 1)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        release_btn = QPushButton("Release to Patient")
        release_btn.setProperty("cssClass", "success")
        release_btn.clicked.connect(self.release_to_patient)
        button_layout.addWidget(release_btn)

        back_btn = QPushButton("Back to Queue")
        back_btn.setProperty("cssClass", "ghost")
        back_btn.clicked.connect(self.go_back)
        button_layout.addWidget(back_btn)

        layout.addLayout(button_layout)

    def format_status(self, status):
        """Format status string for display"""
        status_map = {
            'data_entry_pending': 'Data Entry Pending',
            'data_entry_complete': 'Data Entry Complete',
            'product_dispensing_pending': 'Awaiting Bottle Selection',
            'bottle_selected': 'Bottle Selected',
            'verification_pending': 'In Verification',
            'released_to_pickup': 'Ready for Pickup',
            'completed': 'Completed',
            'cancelled_not_dispensed': 'Cancelled',
            'rejected': 'Rejected',
            'drug_review_pending': 'Drug Review Pending',
        }
        return status_map.get(status, status)

    def load_all_prescriptions(self):
        """Load all prescriptions for the patient"""
        try:
            cursor = self.db_connection.cursor

            # Query all prescriptions for this patient - exclude those already in ReadyForPickUp from ActivatedPrescriptions
            query_activated = """
                SELECT
                    ap.prescription_id,
                    m.medication_name,
                    ap.quantity_dispensed,
                    ap.status,
                    ap.fill_date,
                    ap.rx_number,
                    0 as refills,
                    'activated' as source
                FROM ActivatedPrescriptions ap
                LEFT JOIN medications m ON ap.medication_id = m.medication_id
                WHERE ap.user_id = %s
                  AND ap.status NOT IN ('released_to_pickup', 'completed')
                UNION ALL
                SELECT
                    r.id as prescription_id,
                    m.medication_name,
                    r.quantity as quantity_dispensed,
                    'released_to_pickup' as status,
                    r.ready_date as fill_date,
                    '' as rx_number,
                    0 as refills,
                    'ready' as source
                FROM ReadyForPickUp r
                LEFT JOIN medications m ON r.medication_id = m.medication_id
                WHERE r.user_id = %s
                ORDER BY fill_date DESC
            """

            cursor.execute(query_activated, (self.user_id, self.user_id))
            prescriptions = cursor.fetchall()

            self.prescriptions_table.setRowCount(len(prescriptions))

            for row_idx, rx in enumerate(prescriptions):
                prescription_id = rx.get('prescription_id')
                is_ready = rx.get('source') == 'ready'  # Ready ones are from ReadyForPickUp table

                # Medication name
                med_item = QTableWidgetItem(rx.get('medication_name', ''))
                med_item.setData(Qt.ItemDataRole.UserRole, rx)
                if not is_ready:
                    med_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 0, med_item)

                # Quantity
                qty_item = QTableWidgetItem(str(rx.get('quantity_dispensed', 0)))
                if not is_ready:
                    qty_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 1, qty_item)

                # Status
                formatted_status = self.format_status(rx.get('status', ''))
                status_item = QTableWidgetItem(formatted_status)
                if not is_ready:
                    status_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 2, status_item)

                # Created date
                date_item = QTableWidgetItem(str(rx.get('fill_date', '')))
                if not is_ready:
                    date_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 3, date_item)

                # Refills
                refills_item = QTableWidgetItem(str(rx.get('refills', 0)))
                if not is_ready:
                    refills_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 4, refills_item)

                # Ready for release indicator
                ready_text = "✓ READY" if is_ready else ""
                ready_item = QTableWidgetItem(ready_text)
                if is_ready:
                    ready_item.setForeground(QColor("#4A90D9"))  # Blue for ready
                    ready_item.setBackground(QColor("#2A3A50"))  # Dark blue background
                else:
                    ready_item.setForeground(QColor("#808080"))
                self.prescriptions_table.setItem(row_idx, 5, ready_item)

                # Auto-select the ready prescription
                if is_ready:
                    self.prescriptions_table.selectRow(row_idx)
                    self.selected_row = row_idx

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load prescriptions: {e}")

    def on_row_selected(self):
        """Handle row selection"""
        selected_rows = self.prescriptions_table.selectionModel().selectedRows()
        if selected_rows:
            self.selected_row = selected_rows[0].row()
            selected_rx = self.prescriptions_table.item(self.selected_row, 0).data(Qt.ItemDataRole.UserRole)

            # Only allow selection of the ready prescription
            if selected_rx.get('source') != 'ready':
                QMessageBox.warning(
                    self, "Not Ready",
                    "Only the prescription marked as READY can be released.\n"
                    "Other prescriptions are still in the workflow."
                )
                # Try to find and select the ready row
                for row in range(self.prescriptions_table.rowCount()):
                    item = self.prescriptions_table.item(row, 0)
                    if item and item.data(Qt.ItemDataRole.UserRole).get('source') == 'ready':
                        self.prescriptions_table.selectRow(row)
                        self.selected_row = row
                        break

    def release_to_patient(self):
        """Release the selected prescription to patient"""
        if self.selected_row is None:
            QMessageBox.warning(self, "No Selection", "Please select a prescription to release")
            return

        selected_rx = self.prescriptions_table.item(self.selected_row, 0).data(Qt.ItemDataRole.UserRole)

        # Verify it's the ready prescription
        if selected_rx.get('source') != 'ready':
            QMessageBox.warning(
                self, "Error",
                "You can only release the prescription marked as READY for pickup."
            )
            return

        try:
            cursor = self.db_connection.cursor
            ready_rx_id = selected_rx.get('prescription_id')  # This is the id from ReadyForPickUp table

            # Move to FinishedTransactions
            release_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_query = """
                INSERT INTO FinishedTransactions
                (user_id, rx_store_num, medication_id, quantity, release_time, status)
                SELECT user_id, rx_store_num, medication_id, quantity, %s, 'released'
                FROM ReadyForPickUp WHERE id = %s
            """
            cursor.execute(insert_query, (release_time, ready_rx_id))

            # Delete from ReadyForPickUp
            cursor.execute("DELETE FROM ReadyForPickUp WHERE id = %s", (ready_rx_id,))

            log_transition(
                self.db_connection, ready_rx_id,
                'released_to_pickup', 'completed',
                'Prescription released to patient'
            )
            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"Prescription {selected_rx.get('medication_name')} has been released to patient!"
            )

            self.go_back()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to release prescription: {e}")

    def go_back(self):
        """Go back to release queue"""
        if self.parent_view:
            self.parent_view.load_data()
        self.reject()
