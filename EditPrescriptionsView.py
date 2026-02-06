from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLineEdit, QMessageBox, QGridLayout, QTextEdit,
    QComboBox, QDateEdit, QSpinBox, QCheckBox, QGroupBox, QTabWidget,
    QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QPixmap, QFont
from datetime import datetime, timedelta
import json
import base64
from DataBaseConnection import DatabaseConnection


class EditPrescriptionView(QWidget):
    # Add custom signal
    prescription_processed = pyqtSignal()

    def __init__(self, entry, parent=None):
        super().__init__(parent)

        # Create our own database connection
        self.db = DatabaseConnection(
            host='localhost',
            user='pgx_user',
            password="pgx_password",
            database='pgx_db'
        )

        self.entry = entry
        self.puid = entry.get('user_id', None)  # Get user_id from entry
        self.selected_bottles = []
        self.patient_data = {}
        self.prescriber_data = {}
        self.prescription_data = {}

        self.setWindowTitle(f"Data Entry Detail - {entry['first_name']} {entry['last_name']}")
        self.setMinimumSize(1200, 800)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)

        # Create splitter for main areas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left side - Main form
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Top section - Patient and Prescriber info
        top_section = self.create_top_section()
        left_layout.addWidget(top_section)

        # Middle section - Prescription details
        middle_section = self.create_prescription_section()
        left_layout.addWidget(middle_section)

        # Bottom section - Bottle selection and controls
        bottom_section = self.create_bottle_section()
        left_layout.addWidget(bottom_section)

        # Action buttons
        button_layout = self.create_action_buttons()
        left_layout.addLayout(button_layout)

        splitter.addWidget(left_widget)

        # Right side - Prescription image and additional info
        right_widget = self.create_right_section()
        splitter.addWidget(right_widget)

        # Set splitter proportions (70% left, 30% right)
        splitter.setSizes([840, 360])

    def create_top_section(self):
        """Create the top section with patient and prescriber information"""
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)

        # Patient Information Group
        patient_group = QGroupBox("Patient Info")
        patient_layout = QGridLayout(patient_group)

        # Patient fields
        self.patient_name_label = QLabel()
        self.patient_address_edit = QLineEdit()
        self.patient_city_edit = QLineEdit()
        self.patient_state_edit = QLineEdit()
        self.patient_phone_edit = QLineEdit()
        self.patient_dob_edit = QDateEdit()
        self.patient_dob_edit.setCalendarPopup(True)

        patient_layout.addWidget(QLabel("Patient:"), 0, 0)
        patient_layout.addWidget(self.patient_name_label, 0, 1)
        patient_layout.addWidget(QLabel("Address:"), 1, 0)
        patient_layout.addWidget(self.patient_address_edit, 1, 1)
        patient_layout.addWidget(QLabel("City:"), 2, 0)
        patient_layout.addWidget(self.patient_city_edit, 2, 1)
        patient_layout.addWidget(QLabel("State:"), 3, 0)
        patient_layout.addWidget(self.patient_state_edit, 3, 1)
        patient_layout.addWidget(QLabel("Phone:"), 4, 0)
        patient_layout.addWidget(self.patient_phone_edit, 4, 1)
        patient_layout.addWidget(QLabel("DOB:"), 5, 0)
        patient_layout.addWidget(self.patient_dob_edit, 5, 1)

        # Prescriber Information Group
        prescriber_group = QGroupBox("Prescriber Info")
        prescriber_layout = QGridLayout(prescriber_group)

        self.prescriber_name_edit = QLineEdit()
        self.prescriber_address_edit = QTextEdit()
        self.prescriber_address_edit.setMaximumHeight(60)
        self.prescriber_phone_edit = QLineEdit()
        self.prescriber_dea_edit = QLineEdit()

        prescriber_layout.addWidget(QLabel("Prescriber:"), 0, 0)
        prescriber_layout.addWidget(self.prescriber_name_edit, 0, 1)
        prescriber_layout.addWidget(QLabel("Address:"), 1, 0)
        prescriber_layout.addWidget(self.prescriber_address_edit, 1, 1)
        prescriber_layout.addWidget(QLabel("Phone:"), 2, 0)
        prescriber_layout.addWidget(self.prescriber_phone_edit, 2, 1)
        prescriber_layout.addWidget(QLabel("DEA:"), 3, 0)
        prescriber_layout.addWidget(self.prescriber_dea_edit, 3, 1)

        top_layout.addWidget(patient_group)
        top_layout.addWidget(prescriber_group)

        return top_widget
    def reselect_product(self):
        """Handle reselecting the product"""
        # Logic to reselect product goes here
        QMessageBox.information(self, "Re-select Product", "Product re-selection logic not implemented yet.")

    def create_prescription_section(self):

        """Create the prescription details section"""
        rx_group = QGroupBox("Prescription Details")
        rx_layout = QGridLayout(rx_group)

        # Product Information
        self.product_label = QLabel()
        self.product_label.setProperty("cssClass", "highlight-label")

        self.reselect_product_btn = QPushButton("Re-select Product")
        self.reselect_product_btn.setProperty("cssClass", "warning")
        self.reselect_product_btn.clicked.connect(self.reselect_product)
        db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="pgx_password", database='pgx_db')


        db_connection.cursor.execute("""
        SELECT refillornewrx FROM ProductSelectionQueue WHERE user_id = %s
    """, (self.puid,))
        refill_or_new = db_connection.cursor.fetchone()
        refillornew = refill_or_new['refillornewrx'] if refill_or_new else "None"
        if refillornew == "refill":
            # if its of status refill, disable the reselct product button
            self.reselect_product_btn.setEnabled(False)
        else:
            self.reselect_product_btn.setEnabled(True)


        self.ndc_edit = QLineEdit()
        self.manufacturer_edit = QLineEdit()
        self.dosage_form_edit = QLineEdit()
        self.strength_edit = QLineEdit()

        # Prescription Details
        self.written_date_edit = QDateEdit()
        self.written_date_edit.setCalendarPopup(True)
        self.written_date_edit.setDate(QDate.currentDate())

        self.expiration_date_edit = QDateEdit()
        self.expiration_date_edit.setCalendarPopup(True)
        self.expiration_date_edit.setDate(QDate.currentDate().addYears(1))

        self.written_qty_spin = QSpinBox()
        self.written_qty_spin.setRange(1, 9999)

        self.dispense_qty_spin = QSpinBox()
        self.dispense_qty_spin.setRange(1, 9999)

        self.refills_spin = QSpinBox()
        self.refills_spin.setRange(0, 99)

        self.refills_remaining_spin = QSpinBox()
        self.refills_remaining_spin.setRange(0, 99)

        self.dose_edit = QLineEdit()
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Times Per Week", "Daily", "BID", "TID", "QID", "As Needed"])

        self.days_supply_spin = QSpinBox()
        self.days_supply_spin.setRange(1, 365)
        self.days_supply_spin.setValue(30)

        self.therapy_days_spin = QSpinBox()
        self.therapy_days_spin.setRange(1, 365)

        # Sig/Instructions
        self.instructions_edit = QTextEdit()
        self.instructions_edit.setMaximumHeight(80)
        self.quantity_edit = QTextEdit()
        self.quantity_edit.setMaximumHeight(80)

        # Layout arrangement
        rx_layout.addWidget(QLabel("Product:"), 0, 0)
        rx_layout.addWidget(self.product_label, 0, 1, 1, 3)
        rx_layout.addWidget(self.reselect_product_btn, 0, 4)

        rx_layout.addWidget(QLabel("NDC:"), 1, 0)
        rx_layout.addWidget(self.ndc_edit, 1, 1)
        rx_layout.addWidget(QLabel("Manufacturer:"), 1, 2)
        rx_layout.addWidget(self.manufacturer_edit, 1, 3)

        rx_layout.addWidget(QLabel("Dosage Form:"), 2, 0)
        rx_layout.addWidget(self.dosage_form_edit, 2, 1)
        rx_layout.addWidget(QLabel("Strength:"), 2, 2)
        rx_layout.addWidget(self.strength_edit, 2, 3)

        rx_layout.addWidget(QLabel("Written Date:"), 3, 0)
        rx_layout.addWidget(self.written_date_edit, 3, 1)
        rx_layout.addWidget(QLabel("Expiration Date:"), 3, 2)
        rx_layout.addWidget(self.expiration_date_edit, 3, 3)

        rx_layout.addWidget(QLabel("Written Qty:"), 4, 0)
        rx_layout.addWidget(self.written_qty_spin, 4, 1)
        rx_layout.addWidget(QLabel("Dispense Qty:"), 4, 2)
        rx_layout.addWidget(self.dispense_qty_spin, 4, 3)

        rx_layout.addWidget(QLabel("Refills Allowed:"), 5, 0)
        rx_layout.addWidget(self.refills_spin, 5, 1)
        rx_layout.addWidget(QLabel("Refills Remaining:"), 5, 2)
        rx_layout.addWidget(self.refills_remaining_spin, 5, 3)

        rx_layout.addWidget(QLabel("Dose:"), 6, 0)
        rx_layout.addWidget(self.dose_edit, 6, 1)
        rx_layout.addWidget(QLabel("Frequency:"), 6, 2)
        rx_layout.addWidget(self.frequency_combo, 6, 3)

        rx_layout.addWidget(QLabel("Days Supply:"), 7, 0)
        rx_layout.addWidget(self.days_supply_spin, 7, 1)
        rx_layout.addWidget(QLabel("Therapy Days:"), 7, 2)
        rx_layout.addWidget(self.therapy_days_spin, 7, 3)

        rx_layout.addWidget(QLabel("Sig/Instructions:"), 8, 0)
        rx_layout.addWidget(self.instructions_edit, 8, 1, 1, 3)

        rx_layout.addWidget(QLabel("Quantity:"), 9, 0)
        rx_layout.addWidget(self.quantity_edit, 9, 1, 1, 3)

        return rx_group

    def create_bottle_section(self):
        """Create the bottle selection section"""
        bottle_group = QGroupBox("Available Inventory")
        bottle_layout = QVBoxLayout(bottle_group)

        # Bottle tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)
        self.tree.setHeaderLabels([
            "Bottle ID", "Type", "Quantity", "Expiration",
            "Days Until Expiry", "NDC", "Status"
        ])
        self.tree.setMaximumHeight(200)
        bottle_layout.addWidget(self.tree)

        # Additional options
        options_layout = QHBoxLayout()

        self.third_party_combo = QComboBox()
        self.third_party_combo.addItems(["Cash", "Insurance", "Medicare", "Medicaid"])

        self.daw_combo = QComboBox()
        self.daw_combo.addItems([
            "0 - No Product Selection Indicated",
            "1 - Substitution Not Allowed by Prescriber",
            "2 - Substitution Allowed - Patient Requested",
            "3 - Substitution Allowed - Pharmacist Selected",
            "4 - Substitution Allowed - Generic Not in Stock",
            "5 - Substitution Allowed - Brand Dispensed as Generic"
        ])

        self.origin_code_combo = QComboBox()
        self.origin_code_combo.addItems(["0 - Not Specified", "1 - Written", "2 - Telephone", "3 - Electronic"])

        self.eligible_340b_check = QCheckBox("Eligible for 340B")

        options_layout.addWidget(QLabel("Third Party:"))
        options_layout.addWidget(self.third_party_combo)
        options_layout.addWidget(QLabel("DAW Code:"))
        options_layout.addWidget(self.daw_combo)
        options_layout.addWidget(QLabel("Origin Code:"))
        options_layout.addWidget(self.origin_code_combo)
        options_layout.addWidget(self.eligible_340b_check)
        options_layout.addStretch()

        bottle_layout.addLayout(options_layout)

        return bottle_group

    def create_right_section(self):
        """Create the right section with prescription image and additional info"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Prescription image section
        image_group = QGroupBox("Prescription Image")
        image_layout = QVBoxLayout(image_group)

        self.prescription_image_label = QLabel("No Image Available")
        self.prescription_image_label.setMinimumHeight(300)
        self.prescription_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.prescription_image_label)

        right_layout.addWidget(image_group)

        # Additional information
        info_group = QGroupBox("Additional Information")
        info_layout = QGridLayout(info_group)

        self.rx_number_edit = QLineEdit()
        self.store_number_edit = QLineEdit()
        self.store_number_edit.setText("1618")  # Default store number

        self.promise_time_edit = QDateEdit()
        self.promise_time_edit.setCalendarPopup(True)
        self.promise_time_edit.setDate(QDate.currentDate().addDays(1))

        self.delivery_combo = QComboBox()
        self.delivery_combo.addItems(["Pick-up", "Delivery", "Mail Order"])

        info_layout.addWidget(QLabel("Rx Number:"), 0, 0)
        info_layout.addWidget(self.rx_number_edit, 0, 1)
        info_layout.addWidget(QLabel("Store Number:"), 1, 0)
        info_layout.addWidget(self.store_number_edit, 1, 1)
        info_layout.addWidget(QLabel("Promise Time:"), 2, 0)
        info_layout.addWidget(self.promise_time_edit, 2, 1)
        info_layout.addWidget(QLabel("Delivery:"), 3, 0)
        info_layout.addWidget(self.delivery_combo, 3, 1)

        right_layout.addWidget(info_group)
        right_layout.addStretch()

        return right_widget

    def create_action_buttons(self):
        """Create action buttons at the bottom"""
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel Item")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.cancel_item)

        order_details_btn = QPushButton("Order Details")
        order_details_btn.setProperty("cssClass", "ghost")
        order_details_btn.clicked.connect(self.show_order_details)

        dup_detail_btn = QPushButton("DUP Detail")
        dup_detail_btn.setProperty("cssClass", "ghost")
        dup_detail_btn.clicked.connect(self.show_dup_detail)

        view_pricing_btn = QPushButton("View Pricing")
        view_pricing_btn.setProperty("cssClass", "ghost")
        view_pricing_btn.clicked.connect(self.view_pricing)

        rx_options_btn = QPushButton("Rx Options")
        rx_options_btn.setProperty("cssClass", "ghost")
        rx_options_btn.clicked.connect(self.show_rx_options)

        vaccination_btn = QPushButton("Vaccination")
        vaccination_btn.setProperty("cssClass", "ghost")
        vaccination_btn.clicked.connect(self.handle_vaccination)

        next_btn = QPushButton("Next")
        next_btn.setProperty("cssClass", "primary")
        next_btn.clicked.connect(self.handle_continue)

        decline_btn = QPushButton("Decline")
        decline_btn.setProperty("cssClass", "danger")
        decline_btn.clicked.connect(self.decline_prescription)

        cancel_btn_2 = QPushButton("Cancel")
        cancel_btn_2.setProperty("cssClass", "ghost")
        cancel_btn_2.clicked.connect(self.close)

        save_btn = QPushButton("Save")
        save_btn.setProperty("cssClass", "success")
        save_btn.clicked.connect(self.save_changes)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(order_details_btn)
        button_layout.addWidget(dup_detail_btn)
        button_layout.addWidget(view_pricing_btn)
        button_layout.addWidget(rx_options_btn)
        button_layout.addWidget(vaccination_btn)
        button_layout.addStretch()
        button_layout.addWidget(next_btn)
        button_layout.addWidget(decline_btn)
        button_layout.addWidget(cancel_btn_2)
        button_layout.addWidget(save_btn)

        return button_layout

    def load_data(self):
        """Load all prescription, patient, and prescriber data"""
        try:
            # Load prescription data from Prescriptions table
            if 'prescription_id' in self.entry and self.entry['prescription_id']:
                self.db.cursor.execute("""
                    SELECT p.*, pi.*, pr.*,p.quantity
                    FROM Prescriptions p
                    LEFT JOIN patientsinfo pi ON p.user_id = pi.user_id
                    LEFT JOIN Prescribers pr ON p.prescriber = pr.name
                    WHERE p.prescription_id = %s
                """, (self.entry['prescription_id'],))

                prescription_data = self.db.cursor.fetchone()
                if prescription_data:
                    self.populate_prescription_data(prescription_data)

            # Load medication details
            self.load_medication_details()

            # Load available bottles
            self.load_bottles()

            # Load prescription image
            self.load_prescription_image()

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Data", str(e))

    def populate_prescription_data(self, data):
        """Populate form fields with prescription data"""
        # Patient information
        if data.get('first_name'):
            self.patient_name_label.setText(f"{data['first_name']} {data.get('last_name', '')}")
        if data.get('user_id'):
            self.patient_user_id = data['user_id']
        if data.get('address_1'):
            self.patient_address_edit.setText(data['address_1'])
        if data.get('city'):
            self.patient_city_edit.setText(data['city'])
        if data.get('state'):
            self.patient_state_edit.setText(data['state'])
        if data.get('phone'):
            self.patient_phone_edit.setText(data['phone'])
        if data.get('Dateofbirth'):
            self.patient_dob_edit.setDate(QDate.fromString(str(data['Dateofbirth']), "yyyy-MM-dd"))

        # Prescriber information
        if data.get('prescriber'):
            self.prescriber_name_edit.setText(data['prescriber'])
        if data.get('address'):
            self.prescriber_address_edit.setText(data['address'])
        if data.get('phone'):
            self.prescriber_phone_edit.setText(data['phone'])
        if data.get('dea_number'):
            self.prescriber_dea_edit.setText(data['dea_number'])

        # Prescription details
        if data.get('rx_number'):
            self.rx_number_edit.setText(str(data['rx_number']))
        if data.get('refills'):
            self.refills_spin.setValue(data['refills'])
            self.refills_remaining_spin.setValue(data['refills'])
        if data.get('instructions'):
            self.instructions_edit.setText(data['instructions'])
        if data.get('quantity'):
            self.quantity_edit.setText(str(data['quantity']))

        # Set dispense quantity from entry
        if 'quantity' in self.entry:
            self.dispense_qty_spin.setValue(self.entry['quantity'])
            self.written_qty_spin.setValue(self.entry['quantity'])

    def load_medication_details(self):
        """Load medication details from database"""
        try:
            med_name = self.entry["product"]
            self.product_label.setText(med_name)

            self.db.cursor.execute("SELECT * FROM medications WHERE name = %s", (med_name,))
            med_data = self.db.cursor.fetchone()

            if med_data:
                if med_data.get('ndc'):
                    self.ndc_edit.setText(med_data['ndc'])
                if med_data.get('manufacturer'):
                    self.manufacturer_edit.setText(med_data['manufacturer'])
                if med_data.get('dosage_form'):
                    self.dosage_form_edit.setText(med_data['dosage_form'])
                if med_data.get('strength'):
                    self.strength_edit.setText(med_data['strength'])

        except Exception as e:
            print(f"Error loading medication details: {e}")

    def load_bottles(self):
        """Load available bottles for the medication"""
        self.tree.clear()
        med_name = self.entry["product"]
        try:
            self.db.cursor.execute("SELECT id FROM medications WHERE name = %s", (med_name,))
            row = self.db.cursor.fetchone()
            if not row:
                return
            med_id = row['id']

            self.db.cursor.execute(
                "SELECT id, bottle_type, quantity, expiration, ndc, status FROM bottles WHERE medication_id = %s",
                (med_id,)
            )
            bottles = self.db.cursor.fetchall()
            now = datetime.now().date()

            for b in bottles:
                days_until_expiry = (b['expiration'] - now).days if b['expiration'] else -1

                # Color code based on expiration
                item = QTreeWidgetItem([
                    str(b['id']),
                    b['bottle_type'].capitalize(),
                    str(b['quantity']),
                    b['expiration'].strftime("%Y-%m-%d") if b['expiration'] else "N/A",
                    str(days_until_expiry),
                    str(b['ndc']) if b['ndc'] else "N/A",
                    b['status'].capitalize()
                ])

                # Set background color based on expiration
                if days_until_expiry <= 30 and days_until_expiry >= 0:
                    for col in range(7):
                        item.setBackground(col, Qt.GlobalColor.yellow)
                elif days_until_expiry < 0:
                    for col in range(7):
                        item.setBackground(col, Qt.GlobalColor.red)

                self.tree.addTopLevelItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_prescription_image(self):
        """Load and display prescription image if available"""
        try:
            if 'prescription_id' in self.entry and self.entry['prescription_id']:
                self.db.cursor.execute(
                    "SELECT prescription_image FROM Prescriptions WHERE prescription_id = %s",
                    (self.entry['prescription_id'],)
                )
                result = self.db.cursor.fetchone()

                if result and result['prescription_image']:
                    # Convert blob to pixmap and display
                    pixmap = QPixmap()
                    if pixmap.loadFromData(result['prescription_image']):
                        scaled_pixmap = pixmap.scaled(
                            self.prescription_image_label.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.prescription_image_label.setPixmap(scaled_pixmap)
                    else:
                        self.prescription_image_label.setText("Invalid Image Format")
                else:
                    self.prescription_image_label.setText("No Image Available")
        except Exception as e:
            print(f"Error loading prescription image: {e}")
            self.prescription_image_label.setText("Error Loading Image")
    def handle_continue(self):
        """Handle the continue/next button - move to drug review queue"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Select", "Select at least one bottle.")
            return

        dispense_qty = self.dispense_qty_spin.value()
        selected_bottles = []

        for item in selected_items:
            bottle_id = int(item.text(0))
            bottle_type = item.text(1).lower()
            qty = int(item.text(2))
            expiration = item.text(3)
            status = item.text(6).lower()
            selected_bottles.append({
                "id": bottle_id,
                "type": bottle_type,
                "quantity": qty,
                "expiration": expiration
            })

        try:
            bottles_json = json.dumps(selected_bottles)
            promise_time = self.promise_time_edit.dateTime().toString('yyyy-MM-dd hh:mm:ss')
            rx_store_num = self.store_number_edit.text()
            delivery = self.delivery_combo.currentText()
            printed = "No"

            self.db.cursor.execute(
                """INSERT INTO drugreviewqueue
                (promise_time, rx_store_num, first_name, last_name, product, quantity,
                delivery, printed, selected_bottles, product_selection_queue_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    promise_time, rx_store_num,
                    self.entry['first_name'],
                    self.entry['last_name'],
                    self.entry['product'], dispense_qty,
                    delivery, printed, bottles_json,
                    self.entry['id'], "Drug Review"
                )
            )

            if 'prescription_id' in self.entry and self.entry['prescription_id']:
                self.db.cursor.execute(
                    "UPDATE ActivatedPrescriptions SET status = %s WHERE prescription_id = %s",
                    ("Drug Review", self.entry['prescription_id'])
                )

            for bottle in selected_bottles:
                self.db.cursor.execute(
                    "SELECT quantity FROM bottles WHERE id = %s AND bottle_type = %s",
                    (bottle["id"], bottle["type"].capitalize())
                )
                current_qty = self.db.cursor.fetchone()['quantity']
                remaining = current_qty - dispense_qty


                self.db.cursor.execute(
                    "UPDATE bottles SET quantity = %s, status = %s WHERE id = %s",
                    (remaining, "dispensed", bottle["id"])
                )

                today = datetime.now().date()

                if bottle['type'] == "stock":
                    self.db.cursor.execute("SELECT status FROM bottles WHERE id = %s", (bottle['id'],))
                    source = self.db.cursor.fetchone()['status']
                    self.db.cursor.execute(
                        "SELECT expiration FROM bottles WHERE id = %s",
                        (bottle['id'],)
                    )
                    stock_row = self.db.cursor.fetchone()
                    if stock_row and stock_row['expiration']:
                        stock_exp = stock_row['expiration']
                        if stock_exp <= today + timedelta(days=365):
                            expiration_date = stock_exp
                        else:
                            expiration_date = today + timedelta(days=365)
                    else:
                        expiration_date = today + timedelta(days=365)

                elif bottle['type'] == "amber":
                    expiration_date = datetime.strptime(bottle['expiration'], "%Y-%m-%d").date()

                else:
                    raise Exception(f"Unknown bottle type: {bottle['type']}")

            print(f"Inserting into inusebottles: queue_id={self.entry['id']}, bottle_id={bottle['id']}, type={bottle['type'].capitalize()}, qty={dispense_qty}, exp={expiration_date}")

            self.db.cursor.execute(
                """INSERT INTO inusebottles
                (product_selection_queue_id, bottle_id, bottle_type, quantity, expiration, source)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    self.entry['id'],
                    bottle['id'],
                    bottle['type'].capitalize(),
                    dispense_qty,
                    expiration_date,
                    source
                )
            )

            # Add this to check if the insert worked
            print(f"Rows affected: {self.db.cursor.rowcount}")

            self.db.cursor.execute(
                "UPDATE ProductSelectionQueue SET instructions = %s, refills = %s WHERE id = %s",
                (self.instructions_edit.toPlainText(), self.refills_spin.value(), self.entry['id'])
            )

            self.db.cursor.execute("DELETE FROM ProductSelectionQueue WHERE id = %s", (self.entry['id'],))

            self.db.connection.commit()
            self.prescription_processed.emit()
            QMessageBox.information(self, "Success", "Prescription pushed to Drug Review Queue.")
            self.close()

        except Exception as e:
            self.db.connection.rollback()
            QMessageBox.critical(self, "Error", str(e))


    def save_changes(self):
        """Save changes without processing"""
        try:
            # Update ProductSelectionQueue with current form values
            self.db.cursor.execute(
                """UPDATE ProductSelectionQueue
                SET instructions = %s, refills = %s, quantity = %s
                WHERE id = %s""",
                (
                    self.instructions_edit.toPlainText(),
                    self.refills_spin.value(),
                    self.dispense_qty_spin.value(),
                    self.entry['id']
                )
            )

            self.db.connection.commit()
            QMessageBox.information(self, "Success", "Changes saved successfully.")

        except Exception as e:
            self.db.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")

    def cancel_item(self):
        """Cancel the current item"""
        reply = QMessageBox.question(
            self, "Cancel Item",
            "Are you sure you want to cancel this prescription?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute(
                    "UPDATE ProductSelectionQueue SET status = %s WHERE id = %s",
                    ("Cancelled", self.entry['id'])
                )
                self.db.connection.commit()
                QMessageBox.information(self, "Success", "Prescription cancelled.")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def decline_prescription(self):
        """Decline the prescription"""
        reply = QMessageBox.question(
            self, "Decline Prescription",
            "Are you sure you want to decline this prescription?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.cursor.execute(
                    "UPDATE ProductSelectionQueue SET status = %s WHERE id = %s",
                    ("Declined", self.entry['id'])
                )
                self.db.connection.commit()
                QMessageBox.information(self, "Success", "Prescription declined.")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # Placeholder methods for additional functionality
    def show_order_details(self):
        """Show order details dialog"""
        QMessageBox.information(self, "Order Details", "Order details functionality not implemented yet.")

    def show_dup_detail(self):
        """Show DUP (Drug Utilization Program) details"""
        QMessageBox.information(self, "DUP Detail", "DUP detail functionality not implemented yet.")

    def view_pricing(self):
        """View pricing information"""
        QMessageBox.information(self, "View Pricing", "Pricing view functionality not implemented yet.")

    def show_rx_options(self):
        """Show prescription options"""
        QMessageBox.information(self, "Rx Options", "Rx options functionality not implemented yet.")

    def handle_vaccination(self):
        """Handle vaccination-related functionality"""
        QMessageBox.information(self, "Vaccination", "Vaccination functionality not implemented yet.")

    def closeEvent(self, event):
        """Handle window close event"""

        event.accept()