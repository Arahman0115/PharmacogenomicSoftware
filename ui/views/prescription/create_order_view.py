from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QRadioButton,
    QButtonGroup, QPushButton, QGroupBox, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt
from ui.components import PatientSearchWidget, PrescriptionTable
from .components.refill_section import RefillSection
from .components.new_prescription_section import NewPrescriptionSection
from .components.order_options_section import OrderOptionsSection
from .components.order_summary_section import OrderSummarySection
from datetime import datetime, timedelta


class CreateOrderView(QMainWindow):
    """Order creation dialog with refill and new prescription modes"""

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.selected_patient = None
        self.setWindowTitle("Create New Rx Order")
        self.setGeometry(50, 50, 1400, 900)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Prescription type selection (New vs Refill)
        type_group = self.create_prescription_type_section()
        layout.addWidget(type_group)

        # Patient search (used in both modes)
        self.patient_search = PatientSearchWidget(db_connection=self.db_connection)
        self.patient_search.patient_selected.connect(self.on_patient_selected)
        layout.addWidget(self.patient_search, 1)

        # Stacked widget to hold the two modes
        self.stacked_modes = QStackedWidget()

        # === Page 0: Refill Mode ===
        refill_page = QWidget()
        refill_layout = QVBoxLayout(refill_page)

        self.refill_section = RefillSection(db_connection=self.db_connection)
        refill_layout.addWidget(self.refill_section, 1)

        self.order_options = OrderOptionsSection()
        self.order_options_group = QGroupBox()
        order_opt_layout = QVBoxLayout(self.order_options_group)
        order_opt_layout.addWidget(self.order_options)
        refill_layout.addWidget(self.order_options_group, 1)

        self.order_summary = OrderSummarySection()
        self.order_summary.order_submitted.connect(self.submit_refill_order)
        refill_layout.addWidget(self.order_summary, 1)

        # Create Order button (refill mode)
        refill_btn_layout = QHBoxLayout()
        refill_btn_layout.addStretch()
        self.create_refill_order_btn = QPushButton("Create Refill Order")
        self.create_refill_order_btn.setProperty("cssClass", "success")
        self.create_refill_order_btn.clicked.connect(self.submit_refill_order)
        refill_btn_layout.addWidget(self.create_refill_order_btn)
        self.refill_btn_frame = QFrame()
        self.refill_btn_frame.setLayout(refill_btn_layout)
        refill_layout.addWidget(self.refill_btn_frame)

        refill_layout.addStretch()
        self.stacked_modes.addWidget(refill_page)

        # === Page 1: New Prescription Mode ===
        new_rx_page = QWidget()
        new_rx_layout = QVBoxLayout(new_rx_page)

        self.new_rx_section = NewPrescriptionSection(db_connection=self.db_connection)
        new_rx_layout.addWidget(self.new_rx_section, 2)

        # Create New Prescription button (new rx mode)
        new_rx_btn_layout = QHBoxLayout()
        new_rx_btn_layout.addStretch()
        self.create_new_rx_btn = QPushButton("Create New Prescription")
        self.create_new_rx_btn.setProperty("cssClass", "success")
        self.create_new_rx_btn.clicked.connect(self.create_new_prescription_order)
        new_rx_btn_layout.addWidget(self.create_new_rx_btn)
        self.new_rx_btn_frame = QFrame()
        self.new_rx_btn_frame.setLayout(new_rx_btn_layout)
        new_rx_layout.addWidget(self.new_rx_btn_frame)

        new_rx_layout.addStretch()
        self.stacked_modes.addWidget(new_rx_page)

        # Add stacked widget to main layout
        layout.addWidget(self.stacked_modes, 2)

        self.setCentralWidget(central_widget)

    def create_prescription_type_section(self):
        """Create radio button selection for New Prescription vs Refill"""
        group = QGroupBox("Prescription Type")
        layout = QHBoxLayout(group)

        self.rx_type_group = QButtonGroup()

        self.new_rx_radio = QRadioButton("New Prescription")
        self.new_rx_radio.setChecked(False)
        self.new_rx_radio.toggled.connect(self.toggle_prescription_type)
        self.rx_type_group.addButton(self.new_rx_radio, 0)
        layout.addWidget(self.new_rx_radio)

        self.refill_radio = QRadioButton("Refill")
        self.refill_radio.setChecked(True)
        self.refill_radio.toggled.connect(self.toggle_prescription_type)
        self.rx_type_group.addButton(self.refill_radio, 1)
        layout.addWidget(self.refill_radio)

        layout.addStretch()
        return group

    def toggle_prescription_type(self):
        """Toggle between New Prescription and Refill modes"""
        is_new = self.new_rx_radio.isChecked()

        # Switch stacked widget pages (0=Refill, 1=New Rx)
        self.stacked_modes.setCurrentIndex(1 if is_new else 0)

        if is_new:
            self.new_rx_section.clear()

    def on_patient_selected(self, patient_data):
        """Handle patient selection"""
        self.selected_patient = patient_data
        if patient_data:
            user_id = patient_data.get('user_id')
            # Load refills for refill mode
            self.refill_section.load_refills(user_id)
            # Set patient for new prescription mode
            self.new_rx_section.set_patient(patient_data)

    def create_new_prescription_order(self):
        """Create order for new prescription and move to data entry"""
        rx_data = self.new_rx_section.get_prescription_data()
        if not rx_data:
            return

        try:
            cursor = self.db_connection.cursor
            patient_id = rx_data['patient_id']
            medication_id = rx_data['medication_id']

            # Get patient info
            cursor.execute("SELECT first_name, last_name FROM patientsinfo WHERE user_id = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient:
                raise Exception("Patient not found")

            # Get current date/time for promise
            promise_datetime = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare data for ProductSelectionQueue (reception intake)
            psq_data = (
                patient_id,
                patient['first_name'],
                patient['last_name'],
                rx_data['medication_name'],
                rx_data['quantity'],
                rx_data['instructions'],
                "Pick-up",  # default delivery
                promise_datetime,
                "03102",  # rx_store_num (default fill store)
                "pending",
                rx_data['refills']  # refills from prescription
            )

            # Prepare data for ActivatedPrescriptions (workflow tracking)
            ap_data = (
                patient_id,
                medication_id,
                rx_data['prescriber_id'],
                rx_data['quantity'],
                patient['first_name'],
                patient['last_name'],
                "03102",  # rx_store_num
                "03102",  # store_number
                "data_entry_pending",  # initial status
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # fill_date
            )

            # Insert into ProductSelectionQueue (reception intake)
            insert_query_psq = """INSERT INTO ProductSelectionQueue
                (user_id, first_name, last_name, product, quantity, instructions, delivery, promise_time, rx_store_num, status, refills)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            # Insert into ActivatedPrescriptions (workflow tracking)
            insert_query_ap = """INSERT INTO ActivatedPrescriptions
                (user_id, medication_id, prescriber_id, quantity_dispensed, first_name, last_name, rx_store_num, store_number, status, fill_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            cursor.execute(insert_query_psq, psq_data)
            cursor.execute(insert_query_ap, ap_data)

            # Get the prescription_id just inserted and generate rx_number
            prescription_id = cursor.lastrowid
            rx_number = f"RX{str(prescription_id).zfill(6)}"

            # Update with rx_number
            cursor.execute(
                "UPDATE ActivatedPrescriptions SET rx_number = %s WHERE prescription_id = %s",
                (rx_number, prescription_id)
            )

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"New prescription for {patient['first_name']} {patient['last_name']} has been created.\n"
                f"It will now appear in the Data Entry queue for pharmacist review."
            )

            self.new_rx_section.clear()
            self.refill_radio.setChecked(True)

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to create prescription: {str(e)}")

    def submit_refill_order(self, order_data):
        """Submit the refill order to database"""
        if not self.selected_patient:
            QMessageBox.warning(self, "Error", "Please select a patient first")
            return

        try:
            user_id = self.selected_patient.get('user_id')
            options = self.order_options.get_options()

            # Insert into ProductSelectionQueue
            for item in order_data['items']:
                insert_query = """
                    INSERT INTO ProductSelectionQueue
                    (user_id, product, quantity, instructions, delivery, promise_time, status, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())
                """
                self.db_connection.cursor.execute(
                    insert_query,
                    (
                        user_id,
                        item['medication'],
                        item['quantity'],
                        item['instructions'],
                        options['delivery_type'],
                        options['promise_date']
                    )
                )

            self.db_connection.connection.commit()
            QMessageBox.information(self, "Success", f"Order created with {order_data['total']} items")
            self.order_summary.clear_order()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create order: {e}")
            self.db_connection.connection.rollback()
