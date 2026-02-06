from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDateEdit, QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import pyqtSignal, QDate
from config import Theme
from datetime import datetime


class PatientSearchWidget(QWidget):
    """Reusable patient search component

    Eliminates duplication between:
    - patient_search.py
    - CreateOrderReception.py (lines 168-214)
    """

    patient_selected = pyqtSignal(dict)  # Emits selected patient data

    def __init__(self, parent=None, db_connection=None, show_patient_id=False, show_partner_code=False):
        super().__init__(parent)
        self.db_connection = db_connection
        self.show_patient_id = show_patient_id
        self.show_partner_code = show_partner_code
        self.selected_patient = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_NORMAL)
        layout.setContentsMargins(
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL,
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL
        )

        # Search form
        form_layout = QHBoxLayout()

        # Last Name
        lname_label = QLabel("Last Name (Min chars: 3) and/or Phone")
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setMinimumWidth(250)
        form_layout.addWidget(lname_label)
        form_layout.addWidget(self.last_name_edit)

        # First Name
        fname_label = QLabel("First Name (Min chars: 2)")
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setMinimumWidth(200)
        form_layout.addWidget(fname_label)
        form_layout.addWidget(self.first_name_edit)

        # Date of Birth
        dob_label = QLabel("Date of Birth")
        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDate(QDate.currentDate())
        form_layout.addWidget(dob_label)
        form_layout.addWidget(self.dob_edit)

        form_layout.addStretch()
        layout.addLayout(form_layout)

        # Search Button
        button_layout = QHBoxLayout()
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        button_layout.addStretch()
        button_layout.addWidget(self.search_btn)
        layout.addLayout(button_layout)

        # Results Tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels([
            "First Name", "Last Name", "Street", "City",
            "State", "Phone", "DOB"
        ])
        self.results_tree.itemDoubleClicked.connect(self.on_result_selected)
        layout.addWidget(self.results_tree)

    def perform_search(self):
        """Search for patients based on criteria"""
        if not self.db_connection:
            return

        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        dob = self.dob_edit.date().toString("yyyy-MM-dd")

        # Build query
        query = "SELECT * FROM patientsinfo"
        conditions = []
        params = []

        if first_name and len(first_name) >= 2:
            conditions.append("first_name LIKE %s")
            params.append(f"{first_name}%")

        if last_name and len(last_name) >= 3:
            conditions.append("last_name LIKE %s")
            params.append(f"{last_name}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            try:
                self.db_connection.cursor.execute(query, tuple(params))
                patients = self.db_connection.cursor.fetchall()
                self.display_results(patients)
            except Exception as e:
                print(f"Search error: {e}")
        else:
            self.results_tree.clear()

    def display_results(self, patients):
        """Display search results in tree widget"""
        self.results_tree.clear()
        for patient in patients:
            item = QTreeWidgetItem([
                patient.get('first_name', ''),
                patient.get('last_name', ''),
                patient.get('address_1', ''),
                patient.get('city', ''),
                patient.get('state', ''),
                patient.get('phone', ''),
                str(patient.get('Dateofbirth', ''))
            ])
            item.setData(0, 256, patient)  # Store patient dict in item
            self.results_tree.addTopLevelItem(item)

    def on_result_selected(self, item, column):
        """Handle patient selection from results"""
        patient_data = item.data(0, 256)
        if patient_data:
            self.selected_patient = patient_data
            self.patient_selected.emit(patient_data)

    def get_selected_patient(self):
        """Get currently selected patient data"""
        return self.selected_patient

    def clear(self):
        """Clear search fields and results"""
        self.last_name_edit.clear()
        self.first_name_edit.clear()
        self.results_tree.clear()
        self.selected_patient = None
