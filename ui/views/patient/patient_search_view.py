from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from ui.components import PatientSearchWidget
from .patient_profile_view import PatientProfileView


class PatientSearchView(QWidget):
    """Patient search and profile launcher"""

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Patient search widget - double-click opens profile directly
        self.search_widget = PatientSearchWidget(
            db_connection=self.db_connection,
            parent=self
        )
        self.search_widget.patient_selected.connect(self.open_patient_profile)
        layout.addWidget(self.search_widget)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        new_patient_btn = QPushButton("New Patient")
        new_patient_btn.setProperty("cssClass", "success")
        new_patient_btn.clicked.connect(self.create_new_patient)
        button_layout.addWidget(new_patient_btn)

        layout.addLayout(button_layout)

    def open_patient_profile(self, patient_data):
        """Open patient profile directly on double-click"""
        if patient_data:
            profile = PatientProfileView(
                db_connection=self.db_connection,
                user_id=patient_data.get('user_id'),
                patient_data=patient_data
            )
            profile.exec()

    def create_new_patient(self):
        """Create new patient"""
        QMessageBox.information(self, "New Patient", "New patient creation not yet implemented")
