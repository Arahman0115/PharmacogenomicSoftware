from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit
)
from datetime import datetime
from .base_queue_view import BaseQueueView
from ui.views.audit_log_dialog import log_transition
from .allscripts_ready_for_pt import AllScriptsReadyForPtView


class ReleaseQueueView(BaseQueueView):
    """Release to Patient queue - final dispensing and payment"""

    TABLE_NAME = "ReadyForPickUp"
    WINDOW_TITLE = "Release to Patient Queue"
    COLUMNS = [
        "Rx #", "Patient", "Medication", "Ready Date",
        "Payment Status", "Quantity", "Status"
    ]
    COLUMN_KEYS = [
        "rx_id", "patient_name", "medication_name", "ready_date",
        "payment_status", "quantity", "status"
    ]

    def __init__(self, db_connection, parent=None):
        self.patient_name_filter = None
        self.payment_filter = None
        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create filters for release queue"""
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Patient Name:"))
        self.patient_name_filter = QLineEdit()
        self.patient_name_filter.setPlaceholderText("Search by patient name...")
        self.patient_name_filter.setMinimumWidth(300)
        row1_layout.addWidget(self.patient_name_filter)
        row1_layout.addStretch()
        parent_layout.addLayout(row1_layout)

        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("Payment Status:"))
        self.payment_filter = QComboBox()
        self.payment_filter.addItems(["All", "Paid", "Pending", "Insurance"])
        row2_layout.addWidget(self.payment_filter)
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
        """Load release queue data"""
        if not self.db_connection:
            return

        try:
            # Build WHERE clause based on filters
            where_clauses = []
            params = []

            # Patient name filter
            patient_name = self.patient_name_filter.text().strip() if self.patient_name_filter else ""
            if patient_name:
                where_clauses.append(
                    "CONCAT(pt.first_name, ' ', pt.last_name) LIKE %s"
                )
                params.append(f"%{patient_name}%")

            # Payment status filter
            if self.payment_filter and self.payment_filter.currentText() != "All":
                where_clauses.append("r.payment_status = %s")
                params.append(self.payment_filter.currentText())

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f"""
                SELECT
                    r.id as rx_id,
                    r.rx_store_num,
                    CONCAT(pt.first_name, ', ', pt.last_name) as patient_name,
                    m.medication_name,
                    r.ready_date,
                    r.payment_status,
                    r.quantity,
                    r.status,
                    pt.user_id
                FROM ReadyForPickUp r
                JOIN patientsinfo pt ON r.user_id = pt.user_id
                LEFT JOIN medications m ON r.medication_id = m.medication_id
                WHERE {where_clause}
                ORDER BY r.ready_date ASC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            params.extend([self.page_size, offset])
            self.db_connection.cursor.execute(query, params)
            rows = self.db_connection.cursor.fetchall()

            # Get total count with filters applied
            count_query = f"""
                SELECT COUNT(*) as count FROM ReadyForPickUp r
                JOIN patientsinfo pt ON r.user_id = pt.user_id
                WHERE {where_clause}
            """
            count_params = params[:-2]  # Remove LIMIT params
            self.db_connection.cursor.execute(count_query, count_params)
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading release queue: {e}")

    def apply_filters_clicked(self):
        """Apply filters and reload queue"""
        self.current_page = 0
        self.load_data()

    def reset_filters(self):
        """Reset all filters"""
        self.patient_name_filter.clear()
        self.payment_filter.setCurrentIndex(0)
        self.current_page = 0
        self.load_data()

    def on_row_double_clicked(self, item):
        """Show all prescriptions for patient with release option"""
        row = item.row()
        row_data = self.table.item(row, 0).data(256)

        if row_data:
            # Open the all scripts view as a modal dialog
            dialog = AllScriptsReadyForPtView(
                self.db_connection,
                row_data,
                parent=self
            )
            dialog.exec()

    def release_prescription(self, prescription_data):
        """Release prescription to patient"""
        try:
            rx_id = prescription_data.get('rx_id')
            user_id = prescription_data.get('user_id')

            # Move to FinishedTransactions
            release_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            insert_query = """
                INSERT INTO FinishedTransactions
                (user_id, rx_store_num, medication_id, quantity, release_time, status)
                SELECT user_id, rx_store_num, medication_id, quantity, %s, 'released'
                FROM ReadyForPickUp WHERE id = %s
            """
            self.db_connection.cursor.execute(insert_query, (release_time, rx_id))

            # Delete from ReadyForPickUp
            self.db_connection.cursor.execute("DELETE FROM ReadyForPickUp WHERE id = %s", (rx_id,))

            log_transition(
                self.db_connection, rx_id,
                'released_to_pickup', 'completed',
                'Prescription released to patient'
            )
            self.db_connection.connection.commit()
            QMessageBox.information(self, "Success", "Prescription released to patient")
            self.load_data()
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to release: {e}")
            self.db_connection.connection.rollback()
            return False
