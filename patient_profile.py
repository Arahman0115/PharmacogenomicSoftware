import sys
from datetime import datetime, timedelta
import requests
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import random

# Assume these modules exist and are correctly implemented
from DataBaseConnection import DatabaseConnection
from PrescriptionDetailView import PrescriptionDetailView

class PatientProfileSystem(QMainWindow):
    def __init__(self,db_connection):
        super().__init__()
        # Styling handled by global theme
        self.db_connection = db_connection
        self.profile_window = None

    def show_patient_profile(self, result, la_name, fi_name, dob):
        self.result = result
        self.l_name = la_name
        self.f_name = fi_name
        self.selected_user_id = self.get_user_id(la_name, fi_name)

        self.profile_window = QDialog(self)
        self.profile_window.setWindowTitle(f"Patient Profile: {fi_name} {la_name}")
        self.profile_window.setGeometry(50, 50, 1600, 900)
        self.notebook = QTabWidget()

        # Create and add tabs
        self.notebook.addTab(self.create_patient_info_tab(fi_name, la_name, dob), "1. Patient Info")
        self.notebook.addTab(self.create_allergies_tab(), "2. Allergies")
        self.notebook.addTab(self.create_insurance_tab(), "3. Insurance")
        self.notebook.addTab(self.create_prescriptions_tab(), "4. Prescriptions")
        self.notebook.addTab(self.create_transactions_tab(), "5. Transactions")
        self.notebook.addTab(self.create_genomics_tab(), "6. Genomics")
        self.notebook.addTab(self.create_drug_review_tab(), "7. Drug Review")

        layout = QVBoxLayout()
        layout.addWidget(self.notebook)
        self.profile_window.setLayout(layout)
        self.profile_window.exec()

    def create_patient_info_tab(self, fi_name, la_name, dob):
        tab = QWidget()
        
        layout = QGridLayout()
        layout.setSpacing(20)

        info_group = QGroupBox("Patient Details")
        info_layout = QFormLayout()
        info_layout.addRow("First Name:", QLineEdit(fi_name))
        info_layout.addRow("Last Name:", QLineEdit(la_name))
        dob_entry = QDateEdit(calendarPopup=True)
        try:
            dob_date = datetime.strptime(str(dob), '%Y-%m-%d').date()
            dob_entry.setDate(QDate(dob_date.year, dob_date.month, dob_date.day))
        except (ValueError, TypeError):
            pass # Keep default date if parsing fails
        info_layout.addRow("Date of Birth:", dob_entry)
        info_group.setLayout(info_layout)

        contact_group = QGroupBox("Contact Information")
        contact_layout = QFormLayout()
        contact_layout.addRow("Phone Number:", QLineEdit("(123) 456-7890"))
        contact_layout.addRow("Email Address:", QLineEdit(f"{fi_name.lower()}.{la_name.lower()}@email.com"))
        contact_group.setLayout(contact_layout)

        layout.addWidget(info_group, 0, 0)
        layout.addWidget(contact_group, 0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(2, 1)
        tab.setLayout(layout)
        return tab

    def create_allergies_tab(self):
        tab = QWidget(); 
        layout = QVBoxLayout(); layout.setSpacing(20)
        group = QGroupBox("Known Allergies"); layout_group = QVBoxLayout()
        table = QTableWidget(3, 3)
        table.setHorizontalHeaderLabels(["Allergen", "Reaction", "Severity"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dummy_data = [("Penicillin", "Hives", "Severe"), ("Aspirin", "Rash", "Moderate"), ("Sulfa Drugs", "Anaphylaxis", "Severe")]
        for r, (d1, d2, d3) in enumerate(dummy_data):
            table.setItem(r, 0, QTableWidgetItem(d1)); table.setItem(r, 1, QTableWidgetItem(d2)); table.setItem(r, 2, QTableWidgetItem(d3))
        layout_group.addWidget(table); group.setLayout(layout_group)
        layout.addWidget(group); layout.addStretch(); tab.setLayout(layout)
        return tab

    def create_insurance_tab(self):
        tab = QWidget(); 
        layout = QVBoxLayout(); layout.setSpacing(20)
        group = QGroupBox("Insurance Details"); layout_group = QFormLayout()
        layout_group.addRow("Provider:", QLineEdit("Blue Cross Blue Shield"))
        layout_group.addRow("Policy Number:", QLineEdit("X123456789"))
        layout_group.addRow("Group Number:", QLineEdit("G98765"))
        group.setLayout(layout_group); layout.addWidget(group)
        layout.addStretch(); tab.setLayout(layout)
        return tab

    def create_transactions_tab(self):
        tab = QWidget(); 
        layout = QVBoxLayout(); layout.setSpacing(20)
        group = QGroupBox("Transaction History"); layout_group = QVBoxLayout()
        table = QTableWidget(3, 4)
        table.setHorizontalHeaderLabels(["Date", "Item", "Amount", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dummy_data = [("2025-06-20", "Lisinopril 10mg", "$10.00", "Paid"), ("2025-05-15", "Metformin 500mg", "$15.50", "Paid"), ("2025-04-18", "Atorvastatin 20mg", "$25.00", "Paid")]
        for r, (d1, d2, d3, d4) in enumerate(dummy_data):
            table.setItem(r, 0, QTableWidgetItem(d1)); table.setItem(r, 1, QTableWidgetItem(d2)); table.setItem(r, 2, QTableWidgetItem(d3)); table.setItem(r, 3, QTableWidgetItem(d4))
        layout_group.addWidget(table); group.setLayout(layout_group)
        layout.addWidget(group); layout.addStretch(); tab.setLayout(layout)
        return tab

    def create_prescriptions_tab(self):
        tab = QWidget(); 
        layout = QHBoxLayout(); layout.setSpacing(20)

        # Left side: Prescriptions List
        prescriptions_group = QGroupBox("Patient Prescriptions"); pres_layout = QVBoxLayout()
        self.tree_prescriptions = QTreeWidget()
        self.tree_prescriptions.setHeaderLabels(["Medication", "Refills", "Prescriber", "Instructions", "Quantity","Action"])
        self.tree_prescriptions.setColumnWidth(4, 100)
        pres_layout.addWidget(self.tree_prescriptions)
        prescriptions_group.setLayout(pres_layout)

        # Right side: Form
        form_group = QGroupBox("Add/Edit Prescription"); form_layout = QFormLayout()
        self.pres_med_name_input = QLineEdit()
        self.pres_refills_input = QSpinBox()
        self.pres_prescriber_input = QLineEdit()
        self.pres_instructions_input = QLineEdit()
        self.pres_quantity_input = QSpinBox()
        form_layout.addRow("Medication Name:", self.pres_med_name_input)
        form_layout.addRow("Refills:", self.pres_refills_input)
        form_layout.addRow("Prescriber:", self.pres_prescriber_input)
        form_layout.addRow("Instructions:", self.pres_instructions_input)
        form_layout.addRow("Quantity:", self.pres_quantity_input)
        add_button = QPushButton("Add Prescription"); add_button.setProperty("cssClass", "success"); add_button.clicked.connect(self.add_prescription)
        form_layout.addWidget(add_button)
        form_group.setLayout(form_layout)

        layout.addWidget(prescriptions_group, 3); layout.addWidget(form_group, 1)
        tab.setLayout(layout)

        self.tree_prescriptions.itemDoubleClicked.connect(self.on_prescription_select)
        self.load_prescriptions()
        return tab

    def create_genomics_tab(self):
        tab = QWidget(); 
        layout = QHBoxLayout(); layout.setSpacing(20)

        # Left Side: Genomics List
        genomics_group = QGroupBox("Genetic Information"); gen_layout = QVBoxLayout()
        self.tree_genetic_variant = QTreeWidget()
        self.tree_genetic_variant.setHeaderLabels(["Gene", "Genetic Variant", "Disease", "Genotype"])
        self.tree_genetic_variant.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        gen_layout.addWidget(self.tree_genetic_variant)
        genomics_group.setLayout(gen_layout)

        # Right Side: Form
        form_group = QGroupBox("Add Genetic Data"); form_layout = QFormLayout()
        self.genetic_entries = {}
        labels = ["Gene", "Genetic Variant", "Disease", "Genotype"]
        for label_text in labels:
            entry = QLineEdit()
            form_layout.addRow(f"{label_text}:", entry)
            self.genetic_entries[label_text.lower().replace(' ', '_')] = entry

        add_button = QPushButton("Add Information"); add_button.setProperty("cssClass", "success"); add_button.clicked.connect(self.save_genetic_info)
        delete_button = QPushButton("Delete Selected"); delete_button.setProperty("cssClass", "danger"); delete_button.clicked.connect(self.delete_genetic_entry)
        btn_layout = QHBoxLayout(); btn_layout.addWidget(add_button); btn_layout.addWidget(delete_button)
        form_layout.addRow(btn_layout)
        form_group.setLayout(form_layout)

        layout.addWidget(genomics_group, 3); layout.addWidget(form_group, 1)
        tab.setLayout(layout)

        self.load_genetic_data()
        return tab

    def create_drug_review_tab(self):
        tab = QWidget(); 
        layout = QVBoxLayout(); layout.setSpacing(20)
        review_group = QGroupBox("Drug-Gene Interaction Review"); review_layout = QVBoxLayout()
        self.tree_geneticinfo_variant = QTreeWidget()
        self.tree_geneticinfo_variant.setHeaderLabels(["Drug/Gene", "Finding/Conflict"])
        self.tree_geneticinfo_variant.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        review_layout.addWidget(self.tree_geneticinfo_variant)

        button_layout = QHBoxLayout()
        delete_button = QPushButton("Delete Selected"); delete_button.setProperty("cssClass", "danger"); delete_button.clicked.connect(self.delete_drug_review_entry)
        refresh_button = QPushButton("Refresh"); refresh_button.setProperty("cssClass", "secondary"); refresh_button.clicked.connect(self.load_drug_review_data)
        button_layout.addStretch(); button_layout.addWidget(delete_button); button_layout.addWidget(refresh_button)

        review_layout.addLayout(button_layout)
        review_group.setLayout(review_layout)
        layout.addWidget(review_group)
        tab.setLayout(layout)

        self.load_drug_review_data()
        return tab

    # --- Backend and Helper Methods ---

    def get_user_id(self, la_name, fi_name):
        try:
            query = 'SELECT user_id FROM patientsinfo WHERE last_name = %s AND first_name = %s'
            self.db_connection.cursor.execute(query, (la_name, fi_name))
            result = self.db_connection.cursor.fetchone()
            return result['user_id'] if result else None
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not retrieve User ID: {e}")
            return None

    def on_refill_clicked(self, med_name, prescriber, instructions):

        try:
            # Fetch prescription_id
            query_pres_id = "SELECT prescription_id FROM Prescriptions WHERE user_id = %s AND medication_name = %s LIMIT 1"
            self.db_connection.cursor.execute(query_pres_id, (self.selected_user_id, med_name))
            pres_row = self.db_connection.cursor.fetchone()
            if not pres_row: raise Exception("Prescription ID not found.")
            # Lower case of med_name

            query_ndc = "SELECT ndc FROM bottles WHERE medication_id = (SELECT id FROM medications WHERE name = %s) LIMIT 1"
            self.db_connection.cursor.execute(query_ndc, (med_name,))
            ndc_row = self.db_connection.cursor.fetchone()
            if not ndc_row: raise Exception("NDC not found for medication.")
            self.db_connection.cursor.execute("SELECT quantity FROM Prescriptions WHERE prescription_id = %s", (pres_row['prescription_id'],))
            qty = self.db_connection.cursor.fetchone()['quantity']
            if not qty: raise Exception("Quantity not found for prescription.")
            insert_data = (
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "1618", self.f_name, self.l_name,
                med_name, qty, "Pick-up", "No", instructions, pres_row['prescription_id'], ndc_row['ndc']
            )
            insert_query = """INSERT INTO {}(promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, instructions, prescription_id, ndc)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            self.db_connection.cursor.execute(insert_query.format("ActivatedPrescriptions"), insert_data)
            self.db_connection.cursor.execute(insert_query.format("ProductSelectionQueue"), insert_data)
            self.db_connection.connection.commit()
            QMessageBox.information(self.profile_window, "Success", f"Refill for {med_name} has been processed.")
        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to add refill: {e}")

    def on_prescription_select(self, item):
        # This function is now for opening the detail view on double-click
        prescriber_info = {
            "med_name": item.text(0), "refills": int(item.text(1)),
            "prescriber": item.text(2), "instructions": item.text(3),
        }
        query = "SELECT prescription_id, prescription_image FROM Prescriptions WHERE user_id = %s AND medication_name = %s"
        self.db_connection.cursor.execute(query, (self.selected_user_id, item.text(0)))
        row = self.db_connection.cursor.fetchone()
        if row:
            PrescriptionDetailView(prescriber_info, row.get('prescription_id'), self.db_connection).exec()
        else:
            QMessageBox.warning(self.profile_window, "Not Found", "Could not find details for the selected prescription.")

    import random

    def add_prescription(self):
        med_name = self.pres_med_name_input.text().strip()
        if not med_name or self.selected_user_id is None:
            QMessageBox.warning(self.profile_window, "Input Error", "Medication name is required.")
            return

        try:
            cursor = self.db_connection.cursor  # Correct - no parentheses for MySQL connector

            # Step 1: Insert prescription without rx_number
            insert_query = '''
                INSERT INTO Prescriptions (user_id, medication_name, refills, prescriber, instructions, quantity)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (
                self.selected_user_id,
                med_name,
                self.pres_refills_input.value(),
                self.pres_prescriber_input.text().strip(),
                self.pres_instructions_input.text().strip(),
                self.pres_quantity_input.value()
            )
            cursor.execute(insert_query, values)
            self.db_connection.connection.commit()

            # Step 2: Get the inserted prescription_id
            prescription_id = cursor.lastrowid

            # Step 3: Get drug_class from medications table
            cursor.execute("SELECT drug_class FROM medications WHERE name = %s", (med_name,))
            result = cursor.fetchone()

            # Handle dictionary result properly
            if result and 'drug_class' in result and result['drug_class'] is not None:
                drug_class = str(result['drug_class'])
            else:
                drug_class = "0"

            # Validate drug_class is numeric, fallback to "0" if not
            if not drug_class.isdigit():
                drug_class = "0"

            # Step 4: Generate unique 7-digit rx_number starting with drug_class
            random_part = f"{random.randint(0, 999999):06d}"  # zero-padded 6 digits
            rx_number_str = drug_class + random_part  # e.g. "6123456"
            rx_number = int(rx_number_str)  # convert to int for DB

            # Step 5: Update the inserted record with rx_number
            cursor.execute(
                "UPDATE Prescriptions SET rx_number = %s WHERE prescription_id = %s",
                (rx_number, prescription_id)
            )
            self.db_connection.connection.commit()

            # Step 6: Refresh UI and clear form
            self.load_prescriptions()
            self.pres_med_name_input.clear()
            self.pres_refills_input.setValue(0)
            self.pres_prescriber_input.clear()
            self.pres_instructions_input.clear()
            self.pres_quantity_input.setValue(0)

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to add prescription: {e}")


    def load_prescriptions(self):
        if not self.selected_user_id:
            return
        try:
            self.tree_prescriptions.clear()
            query = 'SELECT medication_name, refills, prescriber, instructions, quantity FROM Prescriptions WHERE user_id = %s'
            self.db_connection.cursor.execute(query, (self.selected_user_id,))
            for pres in self.db_connection.cursor.fetchall():
                item = QTreeWidgetItem([
                    pres['medication_name'],
                    str(pres['refills']),
                    pres['prescriber'],
                    pres['instructions'],
                    str(pres['quantity']),
                    "",  # Action placeholder
                ])
                self.tree_prescriptions.addTopLevelItem(item)
                btn = QPushButton("Refill Rx")
                btn.setProperty("cssClass", "warning")
                btn.clicked.connect(lambda _, m=pres['medication_name'], p=pres['prescriber'], i=pres['instructions']: self.on_refill_clicked(m, p, i))
                self.tree_prescriptions.setItemWidget(item, 5, btn)
        except Exception as e:
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to load prescriptions: {e}")


    def save_genetic_info(self):
        gene = self.genetic_entries['gene'].text().strip()
        variant = self.genetic_entries['genetic_variant'].text().strip()
        genotype = self.genetic_entries['genotype'].text().strip()
        if not gene or not variant:
            QMessageBox.warning(self.profile_window, "Input Error", "Gene and Genetic Variant are required.")
            return

        try:
            # Insert into own DB first
            query_genetic = 'INSERT INTO final_genetic_info (user_id, gene, genetic_variant, disease, genotype) VALUES (%s, %s, %s, %s, %s)'
            values_genetic = (self.selected_user_id, gene, variant, self.genetic_entries['disease'].text(), self.genetic_entries['genotype'].text())
            self.db_connection.cursor.execute(query_genetic, values_genetic)

            # Fetch from PharmGKB
            url = f'https://api.pharmgkb.org/v1/data/variantAnnotation?location.genes.symbol={gene}&location.fingerprint={variant}'
            response = requests.get(url, headers={'accept': 'application/json'})
            response.raise_for_status() # Raise an exception for bad status codes

            for item in response.json().get("data", []):
                if item.get("score", 0) >= 3:
                    for chemical in item.get("relatedChemicals", []):
                        drug_name = chemical.get("name")
                        sentence = item.get("sentence")
                        query_review = 'INSERT INTO drug_review (user_id, drug_name, drug_conflict, genetic_variant, gene, genotype) VALUES (%s, %s, %s, %s, %s, %s)'
                        self.db_connection.cursor.execute(query_review, (self.selected_user_id, drug_name, sentence, variant, gene, genotype))

            self.db_connection.connection.commit()
            self.load_genetic_data()
            self.load_drug_review_data()
            for entry in self.genetic_entries.values(): entry.clear()
        except requests.RequestException as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "API Error", f"Failed to fetch data from PharmGKB: {e}")
        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to save genetic info: {e}")

    def load_genetic_data(self):
        if not self.selected_user_id: return
        try:
            self.tree_genetic_variant.clear()
            query = 'SELECT gene, genetic_variant, disease, genotype FROM final_genetic_info WHERE user_id = %s'
            self.db_connection.cursor.execute(query, (self.selected_user_id,))
            for info in self.db_connection.cursor.fetchall():
                self.tree_genetic_variant.addTopLevelItem(QTreeWidgetItem([str(v) for v in info.values()]))
        except Exception as e:
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to load genetic data: {e}")

    def load_drug_review_data(self):
        if not self.selected_user_id: return
        try:
            self.tree_geneticinfo_variant.clear()
            query = "SELECT gene, drug_name, drug_conflict FROM drug_review WHERE user_id = %s ORDER BY gene, drug_name"
            self.db_connection.cursor.execute(query, (self.selected_user_id,))
            current_gene = ""
            for row in self.db_connection.cursor.fetchall():
                if row['gene'] != current_gene:
                    current_gene = row['gene']
                    gene_item = QTreeWidgetItem([current_gene, ""])
                    gene_item.setFont(0, QFont("JetBrains Mono", 14, QFont.Weight.Bold))
                    self.tree_geneticinfo_variant.addTopLevelItem(gene_item)

                drug_item = QTreeWidgetItem(["", f"{row['drug_name']}: {row['drug_conflict']}"])
                gene_item.addChild(drug_item)
            self.tree_geneticinfo_variant.expandAll()
        except Exception as e:
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to load drug review data: {e}")

    def delete_genetic_entry(self):
        item = self.tree_genetic_variant.currentItem()
        if not item: return
        gene = item.text(0)
        variant = item.text(1)
        reply = QMessageBox.question(self.profile_window, 'Confirm Deletion', f"Delete genetic entry for {gene} ({variant}) and all associated drug reviews?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        try:
            # Also delete associated drug reviews
            query_review = "DELETE FROM drug_review WHERE user_id = %s AND gene = %s AND genetic_variant = %s"
            self.db_connection.cursor.execute(query_review, (self.selected_user_id, gene, variant))
            query_genetic = "DELETE FROM final_genetic_info WHERE user_id = %s AND gene = %s AND genetic_variant = %s"
            self.db_connection.cursor.execute(query_genetic, (self.selected_user_id, gene, variant))
            self.db_connection.connection.commit()
            self.load_genetic_data() # Refresh
            self.load_drug_review_data() # Refresh
        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to delete entry: {e}")

    def delete_drug_review_entry(self):
        item = self.tree_geneticinfo_variant.currentItem()
        if not item or not item.parent(): return # Only allow deletion of child items

        # Extract info from text
        full_text = item.text(1)
        drug_name = full_text.split(':')[0]
        gene = item.parent().text(0)

        reply = QMessageBox.question(self.profile_window, 'Confirm Deletion', f"Delete drug review entry for {drug_name} related to gene {gene}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return

        try:
            query = "DELETE FROM drug_review WHERE user_id = %s AND drug_name = %s AND gene = %s"
            self.db_connection.cursor.execute(query, (self.selected_user_id, drug_name, gene))
            self.db_connection.connection.commit()
            self.load_drug_review_data() # Refresh
        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self.profile_window, "Database Error", f"Failed to delete drug review: {e}")