"""Drug Review Queue - Pharmacist review and approval of drug-gene interactions"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox,
    QDialog, QGroupBox, QFormLayout, QTextEdit
)
from PyQt6.QtCore import Qt
from .base_queue_view import BaseQueueView
from ui.views.audit_log_dialog import log_transition


class DrugReviewQueueView(BaseQueueView):
    """Drug Review queue - pharmacist review of drug-gene interactions"""

    TABLE_NAME = "drugreviewqueue"
    WINDOW_TITLE = "Drug Review Queue"
    COLUMNS = [
        "Rx #", "Patient", "Medication", "Gene",
        "Variant", "Risk Level", "Status"
    ]
    COLUMN_KEYS = [
        "rx_id", "patient_name", "medication_name", "gene",
        "variant", "risk_level", "status"
    ]

    def __init__(self, db_connection, parent=None):
        self.risk_filter = None
        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create filters for drug review queue"""
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Risk Level:"))
        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All", "High", "Moderate", "Low"])
        row1_layout.addWidget(self.risk_filter)
        row1_layout.addStretch()
        parent_layout.addLayout(row1_layout)

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
        """Load drug review queue data - combines drugreviewqueue with drug_review for variant info"""
        if not self.db_connection:
            return

        try:
            # Get from drugreviewqueue but JOIN with drug_review to get gene/variant
            query = """
                SELECT
                    drq.id,
                    drq.prescription_id as rx_id,
                    drq.user_id,
                    drq.medication_id,
                    CONCAT(pt.first_name, ' ', pt.last_name) as patient_name,
                    COALESCE(m.medication_name, 'Unknown') as medication_name,
                    COALESCE(dr.gene, '') as gene,
                    COALESCE(dr.variant, '') as variant,
                    drq.risk_level,
                    drq.status,
                    drq.created_date
                FROM drugreviewqueue drq
                JOIN patientsinfo pt ON drq.user_id = pt.user_id
                LEFT JOIN medications m ON drq.medication_id = m.medication_id
                LEFT JOIN drug_review dr ON drq.medication_id = dr.medication_id
                    AND dr.status = 'active'
                WHERE drq.status = 'pending'
                ORDER BY
                    CASE drq.risk_level
                        WHEN 'High' THEN 1
                        WHEN 'Moderate' THEN 2
                        WHEN 'Low' THEN 3
                        ELSE 4
                    END,
                    drq.created_date ASC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            self.db_connection.cursor.execute(query, (self.page_size, offset))
            rows = self.db_connection.cursor.fetchall()

            # Get total count (only pending, not approved)
            self.db_connection.cursor.execute(
                "SELECT COUNT(*) as count FROM drugreviewqueue WHERE status = 'pending'"
            )
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading drug review queue: {e}")

    def apply_filters_clicked(self):
        """Apply filters and reload queue"""
        self.current_page = 0
        self.load_data()

    def reset_filters(self):
        """Reset all filters"""
        self.risk_filter.setCurrentIndex(0)
        self.current_page = 0
        self.load_data()

    def on_row_double_clicked(self, item):
        """Open drug review approval dialog"""
        row = item.row()
        row_item = self.table.item(row, 0)
        if not row_item:
            return

        row_data = row_item.data(Qt.ItemDataRole.UserRole)

        if row_data:
            # Open approval dialog
            dialog = DrugReviewApprovalDialog(self.db_connection, row_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()


class DrugReviewApprovalDialog(QDialog):
    """Dialog for approving or rejecting drug review items"""

    def __init__(self, db_connection, rx_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data
        self.drq_id = rx_data.get('id')
        self.rx_id = rx_data.get('rx_id')
        self.user_id = rx_data.get('user_id')
        self.medication_id = rx_data.get('medication_id')

        self.setWindowTitle(f"Drug Review - {rx_data.get('patient_name')}")
        self.setGeometry(100, 100, 700, 500)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Patient and Medication Info
        info_group = QGroupBox("Prescription Information")
        info_layout = QFormLayout()

        info_layout.addRow("Patient:", QLabel(self.rx_data.get('patient_name', '')))
        info_layout.addRow("Medication:", QLabel(self.rx_data.get('medication_name', '')))
        info_layout.addRow("Risk Level:", QLabel(self.rx_data.get('risk_level', '')))

        if self.rx_data.get('gene'):
            info_layout.addRow("Gene:", QLabel(self.rx_data.get('gene', '')))
        if self.rx_data.get('variant'):
            info_layout.addRow("Variant:", QLabel(self.rx_data.get('variant', '')))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Review Notes
        notes_group = QGroupBox("Pharmacist Notes")
        notes_layout = QFormLayout()

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        self.notes_edit.setPlaceholderText(
            "Optional: Document your review decision, concerns, or recommendations..."
        )
        notes_layout.addRow(self.notes_edit)

        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Reject button
        reject_btn = QPushButton("Reject / Contact Prescriber")
        reject_btn.setProperty("cssClass", "danger")
        reject_btn.clicked.connect(self.reject_prescription)
        button_layout.addWidget(reject_btn)

        # Approve button
        approve_btn = QPushButton("Approve & Continue")
        approve_btn.setProperty("cssClass", "success")
        approve_btn.clicked.connect(self.approve_prescription)
        button_layout.addWidget(approve_btn)

        # Cancel
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def approve_prescription(self):
        """Approve the drug review and move to product dispensing"""
        try:
            cursor = self.db_connection.cursor
            notes = self.notes_edit.toPlainText()

            # Update drugreviewqueue - mark as approved
            cursor.execute("""
                UPDATE drugreviewqueue
                SET status = 'approved',
                    reviewed_by = 'pharmacist',
                    reviewed_date = NOW(),
                    notes = %s
                WHERE id = %s
            """, (notes, self.drq_id))

            # Update ActivatedPrescriptions - move to product dispensing
            cursor.execute("""
                UPDATE ActivatedPrescriptions
                SET status = 'product_dispensing_pending'
                WHERE prescription_id = %s
            """, (self.rx_id,))

            log_transition(
                self.db_connection, self.rx_id,
                'drug_review_pending', 'product_dispensing_pending',
                'Drug review approved by pharmacist', notes=notes
            )
            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Approved",
                f"Prescription approved for {self.rx_data.get('patient_name')}\n"
                f"Moving to Product Dispensing Queue..."
            )

            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to approve: {e}")

    def reject_prescription(self):
        """Reject the prescription and require prescriber contact"""
        try:
            cursor = self.db_connection.cursor
            notes = self.notes_edit.toPlainText() or "Prescription rejected - requires prescriber contact"

            # Update drugreviewqueue - mark as rejected
            cursor.execute("""
                UPDATE drugreviewqueue
                SET status = 'rejected',
                    reviewed_by = 'pharmacist',
                    reviewed_date = NOW(),
                    notes = %s
                WHERE id = %s
            """, (notes, self.drq_id))

            # Update ActivatedPrescriptions - move back for revision
            cursor.execute("""
                UPDATE ActivatedPrescriptions
                SET status = 'rejected'
                WHERE prescription_id = %s
            """, (self.rx_id,))

            log_transition(
                self.db_connection, self.rx_id,
                'drug_review_pending', 'rejected',
                'Drug review rejected - prescriber contact required', notes=notes
            )
            self.db_connection.connection.commit()

            QMessageBox.warning(
                self, "Rejected",
                f"⚠ Prescription flagged for revision\n"
                f"Prescriber contact required for {self.rx_data.get('patient_name')}"
            )

            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to reject: {e}")
