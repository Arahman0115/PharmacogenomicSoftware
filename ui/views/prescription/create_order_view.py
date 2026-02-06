from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QRadioButton,
    QButtonGroup, QPushButton, QGroupBox, QFrame
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

        # New Prescription section (hidden by default)
        self.new_rx_section = NewPrescriptionSection(db_connection=self.db_connection)
        layout.addWidget(self.new_rx_section, 2)
        self.new_rx_section.hide()

        # Refill section (shown by default)
        self.refill_section = RefillSection(db_connection=self.db_connection)
        layout.addWidget(self.refill_section, 1)

        # Order options (shown for refill only)
        self.order_options = OrderOptionsSection()
        layout.addWidget(self.order_options, 1)
        self.order_options_group = QGroupBox()
        order_opt_layout = QVBoxLayout(self.order_options_group)
        order_opt_layout.addWidget(self.order_options)
        layout.addWidget(self.order_options_group, 1)

        # Order summary (shown for refill only)
        self.order_summary = OrderSummarySection()
        self.order_summary.order_submitted.connect(self.submit_refill_order)
        layout.addWidget(self.order_summary, 1)

        # Create Order button (refill mode)
        refill_btn_layout = QHBoxLayout()
        refill_btn_layout.addStretch()
        self.create_refill_order_btn = QPushButton("Create Refill Order")
        self.create_refill_order_btn.setProperty("cssClass", "success")
        self.create_refill_order_btn.clicked.connect(self.submit_refill_order)
        self.create_refill_order_btn.hide()
        refill_btn_layout.addWidget(self.create_refill_order_btn)
        self.refill_btn_frame = QFrame()
        self.refill_btn_frame.setLayout(refill_btn_layout)
        layout.addWidget(self.refill_btn_frame)

        # Create New Prescription button (new rx mode)
        new_rx_btn_layout = QHBoxLayout()
        new_rx_btn_layout.addStretch()
        self.create_new_rx_btn = QPushButton("Create New Prescription")
        self.create_new_rx_btn.setProperty("cssClass", "success")
        self.create_new_rx_btn.clicked.connect(self.create_new_prescription_order)
        new_rx_btn_layout.addWidget(self.create_new_rx_btn)
        self.new_rx_btn_frame = QFrame()
        self.new_rx_btn_frame.setLayout(new_rx_btn_layout)
        layout.addWidget(self.new_rx_btn_frame)
        self.new_rx_btn_frame.hide()

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

        # Show/hide sections
        self.new_rx_section.setVisible(is_new)
        self.new_rx_btn_frame.setVisible(is_new)
        self.refill_section.setVisible(not is_new)
        self.order_options_group.setVisible(not is_new)
        self.order_summary.setVisible(not is_new)
        self.refill_btn_frame.setVisible(not is_new)
        self.create_refill_order_btn.setVisible(not is_new)

        if is_new:
            self.new_rx_section.clear()

    def on_patient_selected(self, patient_data):
        """Handle patient selection"""
        self.selected_patient = patient_data
        if patient_data:
            user_id = patient_data.get('user_id')
            self.refill_section.load_refills(user_id)

    def create_new_prescription_order(self):
        """Create order for new prescription and move to data entry"""
        rx_data = self.new_rx_section.get_prescription_data()
        if not rx_data:
            return

        try:
            cursor = self.db_connection.cursor
            patient_id = rx_data['patient_id']

            # Get patient info
            cursor.execute("SELECT first_name, last_name FROM patientsinfo WHERE user_id = %s", (patient_id,))
            patient = cursor.fetchone()
            if not patient:
                raise Exception("Patient not found")

            # Get NDC from bottles table
            query_ndc = "SELECT ndc FROM bottles WHERE medication_id = %s LIMIT 1"
            cursor.execute(query_ndc, (rx_data['medication_id'],))
            ndc_row = cursor.fetchone()
            ndc = ndc_row['ndc'] if ndc_row else "000000000"

            # Get current date/time for promise
            promise_datetime = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

            # Prepare insert data
            insert_data = (
                promise_datetime,
                "03102",  # rx_store_num (default fill store)
                patient['first_name'],
                patient['last_name'],
                rx_data['medication_name'],
                rx_data['quantity'],
                "Pick-up",  # default delivery
                "No",  # printed
                rx_data['instructions'],
                None,  # prescription_id (null for new rx)
                ndc,
                "new",  # refillornewrx
                patient_id
            )

            # Insert into both ProductSelectionQueue (reception) and ActivatedPrescriptions (workflow)
            insert_query_psq = """INSERT INTO ProductSelectionQueue
                (promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, instructions, prescription_id, ndc, refillornewrx, user_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')"""

            insert_query_ap = """INSERT INTO ActivatedPrescriptions
                (promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, instructions, prescription_id, ndc, refillornewrx, user_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'data_entry_pending')"""

            cursor.execute(insert_query_psq, insert_data)
            cursor.execute(insert_query_ap, insert_data)
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
