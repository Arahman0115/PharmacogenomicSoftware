"""Rx Search View - Global search across all prescriptions"""
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from .base_queue_view import BaseQueueView


class RxSearchView(BaseQueueView):
    """Rx Search view - global search across all prescriptions"""

    TABLE_NAME = "ActivatedPrescriptions"
    WINDOW_TITLE = "Search All Prescriptions"
    COLUMNS = [
        "Rx #", "Patient", "Medication", "Prescriber",
        "Filled Date", "Status", "Quantity"
    ]
    COLUMN_KEYS = [
        "rx_id", "patient_name", "medication_name", "prescriber_name",
        "fill_date", "status", "quantity_dispensed"
    ]

    # Signal emitted when prescription is selected from search
    prescription_selected = pyqtSignal(int, str)  # prescription_id, status

    def __init__(self, db_connection, parent=None):
        self.patient_search = None
        self.medication_search = None
        self.status_filter = None
        self.table_type_filter = None  # New: Activated vs Released filter
        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create search/filter controls"""
        row_layout = QHBoxLayout()

        # Table type filter (Activated vs Released)
        row_layout.addWidget(QLabel("Show:"))
        self.table_type_filter = QComboBox()
        self.table_type_filter.addItems(["Activated", "Released"])
        self.table_type_filter.currentTextChanged.connect(self.on_table_type_changed)
        row_layout.addWidget(self.table_type_filter)

        row_layout.addWidget(QLabel("Patient (Last, First):"))
        self.patient_search = QLineEdit()
        self.patient_search.setMinimumWidth(200)
        row_layout.addWidget(self.patient_search)

        row_layout.addWidget(QLabel("Medication:"))
        self.medication_search = QLineEdit()
        self.medication_search.setMinimumWidth(200)
        row_layout.addWidget(self.medication_search)

        row_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All", "Pending", "Data Entry Complete", "Product Dispensing Pending",
            "Bottle Selected", "Verification Pending", "Released to Pickup",
            "Completed", "Rejected"
        ])
        row_layout.addWidget(self.status_filter)

        search_btn = QPushButton("Search")
        search_btn.setProperty("cssClass", "primary")
        search_btn.clicked.connect(self.apply_filters_clicked)
        row_layout.addWidget(search_btn)

        parent_layout.addLayout(row_layout)

    def load_data(self):
        """Load all prescriptions or filtered results"""
        if not self.db_connection:
            return

        try:
            table_type = self.table_type_filter.currentText() if self.table_type_filter else "Activated"
            params = []

            # Build WHERE clause for common filters
            where_clause = ""
            patient_search = self.patient_search.text().strip()
            med_search = self.medication_search.text().strip()
            status = self.status_filter.currentText()

            if patient_search:
                if ',' in patient_search:
                    last_name, first_name = patient_search.split(',', 1)
                    where_clause += " AND pt.last_name LIKE %s AND pt.first_name LIKE %s"
                    params.extend([f"{last_name.strip()}%", f"{first_name.strip()}%"])
                else:
                    where_clause += " AND pt.last_name LIKE %s"
                    params.append(f"{patient_search}%")

            if med_search:
                where_clause += " AND m.medication_name LIKE %s"
                params.append(f"%{med_search}%")

            if status != "All":
                status_value = status.lower().replace(' ', '_')
                where_clause += " AND p.status = %s"
                params.append(status_value)

            # Query based on table type
            if table_type == "Activated":
                query = """
                    SELECT
                        p.prescription_id as rx_id,
                        CONCAT(pt.last_name, ', ', pt.first_name) as patient_name,
                        m.medication_name,
                        CONCAT(pr.last_name, ', ', pr.first_name) as prescriber_name,
                        p.fill_date,
                        p.status,
                        p.quantity_dispensed,
                        p.user_id
                    FROM ActivatedPrescriptions p
                    JOIN patientsinfo pt ON p.user_id = pt.user_id
                    LEFT JOIN medications m ON p.medication_id = m.medication_id
                    LEFT JOIN Prescribers pr ON p.prescriber_id = pr.prescriber_id
                    WHERE 1=1
                """ + where_clause
            else:  # Released
                query = """
                    SELECT
                        p.prescription_id as rx_id,
                        CONCAT(pt.last_name, ', ', pt.first_name) as patient_name,
                        m.medication_name,
                        CONCAT(pr.last_name, ', ', pr.first_name) as prescriber_name,
                        p.release_date as fill_date,
                        'released_to_pickup' as status,
                        p.quantity_dispensed,
                        p.user_id
                    FROM ReadyForPickUp p
                    JOIN patientsinfo pt ON p.user_id = pt.user_id
                    LEFT JOIN medications m ON p.medication_id = m.medication_id
                    LEFT JOIN Prescribers pr ON p.prescriber_id = pr.prescriber_id
                    WHERE 1=1
                """ + where_clause

            query += " ORDER BY fill_date DESC LIMIT %s OFFSET %s"
            params.extend([self.page_size, self.get_offset()])

            self.db_connection.cursor.execute(query, tuple(params))
            rows = self.db_connection.cursor.fetchall()

            # Get total count for pagination
            if table_type == "Activated":
                count_query = """
                    SELECT COUNT(*) as count FROM ActivatedPrescriptions p
                    JOIN patientsinfo pt ON p.user_id = pt.user_id
                    LEFT JOIN medications m ON p.medication_id = m.medication_id
                    WHERE 1=1
                """ + where_clause
            else:
                count_query = """
                    SELECT COUNT(*) as count FROM ReadyForPickUp p
                    JOIN patientsinfo pt ON p.user_id = pt.user_id
                    LEFT JOIN medications m ON p.medication_id = m.medication_id
                    WHERE 1=1
                """ + where_clause

            self.db_connection.cursor.execute(count_query, tuple(params[:len(params)-2]))
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_data(rows)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error searching prescriptions: {e}")

    def apply_filters_clicked(self):
        """Apply search filters"""
        self.current_page = 0
        self.load_data()

    def on_table_type_changed(self, text):
        """Handle table type filter change"""
        self.current_page = 0
        self.load_data()

    def on_row_double_clicked(self, item):
        """Handle prescription selection - emit signal to switch queue and open modal"""
        row = item.row()
        row_item = self.table.item(row, 0)
        if not row_item:
            return

        row_data = row_item.data(256)

        if row_data:
            rx_id = row_data.get('rx_id')
            status = row_data.get('status', 'unknown')

            # Emit signal to mainwindow to switch queue and open modal
            self.prescription_selected.emit(rx_id, status)
