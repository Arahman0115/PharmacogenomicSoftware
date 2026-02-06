from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QDialog, QListWidget, QListWidgetItem, QMessageBox,
    QFileDialog, QDoubleSpinBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor


class NewPrescriptionSection(QWidget):
    """New prescription entry section with medication and prescriber selection"""

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

        # Patient info display (read-only - set by CreateOrderView)
        patient_info_layout = QGridLayout()
        patient_info_layout.addWidget(QLabel("Patient:"), 0, 0)
        self.patient_display = QLineEdit()
        self.patient_display.setReadOnly(True)
        patient_info_layout.addWidget(self.patient_display, 0, 1)

        patient_info_layout.addWidget(QLabel("Phone:"), 1, 0)
        self.patient_phone_display = QLineEdit()
        self.patient_phone_display.setReadOnly(True)
        patient_info_layout.addWidget(self.patient_phone_display, 1, 1)

        patient_info_layout.addWidget(QLabel("Address:"), 2, 0)
        self.patient_address_display = QLineEdit()
        self.patient_address_display.setReadOnly(True)
        patient_info_layout.addWidget(self.patient_address_display, 2, 1)

        patient_info_layout.addWidget(QLabel("DOB:"), 3, 0)
        self.patient_dob_display = QLineEdit()
        self.patient_dob_display.setReadOnly(True)
        patient_info_layout.addWidget(self.patient_dob_display, 3, 1)

        group_layout.addLayout(patient_info_layout)

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

    def set_patient(self, patient_data):
        """Set patient data (called by CreateOrderView)"""
        if patient_data:
            self.selected_patient_id = patient_data.get('user_id')
            self.patient_display.setText(
                f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
            )
            self.patient_phone_display.setText(patient_data.get('phone', ''))
            self.patient_address_display.setText(patient_data.get('address_1', ''))
            self.patient_dob_display.setText(str(patient_data.get('Dateofbirth', '')))
        else:
            self.clear_patient()

    def clear_patient(self):
        """Clear patient info"""
        self.selected_patient_id = None
        self.patient_display.clear()
        self.patient_phone_display.clear()
        self.patient_address_display.clear()
        self.patient_dob_display.clear()

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
        self.clear_patient()
        self.rx_image_path_edit.clear()
        self.medication_edit.clear()
        self.quantity_spin.setValue(30)
        self.instructions_edit.clear()
        self.prescriber_edit.clear()
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
    """Dialog to search and select a medication with inventory display"""
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.selected_medication_id = None
        self.selected_medication_name = None
        self.setWindowTitle("Search Medication")
        self.setGeometry(100, 100, 800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search field with live search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Medication Name (live search):"))
        self.medication_edit = QLineEdit()
        self.medication_edit.setPlaceholderText("Start typing to search...")
        self.medication_edit.textChanged.connect(self.perform_search)  # Live search
        search_layout.addWidget(self.medication_edit)
        layout.addLayout(search_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Medication Name", "Bottles Available", "Medication ID", ""])

        # Set column widths
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.results_table.itemDoubleClicked.connect(self.select_medication)
        self.results_table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.results_table)

        # Info label
        self.info_label = QLabel("Enter at least 2 characters to search")
        layout.addWidget(self.info_label)

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
        """Live search for medications"""
        med_name = self.medication_edit.text().strip()

        self.results_table.setRowCount(0)

        if len(med_name) < 2:
            self.info_label.setText("Enter at least 2 characters to search")
            return

        try:
            # Search medications with inventory count
            query = """
                SELECT DISTINCT m.medication_id, m.medication_name, COUNT(b.bottle_id) as bottles_available
                FROM medications m
                LEFT JOIN bottles b ON m.medication_id = b.medication_id AND b.status = 'in_stock'
                WHERE m.medication_name LIKE %s
                GROUP BY m.medication_id, m.medication_name
                ORDER BY m.medication_name ASC
                LIMIT 50
            """
            self.db_connection.cursor.execute(query, (f"%{med_name}%",))
            results = self.db_connection.cursor.fetchall()

            if not results:
                self.info_label.setText(f"No medications found matching '{med_name}'")
                return

            self.info_label.setText(f"Found {len(results)} medication(s)")

            for med in results:
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)

                # Medication name
                name_item = QTableWidgetItem(med['medication_name'])
                self.results_table.setItem(row, 0, name_item)

                # Inventory count with color coding
                stock = med['bottles_available'] if med['bottles_available'] else 0
                stock_item = QTableWidgetItem(f"{stock} available")
                if stock == 0:
                    stock_item.setBackground(QColor(200, 100, 100))  # Red for out of stock
                elif stock < 5:
                    stock_item.setBackground(QColor(220, 180, 60))   # Yellow for low stock
                else:
                    stock_item.setBackground(QColor(100, 180, 100))  # Green for in stock
                self.results_table.setItem(row, 1, stock_item)

                # Medication ID
                id_item = QTableWidgetItem(str(med['medication_id']))
                self.results_table.setItem(row, 2, id_item)

                # Store full medication data
                self.results_table.item(row, 0).setData(256, med)

        except Exception as e:
            self.info_label.setText(f"Search error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")

    def on_row_selected(self):
        """Handle row selection"""
        pass

    def select_medication(self):
        """Select highlighted medication"""
        current_row = self.results_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a medication.")
            return

        med = self.results_table.item(current_row, 0).data(256)
        if not med:
            QMessageBox.warning(self, "Selection Error", "Please select a medication.")
            return

        self.selected_medication_id = med['medication_id']
        self.selected_medication_name = med['medication_name']
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
