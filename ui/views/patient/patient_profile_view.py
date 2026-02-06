from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget
from .tabs.patient_info_tab import PatientInfoTab
from .tabs.allergies_tab import AllergiesTab
from .tabs.insurance_tab import InsuranceTab
from .tabs.prescriptions_tab import PrescriptionsTab
from .tabs.transactions_tab import TransactionsTab
from .tabs.genomics_tab import GenomicsTab
from .tabs.drug_review_tab import DrugReviewTab


class PatientProfileView(QDialog):
    """Main patient profile dialog"""

    def __init__(self, db_connection, user_id=None, patient_data=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.patient_data = patient_data or {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle(f"Patient Profile: {self.get_patient_name()}")
        self.setGeometry(50, 50, 1600, 900)
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()

        # Add all tabs
        self.tabs.addTab(PatientInfoTab(self.patient_data, self.db_connection), "1. Patient Info")
        self.tabs.addTab(AllergiesTab(self.db_connection, self.user_id), "2. Allergies")
        self.tabs.addTab(InsuranceTab(self.db_connection, self.user_id), "3. Insurance")
        self.tabs.addTab(PrescriptionsTab(self.db_connection, self.user_id), "4. Prescriptions")
        self.tabs.addTab(TransactionsTab(self.db_connection, self.user_id), "5. Transactions")
        self.tabs.addTab(GenomicsTab(self.db_connection, self.user_id), "6. Genomics")
        self.tabs.addTab(DrugReviewTab(self.db_connection, self.user_id), "7. Drug Review")

        layout.addWidget(self.tabs)

    def get_patient_name(self):
        """Get patient name from data"""
        first = self.patient_data.get('first_name', '')
        last = self.patient_data.get('last_name', '')
        return f"{first} {last}".strip() or "Unknown Patient"
