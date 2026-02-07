"""Contact Queue - Prescriber contact hub for refills, clarifications, and genetic info requests"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QDialog, QGroupBox, QFormLayout, QTextEdit, QComboBox, QTableWidgetItem,
    QTableWidget, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from .base_queue_view import BaseQueueView


class ContactQueueView(BaseQueueView):
    """Contact queue - manage prescriber contacts for refills, clarifications, and genetic info"""

    TABLE_NAME = "contact_requests"
    WINDOW_TITLE = "Contact Queue"
    COLUMNS = [
        "Patient", "Request Type", "Reason", "Prescriber/Med", "Status", "Fax Count", "Created"
    ]
    COLUMN_KEYS = [
        "patient_name", "request_type", "reason", "prescriber_or_med",
        "status", "fax_send_count", "created_at"
    ]

    def __init__(self, db_connection, parent=None):
        self.status_filter = None
        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create filters for contact queue"""
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Pending", "Sent", "Resolved"])
        row_layout.addWidget(self.status_filter)
        row_layout.addStretch()

        filter_btn = QPushButton("Filter")
        filter_btn.setProperty("cssClass", "primary")
        filter_btn.clicked.connect(self.apply_filters_clicked)
        row_layout.addWidget(filter_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setProperty("cssClass", "secondary")
        reset_btn.clicked.connect(self.reset_filters)
        row_layout.addWidget(reset_btn)

        parent_layout.addLayout(row_layout)

    def load_data(self):
        """Load contact requests"""
        if not self.db_connection:
            return

        try:
            status_filter = self.status_filter.currentText() if self.status_filter else "All"

            query = """
                SELECT
                    cr.id,
                    cr.user_id,
                    CONCAT(pi.first_name, ' ', pi.last_name) as patient_name,
                    cr.request_type,
                    cr.reason,
                    COALESCE(CONCAT(pr.last_name, ', ', pr.first_name), m.medication_name, 'N/A') as prescriber_or_med,
                    cr.status,
                    cr.fax_send_count,
                    cr.created_at,
                    cr.prescriber_id,
                    cr.prescription_id,
                    cr.medication_id,
                    cr.delivery_method,
                    cr.delivery_value
                FROM contact_requests cr
                JOIN patientsinfo pi ON cr.user_id = pi.user_id
                LEFT JOIN Prescribers pr ON cr.prescriber_id = pr.prescriber_id
                LEFT JOIN medications m ON cr.medication_id = m.medication_id
                WHERE 1=1
            """

            params = []
            if status_filter != "All":
                query += " AND cr.status = %s"
                params.append(status_filter.lower())

            query += " ORDER BY cr.created_at DESC LIMIT %s OFFSET %s"
            params.extend([self.page_size, self.get_offset()])

            self.db_connection.cursor.execute(query, tuple(params))
            rows = self.db_connection.cursor.fetchall()

            # Get total count
            count_query = """
                SELECT COUNT(*) as count FROM contact_requests cr
                WHERE 1=1
            """
            if status_filter != "All":
                count_query += " AND cr.status = %s"
                self.db_connection.cursor.execute(count_query, (status_filter.lower(),))
            else:
                self.db_connection.cursor.execute(count_query)

            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading contact queue: {e}")

    def display_data(self, rows):
        """Display data with custom row coloring"""
        self.table.setRowCount(0)

        for row_idx, row in enumerate(rows):
            self.table.insertRow(row_idx)

            # Store full data
            item = QTableWidgetItem(row.get('patient_name', ''))
            item.setData(Qt.ItemDataRole.UserRole, row)
            self.table.setItem(row_idx, 0, item)

            # Request type (with color)
            request_type = row.get('request_type', '')
            type_item = QTableWidgetItem(request_type.replace('_', ' ').title())

            # Color code by type
            if request_type == 'refill':
                type_item.setBackground(QColor(70, 150, 180))  # Blue
            elif request_type == 'rx_clarification':
                type_item.setBackground(QColor(200, 140, 60))  # Orange
            elif request_type == 'genetic_info':
                type_item.setBackground(QColor(120, 160, 100))  # Green

            self.table.setItem(row_idx, 1, type_item)

            # Reason
            self.table.setItem(row_idx, 2, QTableWidgetItem(row.get('reason', '')))

            # Prescriber or Medication
            self.table.setItem(row_idx, 3, QTableWidgetItem(row.get('prescriber_or_med', 'N/A')))

            # Status
            self.table.setItem(row_idx, 4, QTableWidgetItem(row.get('status', '').title()))

            # Fax count
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(row.get('fax_send_count', 0))))

            # Created date
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(row.get('created_at', ''))))

    def apply_filters_clicked(self):
        """Apply filters"""
        self.current_page = 0
        self.load_data()

    def reset_filters(self):
        """Reset all filters"""
        self.status_filter.setCurrentIndex(0)
        self.current_page = 0
        self.load_data()

    def on_row_double_clicked(self, item):
        """Open contact request detail dialog"""
        row = item.row()
        row_item = self.table.item(row, 0)
        if not row_item:
            return

        row_data = row_item.data(Qt.ItemDataRole.UserRole)

        if row_data:
            dialog = ContactRequestDialog(self.db_connection, row_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()


class ContactRequestDialog(QDialog):
    """Dialog for viewing and managing contact requests"""

    def __init__(self, db_connection, request_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.request_data = request_data
        self.request_id = request_data.get('id')
        self.request_type = request_data.get('request_type')

        title_map = {
            'refill': 'Refill Request',
            'rx_clarification': 'Rx Clarification Request',
            'genetic_info': 'Genetic Information Request'
        }
        self.setWindowTitle(title_map.get(self.request_type, 'Contact Request'))
        self.setGeometry(100, 100, 700, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Patient Info
        info_group = QGroupBox("Request Information")
        info_layout = QFormLayout()

        info_layout.addRow("Patient:", self.create_label(self.request_data.get('patient_name', '')))
        info_layout.addRow("Request Type:", self.create_label(self.request_data.get('request_type', '').replace('_', ' ').title()))
        info_layout.addRow("Status:", self.create_label(self.request_data.get('status', '').title()))
        info_layout.addRow("Created:", self.create_label(str(self.request_data.get('created_at', ''))))
        info_layout.addRow("Times Sent:", self.create_label(str(self.request_data.get('fax_send_count', 0))))

        # Show prescriber for refill/clarification
        if self.request_type in ['refill', 'rx_clarification']:
            info_layout.addRow("Prescriber:", self.create_label(self.request_data.get('prescriber_or_med', '')))
            info_layout.addRow("Medication:", self.create_label(self.get_medication_name()))
        else:
            info_layout.addRow("Medication:", self.create_label(self.request_data.get('prescriber_or_med', '')))

        info_layout.addRow("Reason:", self.create_label(self.request_data.get('reason', '')))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Delivery Method
        delivery_group = QGroupBox("Delivery Method")
        delivery_layout = QFormLayout()

        delivery_layout.addRow("Method:", self.create_label(self.request_data.get('delivery_method', 'fax').title()))
        if self.request_data.get('delivery_value'):
            delivery_layout.addRow("Contact Info:", self.create_label(self.request_data.get('delivery_value', '')))

        delivery_group.setLayout(delivery_layout)
        layout.addWidget(delivery_group)

        # Fax Send Log
        fax_log_group = QGroupBox("Fax Send History")
        fax_log_layout = QVBoxLayout()

        self.fax_log_table = QTableWidget()
        self.fax_log_table.setColumnCount(2)
        self.fax_log_table.setHorizontalHeaderLabels(["Date & Time Sent", "Notes"])
        self.fax_log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.fax_log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.fax_log_table.setMaximumHeight(150)

        fax_log_layout.addWidget(self.fax_log_table)
        fax_log_group.setLayout(fax_log_layout)
        layout.addWidget(fax_log_group)

        # Load fax log
        self.load_fax_log()

        # Notes
        notes_group = QGroupBox("Notes")
        notes_layout = QFormLayout()

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(120)
        notes_layout.addRow(self.notes_edit)

        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.send_btn = QPushButton("Send Fax")
        self.send_btn.setProperty("cssClass", "success")
        self.send_btn.clicked.connect(self.send_fax)
        button_layout.addWidget(self.send_btn)

        resolve_btn = QPushButton("Mark Resolved")
        resolve_btn.setProperty("cssClass", "secondary")
        resolve_btn.clicked.connect(self.mark_resolved)
        button_layout.addWidget(resolve_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "ghost")
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def create_label(self, text):
        """Create a read-only label"""
        from PyQt6.QtWidgets import QLineEdit
        label = QLineEdit(text)
        label.setReadOnly(True)
        return label

    def get_medication_name(self):
        """Get medication name from prescription"""
        if self.request_data.get('prescription_id'):
            try:
                cursor = self.db_connection.cursor
                cursor.execute("""
                    SELECT m.medication_name FROM ActivatedPrescriptions ap
                    JOIN medications m ON ap.medication_id = m.medication_id
                    WHERE ap.prescription_id = %s
                """, (self.request_data.get('prescription_id'),))
                result = cursor.fetchone()
                return result.get('medication_name', 'Unknown') if result else 'Unknown'
            except Exception as e:
                print(f"Error getting medication name: {e}")
                return 'Unknown'
        return 'N/A'

    def load_fax_log(self):
        """Load fax send history from log"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                SELECT sent_at, notes FROM contact_request_fax_log
                WHERE contact_request_id = %s
                ORDER BY sent_at DESC
            """, (self.request_id,))
            fax_logs = cursor.fetchall()

            self.fax_log_table.setRowCount(len(fax_logs))
            for row_idx, log in enumerate(fax_logs):
                sent_time = str(log.get('sent_at', ''))
                notes = log.get('notes', '')

                self.fax_log_table.setItem(row_idx, 0, QTableWidgetItem(sent_time))
                self.fax_log_table.setItem(row_idx, 1, QTableWidgetItem(notes or ''))

        except Exception as e:
            print(f"Error loading fax log: {e}")

    def send_fax(self):
        """Send fax and log it"""
        try:
            cursor = self.db_connection.cursor

            # Insert into fax log
            cursor.execute("""
                INSERT INTO contact_request_fax_log
                (contact_request_id, sent_at, notes)
                VALUES (%s, NOW(), %s)
            """, (self.request_id, "Fax sent"))

            # Update fax_send_count for backwards compatibility
            new_count = self.request_data.get('fax_send_count', 0) + 1
            cursor.execute("""
                UPDATE contact_requests
                SET fax_send_count = %s
                WHERE id = %s
            """, (new_count, self.request_id))

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Fax Sent",
                f"Fax sent successfully to prescriber."
            )

            # Reload the fax log to show the new entry
            self.load_fax_log()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to send fax: {e}")

    def mark_resolved(self):
        """Mark request as resolved"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                UPDATE contact_requests
                SET status = 'resolved'
                WHERE id = %s
            """, (self.request_id,))

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                "Request marked as resolved."
            )

            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to mark resolved: {e}")
