from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox,
    QFileDialog, QDoubleSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class NewPrescriptionSection(QWidget):
    """New prescription entry section with patient, medication, and prescriber selection"""

    prescription_ready = pyqtSignal(dict)  # Emits prescription data when ready

    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection
        self.selected_patient_id = None
        self.selected_medication_id = None
        self.selected_prescriber_id = None
        self.selected_medication_name = None
        self.rx_image_path = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("New Prescription")
        group_layout = QVBoxLayout(group)

        # Patient selection
        patient_layout = QHBoxLayout()
        patient_layout.addWidget(QLabel("Patient:"))
        self.patient_edit = QLineEdit()
        self.patient_edit.setReadOnly(True)
        patient_layout.addWidget(self.patient_edit)
        self.patient_search_btn = QPushButton("Search Patient")
        self.patient_search_btn.setProperty("cssClass", "primary")
        self.patient_search_btn.clicked.connect(self.search_patient)
        patient_layout.addWidget(self.patient_search_btn)
        group_layout.addLayout(patient_layout)

        # Rx Image
        image_layout = QHBoxLayout()
        image_layout.addWidget(QLabel("Rx Image:"))
        self.rx_image_path_edit = QLineEdit()
        self.rx_image_path_edit.setReadOnly(True)
        image_layout.addWidget(self.rx_image_path_edit)
        self.scan_btn = QPushButton("Scan Rx")
        self.scan_btn.setProperty("cssClass", "primary")
        self.scan_btn.clicked.connect(self.scan_rx_image)
        image_layout.addWidget(self.scan_btn)
        group_layout.addLayout(image_layout)

        # Medication selection
        med_layout = QHBoxLayout()
        med_layout.addWidget(QLabel("Medication:"))
        self.medication_edit = QLineEdit()
        self.medication_edit.setReadOnly(True)
        med_layout.addWidget(self.medication_edit)
        self.medication_search_btn = QPushButton("Search Medication")
        self.medication_search_btn.setProperty("cssClass", "primary")
        self.medication_search_btn.clicked.connect(self.search_medications)
        med_layout.addWidget(self.medication_search_btn)
        group_layout.addLayout(med_layout)

        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.quantity_spin.setValue(30)
        qty_layout.addWidget(self.quantity_spin)
        qty_layout.addStretch()
        group_layout.addLayout(qty_layout)

        # Instructions
        instr_layout = QHBoxLayout()
        instr_layout.addWidget(QLabel("Instructions:"))
        self.instructions_edit = QLineEdit()
        self.instructions_edit.setPlaceholderText("e.g., Take 1 tablet daily")
        instr_layout.addWidget(self.instructions_edit)
        group_layout.addLayout(instr_layout)

        # Prescriber selection
        prescriber_layout = QHBoxLayout()
        prescriber_layout.addWidget(QLabel("Prescriber:"))
        self.prescriber_edit = QLineEdit()
        self.prescriber_edit.setReadOnly(True)
        prescriber_layout.addWidget(self.prescriber_edit)
        self.prescriber_search_btn = QPushButton("Select Prescriber")
        self.prescriber_search_btn.setProperty("cssClass", "primary")
        self.prescriber_search_btn.clicked.connect(self.search_prescribers)
        prescriber_layout.addWidget(self.prescriber_search_btn)
        group_layout.addLayout(prescriber_layout)

        layout.addWidget(group)
        layout.addStretch()

    def search_patient(self):
        """Open patient search dialog"""
        dialog = PatientSearchDialog(self.db_connection, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_patient_id = dialog.selected_patient_id
            patient_name = dialog.selected_patient_name
            self.patient_edit.setText(patient_name)

    def scan_rx_image(self):
        """Select an Rx image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Prescription Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        if file_path:
            self.rx_image_path = file_path
            self.rx_image_path_edit.setText(file_path.split('/')[-1])

    def search_medications(self):
        """Open medication search dialog"""
        if not self.selected_patient_id:
            QMessageBox.warning(self, "Patient Required", "Please select a patient first.")
            return

        dialog = MedicationSearchDialog(self.db_connection, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_medication_id = dialog.selected_medication_id
            self.selected_medication_name = dialog.selected_medication_name
            self.medication_edit.setText(self.selected_medication_name)

    def search_prescribers(self):
        """Open prescriber search dialog"""
        dialog = PrescriberSearchDialog(self.db_connection, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_prescriber_id = dialog.selected_prescriber_id
            prescriber_name = dialog.selected_prescriber_name
            self.prescriber_edit.setText(prescriber_name)

    def get_prescription_data(self):
        """Validate and return prescription data"""
        if not self.selected_patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return None
        if not self.selected_medication_id:
            QMessageBox.warning(self, "Validation Error", "Please select a medication.")
            return None
        if self.quantity_spin.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid quantity.")
            return None
        if not self.selected_prescriber_id:
            QMessageBox.warning(self, "Validation Error", "Please select a prescriber.")
            return None

        return {
            'patient_id': self.selected_patient_id,
            'medication_id': self.selected_medication_id,
            'medication_name': self.selected_medication_name,
            'quantity': int(self.quantity_spin.value()),
            'instructions': self.instructions_edit.text(),
            'prescriber_id': self.selected_prescriber_id,
            'rx_image_path': self.rx_image_path
        }

    def clear(self):
        """Clear all fields"""
        self.patient_edit.clear()
        self.rx_image_path_edit.clear()
        self.medication_edit.clear()
        self.quantity_spin.setValue(30)
        self.instructions_edit.clear()
        self.prescriber_edit.clear()
        self.selected_patient_id = None
        self.selected_medication_id = None
        self.selected_prescriber_id = None
        self.rx_image_path = None


# ============================================================================
# SEARCH DIALOGS
# ============================================================================

class PatientSearchDialog(QDialog):
    """Dialog to search and select a patient"""
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.selected_patient_id = None
        self.selected_patient_name = None
        self.setWindowTitle("Search Patient")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search fields
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Last Name:"))
        self.last_name_edit = QLineEdit()
        search_layout.addWidget(self.last_name_edit)

        search_layout.addWidget(QLabel("First Name:"))
        self.first_name_edit = QLineEdit()
        search_layout.addWidget(self.first_name_edit)

        search_btn = QPushButton("Search")
        search_btn.setProperty("cssClass", "primary")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.select_patient)
        layout.addWidget(self.results_list)

        # Buttons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.setProperty("cssClass", "success")
        select_btn.clicked.connect(self.select_patient)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def perform_search(self):
        """Search for patients"""
        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()

        if not last_name and not first_name:
            QMessageBox.warning(self, "Input Error", "Please enter at least one search criteria.")
            return

        try:
            query = "SELECT user_id, first_name, last_name FROM patientsinfo WHERE 1=1"
            params = []

            if last_name:
                query += " AND last_name LIKE %s"
                params.append(f"{last_name}%")
            if first_name:
                query += " AND first_name LIKE %s"
                params.append(f"{first_name}%")

            self.db_connection.cursor.execute(query, params)
            results = self.db_connection.cursor.fetchall()

            self.results_list.clear()
            for patient in results:
                item_text = f"{patient['first_name']} {patient['last_name']} (ID: {patient['user_id']})"
                item = QListWidgetItem(item_text)
                item.setData(256, patient)
                self.results_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def select_patient(self):
        """Select highlighted patient"""
        item = self.results_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a patient.")
            return

        patient = item.data(256)
        self.selected_patient_id = patient['user_id']
        self.selected_patient_name = f"{patient['first_name']} {patient['last_name']}"
        self.accept()


class MedicationSearchDialog(QDialog):
    """Dialog to search and select a medication"""
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.selected_medication_id = None
        self.selected_medication_name = None
        self.setWindowTitle("Search Medication")
        self.setGeometry(100, 100, 700, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search field
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Medication Name:"))
        self.medication_edit = QLineEdit()
        search_layout.addWidget(self.medication_edit)

        search_btn = QPushButton("Search")
        search_btn.setProperty("cssClass", "primary")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.select_medication)
        layout.addWidget(self.results_list)

        # Buttons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.setProperty("cssClass", "success")
        select_btn.clicked.connect(self.select_medication)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def perform_search(self):
        """Search for medications in inventory"""
        med_name = self.medication_edit.text().strip()

        if not med_name:
            QMessageBox.warning(self, "Input Error", "Please enter a medication name.")
            return

        try:
            # Search medications that are in stock
            query = """
                SELECT DISTINCT m.id, m.name, COUNT(b.bottle_id) as bottles_available
                FROM medications m
                LEFT JOIN bottles b ON m.id = b.medication_id AND b.status = 'in_stock'
                WHERE m.name LIKE %s
                GROUP BY m.id, m.name
            """
            self.db_connection.cursor.execute(query, (f"%{med_name}%",))
            results = self.db_connection.cursor.fetchall()

            self.results_list.clear()
            for med in results:
                stock = med['bottles_available'] if med['bottles_available'] else 0
                item_text = f"{med['name']} ({stock} bottles available)"
                item = QListWidgetItem(item_text)
                item.setData(256, med)
                self.results_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def select_medication(self):
        """Select highlighted medication"""
        item = self.results_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a medication.")
            return

        med = item.data(256)
        self.selected_medication_id = med['id']
        self.selected_medication_name = med['name']
        self.accept()


class PrescriberSearchDialog(QDialog):
    """Dialog to search and select a prescriber"""
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.selected_prescriber_id = None
        self.selected_prescriber_name = None
        self.setWindowTitle("Search Prescriber")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search fields
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Prescriber Name:"))
        self.prescriber_edit = QLineEdit()
        search_layout.addWidget(self.prescriber_edit)

        search_btn = QPushButton("Search")
        search_btn.setProperty("cssClass", "primary")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.select_prescriber)
        layout.addWidget(self.results_list)

        # Buttons
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Select")
        select_btn.setProperty("cssClass", "success")
        select_btn.clicked.connect(self.select_prescriber)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def perform_search(self):
        """Search for prescribers"""
        prescriber_name = self.prescriber_edit.text().strip()

        if not prescriber_name:
            QMessageBox.warning(self, "Input Error", "Please enter a prescriber name.")
            return

        try:
            query = """
                SELECT prescriber_id, prescriber_name, npi
                FROM Prescribers
                WHERE prescriber_name LIKE %s
            """
            self.db_connection.cursor.execute(query, (f"%{prescriber_name}%",))
            results = self.db_connection.cursor.fetchall()

            self.results_list.clear()
            for prescriber in results:
                npi = prescriber['npi'] if prescriber['npi'] else "N/A"
                item_text = f"{prescriber['prescriber_name']} (NPI: {npi})"
                item = QListWidgetItem(item_text)
                item.setData(256, prescriber)
                self.results_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def select_prescriber(self):
        """Select highlighted prescriber"""
        item = self.results_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a prescriber.")
            return

        prescriber = item.data(256)
        self.selected_prescriber_id = prescriber['prescriber_id']
        self.selected_prescriber_name = prescriber['prescriber_name']
        self.accept()
