import sys
import sqlite3
from datetime import datetime, date
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton,
                            QComboBox, QTableWidget, QTableWidgetItem, QGroupBox,
                            QCheckBox, QDateEdit, QTimeEdit, QTextEdit, QHeaderView,
                            QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from DataBaseConnection import DatabaseConnection
from datetime import timedelta, datetime
from PrescriberSelectionView import PrescriberSelectionView
class CreateOrderWindow(QMainWindow):
    def __init__(self,db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.setWindowTitle("Create Order")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize attributes used in search and refill operations
        self.first_name = None
        self.last_name = None
        self.patient_id = None
        self.dob = None
        self.phone = None
        self.current_patient_id = None
        # Styling handled by global theme

        # Initialize database connection (you'll need to replace this with your MySQL connection)
        self.init_database()

        # Setup the main UI
        self.setup_ui()

        # Connect signals
        self.connect_signals()

    def init_database(self):
        """Database connection is already provided via __init__ parameter"""
        # Use the db_connection passed to __init__
        pass

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Top section with Refill Rx and Patient Search
        top_layout = QHBoxLayout()

        # Refill Rx section
        refill_group = self.create_refill_section()
        top_layout.addWidget(refill_group, 1)

        # Patient Search section
        patient_search_group = self.create_patient_search_section()
        top_layout.addWidget(patient_search_group, 2)

        main_layout.addLayout(top_layout)

        # Middle section with Patient Profile and Order Options
        middle_layout = QHBoxLayout()

        # Left side - Patient Profile and Prescriptions
        left_layout = QVBoxLayout()

        # Patient Profile
        patient_profile_group = self.create_patient_profile_section()
        left_layout.addWidget(patient_profile_group)

        # Prescription table
        prescription_group = self.create_prescription_table_section()
        left_layout.addWidget(prescription_group)

        middle_layout.addLayout(left_layout, 1)

        # Right side - Order Options
        order_options_group = self.create_order_options_section()
        middle_layout.addWidget(order_options_group, 1)

        main_layout.addLayout(middle_layout)

        # Bottom section - Order Summary
        order_summary_group = self.create_order_summary_section()
        main_layout.addWidget(order_summary_group)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.create_order_btn = QPushButton("Create Order")
        self.create_order_btn.setProperty("cssClass", "success")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("cssClass", "ghost")

        button_layout.addWidget(self.create_order_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def create_refill_section(self):
        group = QGroupBox("Refill Rx:")
        layout = QVBoxLayout(group)

        # Rx Number input
        rx_layout = QHBoxLayout()
        rx_layout.addWidget(QLabel("*Rx Number"))
        self.rx_number_edit = QLineEdit()
        rx_layout.addWidget(self.rx_number_edit)

        # Store Number
        rx_layout.addWidget(QLabel("Store Number"))
        self.store_number_edit = QLineEdit()
        rx_layout.addWidget(self.store_number_edit)

        layout.addLayout(rx_layout)

        # Add Refill Rx button
        self.add_refill_btn = QPushButton("Add Refill Rx")
        self.add_refill_btn.setProperty("cssClass", "primary")
        layout.addWidget(self.add_refill_btn)

        return group

    def create_patient_search_section(self):
        group = QGroupBox("Patient Search:")
        layout = QVBoxLayout(group)

        # Search fields
        search_layout = QGridLayout()

        # Patient ID
        search_layout.addWidget(QLabel("Patient ID"), 0, 0)
        self.patient_id_edit = QLineEdit()
        search_layout.addWidget(self.patient_id_edit, 0, 1)

        # Partner Code
        search_layout.addWidget(QLabel("Partner Code"), 0, 2)
        self.partner_code_edit = QLineEdit()
        search_layout.addWidget(self.partner_code_edit, 0, 3)

        # Last Name
        search_layout.addWidget(QLabel("Last Name (Min chars:3)"), 1, 0)
        self.last_name_edit = QLineEdit()
        search_layout.addWidget(self.last_name_edit, 1, 1)

        # Phone
        search_layout.addWidget(QLabel("and/or Phone"), 1, 2)
        self.phone_edit = QLineEdit()
        search_layout.addWidget(self.phone_edit, 1, 3)

        # First Name
        search_layout.addWidget(QLabel("First Name (Min chars:2)"), 2, 0)
        self.first_name_edit = QLineEdit()
        search_layout.addWidget(self.first_name_edit, 2, 1)

        # Date of Birth
        search_layout.addWidget(QLabel("Date of Birth"), 2, 2)
        self.dob_edit = QDateEdit()
        self.dob_edit.setDate(QDate.currentDate())
        self.dob_edit.setCalendarPopup(True)
        search_layout.addWidget(self.dob_edit, 2, 3)

        # OR label and Search button
        search_layout.addWidget(QLabel("or"), 1, 4)
        search_layout.addWidget(QLabel("and/or"), 2, 4)

        self.search_btn = QPushButton("Search")
        self.search_btn.setProperty("cssClass", "primary")
        search_layout.addWidget(self.search_btn, 1, 5)

        layout.addLayout(search_layout)

        return group

    def create_patient_profile_section(self):
        group = QGroupBox("Patient Profile")
        layout = QVBoxLayout(group)

        # Patient info
        info_layout = QGridLayout()

        info_layout.addWidget(QLabel("Patient [F5]:"), 0, 0)
        self.patient_display = QLineEdit()
        self.patient_display.setReadOnly(True)
        info_layout.addWidget(self.patient_display, 0, 1)

        info_layout.addWidget(QLabel("Contact Number [F4]:"), 1, 0)
        self.contact_number_display = QLineEdit()
        self.contact_number_display.setReadOnly(True)
        info_layout.addWidget(self.contact_number_display, 1, 1)

        layout.addLayout(info_layout)

        # Patient count and filter
        count_layout = QHBoxLayout()
        self.patient_count_label = QLabel("1 Patient")
        count_layout.addWidget(self.patient_count_label)

        count_layout.addWidget(QLabel("2 Other Account Members"))
        count_layout.addStretch()

        # Filter controls
        count_layout.addWidget(QLabel("Filter Status By:"))
        self.filter_status_combo = QComboBox()
        self.filter_status_combo.addItems(["Active & Profiled", "All", "Active Only", "Profiled Only"])
        count_layout.addWidget(self.filter_status_combo)

        layout.addLayout(count_layout)

        return group

    def create_prescription_table_section(self):
        group = QGroupBox("")
        layout = QVBoxLayout(group)

        # Product name display control
        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("Product Name Display:"))
        self.product_display_combo = QComboBox()
        self.product_display_combo.addItems(["Dispensed", "Generic", "Brand"])
        display_layout.addWidget(self.product_display_combo)

        # Previous/Next buttons
        display_layout.addStretch()
        self.prev_rx_btn = QPushButton("Previous Rxs")
        self.prev_rx_btn.setProperty("cssClass", "ghost")
        self.next_rx_btn = QPushButton("Next Rxs (0)")
        self.next_rx_btn.setProperty("cssClass", "ghost")
        display_layout.addWidget(self.prev_rx_btn)
        display_layout.addWidget(self.next_rx_btn)

        layout.addLayout(display_layout)

        # Prescription table
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(8)
        self.prescription_table.setHorizontalHeaderLabels([
            "Rx # - Store #", "Product Name", "RR", "Disp. Qty", "Last Fill", "Prescriber", "Status","Instructions"
        ])

        # Set column widths
        header = self.prescription_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.prescription_table)

        # Add buttons
        button_layout = QHBoxLayout()
        self.add_new_rx_btn = QPushButton("Add New Rx")
        self.add_new_rx_btn.setProperty("cssClass", "success")
        self.add_refill_rx_btn = QPushButton("Add Refill Rx")
        self.add_refill_rx_btn.setProperty("cssClass", "warning")

        self.add_new_rx_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button_layout.addWidget(self.add_new_rx_btn)
        button_layout.addWidget(self.add_refill_rx_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        return group

    def create_order_options_section(self):
        group = QGroupBox("Order Options")
        layout = QVBoxLayout(group)

        # Delivery
        delivery_layout = QHBoxLayout()
        delivery_layout.addWidget(QLabel("Delivery:"))
        self.delivery_combo = QComboBox()
        self.delivery_combo.addItems(["Ship", "Pick Up", "Delivery"])
        delivery_layout.addWidget(self.delivery_combo)

        self.shipping_options_btn = QPushButton("Shipping Options")
        self.shipping_options_btn.setProperty("cssClass", "ghost")
        delivery_layout.addWidget(self.shipping_options_btn)

        layout.addLayout(delivery_layout)

        # Promise Time
        promise_layout = QHBoxLayout()
        promise_layout.addWidget(QLabel("Promise Time:"))
        self.promise_date_edit = QDateEdit()
        self.promise_date_edit.setDate(QDate.currentDate())
        self.promise_date_edit.setCalendarPopup(True)
        promise_layout.addWidget(self.promise_date_edit)

        self.promise_time_edit = QTimeEdit()
        self.promise_time_edit.setTime(QTime(8, 25))
        promise_layout.addWidget(self.promise_time_edit)

        self.am_pm_combo = QComboBox()
        self.am_pm_combo.addItems(["AM", "PM"])
        promise_layout.addWidget(self.am_pm_combo)

        self.high_priority_cb = QCheckBox("High Priority")
        promise_layout.addWidget(self.high_priority_cb)

        layout.addLayout(promise_layout)

        # Delivery Date
        delivery_date_layout = QHBoxLayout()
        delivery_date_layout.addWidget(QLabel("*Delivery Date:"))
        self.delivery_date_edit = QDateEdit()
        self.delivery_date_edit.setDate(QDate.currentDate())
        self.delivery_date_edit.setCalendarPopup(True)
        delivery_date_layout.addWidget(self.delivery_date_edit)

        layout.addLayout(delivery_date_layout)

        # Fill Store
        fill_store_layout = QHBoxLayout()
        fill_store_layout.addWidget(QLabel("Fill Store:"))
        self.fill_store_edit = QLineEdit("03102")
        fill_store_layout.addWidget(self.fill_store_edit)

        layout.addLayout(fill_store_layout)

        # Payment Method
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("*Payment Method:"))
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["CHARGE TO ACCOUNT", "CASH", "CREDIT CARD", "INSURANCE"])
        payment_layout.addWidget(self.payment_method_combo)

        layout.addLayout(payment_layout)

        # Account details table
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(7)
        self.account_table.setHorizontalHeaderLabels([
            "Account Number", "Account Name", "Credit Limit", "Available Credit",
            "Account Balance", "Account Status", "Charge To"
        ])
        self.account_table.setMaximumHeight(100)

        layout.addWidget(self.account_table)

        return group

    def create_order_summary_section(self):
        group = QGroupBox("Order Summary (0)")
        layout = QVBoxLayout(group)

        # Order summary table
        self.order_summary_table = QTableWidget()
        self.order_summary_table.setColumnCount(4)
        self.order_summary_table.setHorizontalHeaderLabels([
            "Patient Name", "Product Name", "RR", "Disp. Qty"
        ])
        self.order_summary_table.setMaximumHeight(150)

        layout.addWidget(self.order_summary_table)

        # Remove item button
        remove_layout = QHBoxLayout()
        remove_layout.addStretch()
        self.remove_item_btn = QPushButton("Remove Item")
        self.remove_item_btn.setProperty("cssClass", "danger")
        remove_layout.addWidget(self.remove_item_btn)

        layout.addLayout(remove_layout)

        return group

    def connect_signals(self):
        """Connect all the signals to their respective slots"""
        self.search_btn.clicked.connect(self.search_patients)
        self.add_refill_btn.clicked.connect(self.add_refill_rx)
        self.add_new_rx_btn.clicked.connect(self.add_new_rx)
        self.create_order_btn.clicked.connect(self.create_order)
        self.add_refill_rx_btn.clicked.connect(self.add_refill_rx_by_row)
        self.cancel_btn.clicked.connect(self.close)
        self.prescription_table.itemDoubleClicked.connect(self.add_prescription_to_order)

        # Patient search triggers
    def add_refill_rx_by_row(self):
        current_row = self.prescription_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a prescription row first.")
            return
        print(current_row)
        med_name = self.prescription_table.item(current_row, 1).text()
        prescriber = self.prescription_table.item(current_row, 5).text()
        instructions = self.prescription_table.item(current_row, 7).text()

        try:
            query_pres_id = "SELECT prescription_id FROM Prescriptions WHERE user_id = %s AND medication_name = %s LIMIT 1"
            self.db_connection.cursor.execute(query_pres_id, (self.current_patient_id, med_name))
            pres_row = self.db_connection.cursor.fetchone()
            if not pres_row:
                raise Exception("Prescription ID not found.")

            query_ndc = "SELECT ndc FROM bottles WHERE medication_id = (SELECT id FROM medications WHERE name = %s) LIMIT 1"
            self.db_connection.cursor.execute(query_ndc, (med_name,))
            ndc_row = self.db_connection.cursor.fetchone()
            if not ndc_row:
                raise Exception("NDC not found for medication.")

            self.db_connection.cursor.execute("SELECT quantity FROM Prescriptions WHERE prescription_id = %s", (pres_row['prescription_id'],))
            qty_row = self.db_connection.cursor.fetchone()
            qty = qty_row['quantity'] if qty_row else None
            if not qty:
                raise Exception("Quantity not found for prescription.")
            self.db_connection.cursor.execute("SELECT first_name FROM patientsinfo WHERE user_id = %s", (self.current_patient_id,))
            patient_row = self.db_connection.cursor.fetchone()
            if not patient_row:
                raise Exception("Patient not found.")
            first_name = patient_row['first_name']
            insert_data = (
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "1618",
                first_name, self.last_name, med_name, qty, "Pick-up", "No",
                instructions, pres_row['prescription_id'], ndc_row['ndc'], "refill"
            )
            insert_query = """INSERT INTO {}(promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, instructions, prescription_id, ndc,refillornewrx)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.db_connection.cursor.execute(insert_query.format("ActivatedPrescriptions"), insert_data)
            self.db_connection.cursor.execute(insert_query.format("ProductSelectionQueue"), insert_data)
            self.db_connection.connection.commit()

            QMessageBox.information(self, "Success", f"Refill for {med_name} has been processed.")
        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to add refill: {e}")

    def auto_search(self):
        """Auto-search when minimum characters are entered"""
        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        phone = self.phone_edit.text().strip()

        if (len(last_name) >= 3 or len(first_name) >= 2 or len(phone) >= 3):
            self.search_patients()



    def search_patients(self):
        self.last_name = self.last_name_edit.text().strip()
        self.first_name = self.first_name_edit.text().strip()
        self.phone = self.phone_edit.text().strip()
        self.patient_id = self.patient_id_edit.text().strip()
        self.dob =  self.dob_edit.date().toString("yyyy-MM-dd")


        db_connection = self.db_connection

        query = "SELECT user_id, first_name, last_name, phone, Dateofbirth, address_1, city, state FROM patientsinfo"

        conditions = []
        params = []

        if self.patient_id:
            conditions.append("user_id = %s")
            params.append(self.patient_id)

        if self.first_name and len(self.first_name) >= 2:
            conditions.append("first_name LIKE %s")
            params.append(f"{self.first_name}%")

        if self.last_name and len(self.last_name) >= 3:
            conditions.append("last_name LIKE %s")
            params.append(f"{self.last_name}%")

        if self.phone:
            conditions.append("phone LIKE %s")
            params.append(f"%{self.phone}%")

        if self.dob:
            conditions.append("Dateofbirth = %s")
            params.append(self.dob)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        else:
            self.display_patients([])
            return

        try:
            db_connection.cursor.execute(query, tuple(params))
            patients = db_connection.cursor.fetchall()
            if patients:
                # Show first patient details and load prescriptions
                first_patient = patients[0]
                self.display_patient_info(first_patient)
                self.load_patient_prescriptions(first_patient['user_id'])
            else:
                self.clear_patient_info()
                QMessageBox.information(self, "Search Results", "No patients found matching the criteria.")

        except Exception as e:
            QMessageBox.critical(self, "Search Error", f"Error searching patients: {str(e)}")


    def display_patient_info(self, patient):
        """Display patient information in the patient profile section"""
        patient_first_name = patient['first_name']
        patient_last_name = patient['last_name']
        patient_dob = patient['Dateofbirth']
        self.current_patient_id = patient['user_id']
        self.patient_display.setText(f"{patient_first_name} {patient_last_name} - DOB: {patient_dob}")



        # Store current patient ID for prescription loading


    def clear_patient_info(self):
        """Clear patient information display"""
        self.patient_display.clear()
        self.contact_number_display.clear()
        self.prescription_table.setRowCount(0)
        self.current_patient_id = None

    def load_patient_prescriptions(self, patient_id):
        """Load prescriptions for the selected patient"""
        try:
            query = """
                SELECT p.rx_number, p.medication_name, p.refills, p.quantity, p.prescriber, p.instructions
                FROM Prescriptions p
                WHERE p.user_id = %s
                ORDER BY p.prescription_id DESC
            """
            db_connection = self.db_connection
            db_connection.cursor.execute(query, (patient_id,))
            prescriptions = db_connection.cursor.fetchall()

            self.prescription_table.setColumnCount(8)
            self.prescription_table.setHorizontalHeaderLabels([
                "Rx # - Store #", "Product Name", "RR", "Disp. Qty",
                "Last Fill", "Prescriber", "Status", "Instructions"
            ])
            self.prescription_table.setRowCount(len(prescriptions))

            for row, prescription in enumerate(prescriptions):
                rx_number = prescription['rx_number']
                med_name = prescription['medication_name']
                refills = prescription['refills']
                quantity = prescription['quantity']
                prescriber = prescription['prescriber']
                instructions = prescription.get('instructions', "No instructions")

                # Column 0: Rx # - Store #
                rx_store = f"{rx_number} - 03102"
                self.prescription_table.setItem(row, 0, QTableWidgetItem(str(rx_store)))

                # Column 1: Product Name
                self.prescription_table.setItem(row, 1, QTableWidgetItem(med_name))

                # Column 2: RR
                self.prescription_table.setItem(row, 2, QTableWidgetItem(str(refills)))

                # Column 3: Disp. Qty
                self.prescription_table.setItem(row, 3, QTableWidgetItem(str(quantity)))

                # Column 4: Last Fill (hardcoded placeholder)
                self.prescription_table.setItem(row, 4, QTableWidgetItem("01/15/2024"))

                # Column 5: Prescriber
                self.prescription_table.setItem(row, 5, QTableWidgetItem(prescriber))

                # Column 6: Status
                status = "Active" if refills > 0 else "No Refills"
                status_item = QTableWidgetItem(status)
                if refills == 0:
                    status_item.setBackground(QColor(255, 200, 200))
                self.prescription_table.setItem(row, 6, status_item)

                # Column 7: Instructions
                self.prescription_table.setItem(row, 7, QTableWidgetItem(instructions))

            # Connect refill button AFTER filling the table
            self.add_refill_rx_btn.clicked.connect(self.handle_add_refill_rx_click)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error loading prescriptions: {str(e)}")

    def handle_add_refill_rx_click(self):
        current_row = self.prescription_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No selection", "Please select a prescription row.")
            return

        med_item = self.prescription_table.item(current_row, 1)
        prescriber_item = self.prescription_table.item(current_row, 5)
        instructions_item = self.prescription_table.item(current_row, 7)

        if not med_item or not prescriber_item or not instructions_item:
            QMessageBox.warning(self, "Data Error", "Missing information in selected prescription.")
            return

        self.add_refill_rx_by_row()
    def add_prescription_to_order(self, item):
        """Add selected prescription to order summary"""
        row = item.row()

        # Get prescription data from the table
        patient_name = self.patient_display.text().split(" - ")[0] if self.patient_display.text() else ""
        product_name = self.prescription_table.item(row, 1).text()
        rr = self.prescription_table.item(row, 2).text()
        disp_qty = self.prescription_table.item(row, 3).text()

        # Add to order summary table
        current_rows = self.order_summary_table.rowCount()
        self.order_summary_table.setRowCount(current_rows + 1)

        self.order_summary_table.setItem(current_rows, 0, QTableWidgetItem(patient_name))
        self.order_summary_table.setItem(current_rows, 1, QTableWidgetItem(product_name))
        self.order_summary_table.setItem(current_rows, 2, QTableWidgetItem(rr))
        self.order_summary_table.setItem(current_rows, 3, QTableWidgetItem(disp_qty))

        # Update order summary count
        order_count = self.order_summary_table.rowCount()
        self.findChild(QGroupBox, "Order Summary (0)").setTitle(f"Order Summary ({order_count})")

    def add_refill_rx(self):
        """Add refill prescription functionality"""

        rx_number = self.rx_number_edit.text().strip()
        store_number = self.store_number_edit.text().strip()
        db_connection = self.db_connection

        db_connection.cursor.execute("""
            SELECT * FROM Prescriptions WHERE rx_number = %s
        """, (rx_number,))
        pres_row = db_connection.cursor.fetchone()
        med_name = pres_row['medication_name'] if pres_row else None
        instructions = pres_row['instructions'] if pres_row else "No instructions"
        current_patient_id = pres_row['user_id'] if pres_row else None
        db_connection.cursor.execute("""
            SELECT last_name, first_name FROM patientsinfo WHERE user_id = %s
        """, (current_patient_id,))
        name_row = db_connection.cursor.fetchone()
        last_name = name_row['last_name'] if name_row else "Unknown"
        first_name = name_row['first_name'] if name_row else "Unknown"


        try:
            query_ndc = "SELECT ndc FROM bottles WHERE medication_id = (SELECT id FROM medications WHERE name = %s) LIMIT 1"
            db_connection.cursor.execute(query_ndc, (med_name,))
            ndc_row = db_connection.cursor.fetchone()
            if not ndc_row:
                raise Exception("NDC not found for medication.")

            db_connection.cursor.execute(
                "SELECT quantity FROM Prescriptions WHERE prescription_id = %s",
                (pres_row['prescription_id'],)
            )
            qty_row = db_connection.cursor.fetchone()
            qty = qty_row['quantity'] if qty_row else None
            if not qty:
                raise Exception("Quantity not found for prescription.")

            db_connection.cursor.execute(
                "SELECT first_name FROM patientsinfo WHERE user_id = %s",
                (current_patient_id,)
            )
            patient_row = db_connection.cursor.fetchone()
            if not patient_row:
                raise Exception("Patient not found.")
            first_name = patient_row['first_name']

            insert_data = (
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "1618",
                first_name, last_name, med_name, qty, "Pick-up", "No",
                instructions, pres_row['prescription_id'], ndc_row['ndc'],"refill",current_patient_id
            )
            insert_query = """INSERT INTO {}(promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, instructions, prescription_id, ndc,refillornewrx,user_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            db_connection.cursor.execute(insert_query.format("ActivatedPrescriptions"), insert_data)
            db_connection.cursor.execute(insert_query.format("ProductSelectionQueue"), insert_data)
            db_connection.connection.commit()

            QMessageBox.information(self, "Success", f"Refill for {med_name} has been processed.")
        except Exception as e:
            db_connection.connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to add refill: {e}")



    def add_new_rx(self):
        self.prescriber_window = PrescriberSelectionView()  # keep a reference
        self.prescriber_window.show()
    def create_order(self):
        """Create the order with all selected items"""
        if self.order_summary_table.rowCount() == 0:
            QMessageBox.warning(self, "Order Error", "Please add items to the order before creating it.")
            return

        try:
            # Get order details
            delivery_method = self.delivery_combo.currentText()
            promise_date = self.promise_date_edit.date().toPython()
            promise_time = self.promise_time_edit.time().toPython()
            delivery_date = self.delivery_date_edit.date().toPython()
            payment_method = self.payment_method_combo.currentText()
            fill_store = self.fill_store_edit.text()
            high_priority = self.high_priority_cb.isChecked()

            # Here you would insert the order into your database
            # For demonstration, show success message
            order_id = 12345  # This would be generated by your database

            QMessageBox.information(self, "Order Created",
                                  f"Order #{order_id} has been created successfully!\n"
                                  f"Delivery: {delivery_method}\n"
                                  f"Promise Date: {promise_date}\n"
                                  f"Payment: {payment_method}")

            # Clear the form after successful order creation
            self.clear_order_form()

        except Exception as e:
            QMessageBox.critical(self, "Order Error", f"Error creating order: {str(e)}")

    def clear_order_form(self):
        """Clear the order form after successful submission"""
        self.order_summary_table.setRowCount(0)
        self.rx_number_edit.clear()
        self.store_number_edit.clear()
        self.clear_patient_info()

        # Reset dates to current
        self.promise_date_edit.setDate(QDate.currentDate())
        self.delivery_date_edit.setDate(QDate.currentDate())

        # Reset order summary title
        order_summary_group = self.findChild(QGroupBox)
        for child in self.findChildren(QGroupBox):
            if "Order Summary" in child.title():
                child.setTitle("Order Summary (0)")
                break

