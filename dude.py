from DataBaseConnection import DatabaseConnection
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import requests
import sys


class PatientManagementSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.result = None
        self.dob = None
        self.last_name = None
        self.first_name = None
        self.l_name = None
        self.f_name = None

    def rx_s_patient(self):
        self.hide_frames()

        self.search_window = QDialog(self)
        self.search_window.setWindowTitle("Search Patient")
        self.search_window.setGeometry(100, 100, 1350, 600)

        # Create main layout
        main_layout = QVBoxLayout()

        # Create search form layout
        form_layout = QHBoxLayout()

        # Last name section
        lname_layout = QVBoxLayout()
        lname_label = QLabel("Last Name (Min chars:4) and/or Phone")
        self.lname_entry = QLineEdit()
        self.lname_entry.setFixedWidth(300)
        lname_layout.addWidget(lname_label)
        lname_layout.addWidget(self.lname_entry)

        # First name section
        fname_layout = QVBoxLayout()
        fname_label = QLabel("First Name (Min chars:2)")
        self.fname_entry = QLineEdit()
        self.fname_entry.setFixedWidth(200)
        fname_layout.addWidget(fname_label)
        fname_layout.addWidget(self.fname_entry)

        # Date of birth section
        dob_layout = QVBoxLayout()
        dob_label = QLabel("Date of Birth")
        self.dob_entry = QDateEdit()
        self.dob_entry.setCalendarPopup(True)
        self.dob_entry.setDate(QDate.currentDate())
        dob_layout.addWidget(dob_label)
        dob_layout.addWidget(self.dob_entry)

        form_layout.addLayout(lname_layout)
        form_layout.addLayout(fname_layout)
        form_layout.addLayout(dob_layout)
        form_layout.addStretch()

        # Create buttons layout
        button_layout = QHBoxLayout()

        search_button = QPushButton("Search Local")
        search_button.setProperty("cssClass", "primary")
        search_button.clicked.connect(self.search_patient)

        search_buttonc = QPushButton("Search Corporate")
        search_buttonc.setProperty("cssClass", "secondary")
        search_buttonc.clicked.connect(self.search_patient)

        new_pt_button = QPushButton("New Patient")
        new_pt_button.setProperty("cssClass", "success")
        new_pt_button.clicked.connect(lambda: self.rx_Profile_patient(self.result, self.dob, self.last_name, self.first_name))

        button_layout.addWidget(search_button)
        button_layout.addWidget(search_buttonc)
        button_layout.addWidget(new_pt_button)
        button_layout.addStretch()

        # Create tree widget for patient results
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["First Name", "Last Name", "Street", "City", "State", "Phone", "DOB"])
        self.tree.itemDoubleClicked.connect(self.on_row_select)

        # Add all components to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree)

        self.search_window.setLayout(main_layout)
        self.search_window.exec()

    def search_patient(self):
        self.last_name = self.lname_entry.text()
        self.first_name = self.fname_entry.text()
        self.dob = self.dob_entry.date().toString("yyyy-MM-dd")

        db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')

        if self.last_name and self.first_name:
            db_connection.cursor.execute(
                'SELECT * FROM patientsinfo WHERE first_name LIKE %s AND last_name LIKE %s',
                (f"{self.first_name}%", f"{self.last_name}%"))
        elif self.dob and self.last_name:
            db_connection.cursor.execute(
                'SELECT * FROM patientsinfo WHERE Dateofbirth = %s AND last_name LIKE %s',
                (self.dob, f"{self.last_name}%"))
        elif self.last_name:
            db_connection.cursor.execute(
                'SELECT * FROM patientsinfo WHERE last_name LIKE %s', (f"{self.last_name}%",))
        elif self.dob:
            db_connection.cursor.execute(
                'SELECT * FROM patientsinfo WHERE Dateofbirth=%s', (self.dob,))

        patients = db_connection.cursor.fetchall()
        self.display_patients(patients)

    def display_patients(self, patients):
        self.tree.clear()

        for patient in patients:
            item = QTreeWidgetItem([
                patient['first_name'],
                patient['last_name'],
                patient['address_1'],
                patient['city'],
                patient['state'],
                patient['phone'],
                str(patient['Dateofbirth'])
            ])
            self.tree.addTopLevelItem(item)

    def on_row_select(self, item, column):
        self.l_name = item.text(1)  # Last name
        self.f_name = item.text(0)  # First name

        db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="pgx_password", database='pgx_db')
        db_connection.cursor.execute(
            'SELECT * from patientsinfo WHERE last_name= %s AND first_name=%s',
            (self.l_name, self.f_name))
        self.result = db_connection.cursor.fetchone()

        if self.result:
            self.dob = self.result['Dateofbirth']
            self.rx_Profile_patient(self.result, self.l_name, self.f_name, self.dob)
        else:
            print("No results")

    def rx_Profile_patient(self, result, la_name, fi_name, dob):
        if hasattr(self, "search_window") and self.search_window:
            self.search_window.close()

        # Create main profile window
        self.profile_window = QDialog(self)
        self.profile_window.setWindowTitle("Patient Profile")
        self.profile_window.setGeometry(50, 50, 1400, 800)

        # Create tab widget
        self.notebook = QTabWidget()

        # Create tabs
        tab1 = self.create_patient_info_tab(fi_name, la_name, dob)
        tab2 = self.create_allergies_tab()
        tab3 = self.create_insurance_tab()
        tab4 = self.create_prescriptions_tab()
        tab5 = self.create_transactions_tab()
        tab6 = self.create_genomics_tab(la_name, fi_name)
        tab7 = self.create_drug_review_tab(la_name, fi_name)

        self.notebook.addTab(tab1, "1. Patient Info")
        self.notebook.addTab(tab2, "2. Allergies")
        self.notebook.addTab(tab3, "3. Insurance")
        self.notebook.addTab(tab4, "4. Prescriptions")
        self.notebook.addTab(tab5, "5. Transactions")
        self.notebook.addTab(tab6, "6. Genomics")
        self.notebook.addTab(tab7, "7. Drug Review")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.notebook)
        self.profile_window.setLayout(layout)

        self.result = result
        self.l_name = la_name
        self.f_name = fi_name

        self.profile_window.exec()

    def create_patient_info_tab(self, fi_name, la_name, dob):
        tab = QWidget()

        layout = QGridLayout()

        # First Name
        first_name_label = QLabel("First Name")
        first_name_entry = QLineEdit(fi_name)

        # Last Name
        last_name_label = QLabel("Last Name")
        last_name_entry = QLineEdit(la_name)

        # Date of Birth
        dob_label = QLabel("Date of Birth")
        dob_entry = QLineEdit(str(dob))

        layout.addWidget(first_name_label, 0, 0)
        layout.addWidget(first_name_entry, 0, 1)
        layout.addWidget(last_name_label, 0, 2)
        layout.addWidget(last_name_entry, 0, 3)
        layout.addWidget(dob_label, 0, 4)
        layout.addWidget(dob_entry, 0, 5)

        layout.setRowStretch(1, 1)  # Add stretch to push content to top

        tab.setLayout(layout)
        return tab

    def create_allergies_tab(self):
        tab = QWidget()

        layout = QVBoxLayout()
        label = QLabel("Content for Tab 2")
        layout.addWidget(label)

        tab.setLayout(layout)
        return tab

    def create_insurance_tab(self):
        tab = QWidget()
        return tab

    def create_prescriptions_tab(self):
        tab = QWidget()

        layout = QVBoxLayout()

        # Create tree widget for prescriptions
        tree = QTreeWidget()
        tree.setHeaderLabels(["Medication Name", "Refills", "Prescriber", "Instructions"])

        # Add dummy data
        prescriptions = [
            ("Alprazolam 1 MG", "2", "Dr. A", "Take 1 tablet daily"),
            ("Clonazepam 2 MG", "1", "Dr. B", "Take 2 tablets daily"),
            ("Simvastatin 20 MG", "3", "Dr. C", "Take 3 tablets daily")
        ]

        for med, refills, prescriber, instructions in prescriptions:
            item = QTreeWidgetItem([med, refills, prescriber, instructions])
            tree.addTopLevelItem(item)

        layout.addWidget(tree)
        tab.setLayout(layout)
        return tab

    def create_transactions_tab(self):
        tab = QWidget()
        return tab

    def create_genomics_tab(self, la_name, fi_name):
        tab = QWidget()

        layout = QVBoxLayout()

        # Create genetic variant tree
        self.tree_genetic_variant = QTreeWidget()
        self.tree_genetic_variant.setHeaderLabels(["Gene", "Genetic Variant", "Disease", "Genotype"])

        # Add sample data
        sample_item = QTreeWidgetItem(["SLCO1B1", "rs414956", "Hypertension", "CT"])
        self.tree_genetic_variant.addTopLevelItem(sample_item)

        # Load data from database
        self.load_genetic_data(la_name, fi_name)

        layout.addWidget(self.tree_genetic_variant)

        # Create input form
        form_widget = self.create_genetic_input_form(la_name, fi_name)
        layout.addWidget(form_widget)

        tab.setLayout(layout)
        return tab

    def create_genetic_input_form(self, la_name, fi_name):
        form_widget = QWidget()
        form_widget.setFixedHeight(150)

        layout = QGridLayout()

        # Labels
        gene_label = QLabel("Gene")
        variant_label = QLabel("Genetic Variant")
        disease_label = QLabel("Disease")
        genotype_label = QLabel("Genotype")

        # Entry fields
        self.gene_entry = QLineEdit()
        self.variant_entry = QLineEdit()
        self.disease_entry = QLineEdit()
        self.genotype_entry = QLineEdit()

        # Buttons
        add_button = QPushButton("Add Information")
        add_button.setProperty("cssClass", "success")
        add_button.clicked.connect(lambda: self.save_info(la_name, fi_name))

        delete_button = QPushButton("Delete")
        delete_button.setProperty("cssClass", "danger")
        delete_button.clicked.connect(self.delete_entry)

        # Layout
        layout.addWidget(gene_label, 0, 0)
        layout.addWidget(self.gene_entry, 1, 0)
        layout.addWidget(variant_label, 0, 1)
        layout.addWidget(self.variant_entry, 1, 1)
        layout.addWidget(disease_label, 0, 2)
        layout.addWidget(self.disease_entry, 1, 2)
        layout.addWidget(genotype_label, 0, 3)
        layout.addWidget(self.genotype_entry, 1, 3)
        layout.addWidget(add_button, 2, 0)
        layout.addWidget(delete_button, 2, 1)

        form_widget.setLayout(layout)
        return form_widget

    def create_drug_review_tab(self, la_name, fi_name):
        tab = QWidget()

        layout = QVBoxLayout()

        # Create drug review tree
        self.tree_geneticinfo_variant = QTreeWidget()
        self.tree_geneticinfo_variant.setHeaderLabels(["Drug Name", "Drug Conflict"])

        # Load drug review data
        self.load_drug_review_data(la_name, fi_name)

        layout.addWidget(self.tree_geneticinfo_variant)

        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setProperty("cssClass", "danger")
        delete_button.clicked.connect(self.delete_entry_variant)
        layout.addWidget(delete_button)

        tab.setLayout(layout)
        return tab

    def load_genetic_data(self, la_name, fi_name):
        db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')
        db_connection.cursor.execute('SELECT user_id FROM patientsinfo WHERE last_name = %s AND first_name = %s', (la_name, fi_name))
        user_id_result = db_connection.cursor.fetchone()

        if user_id_result:
            user_id = user_id_result['user_id']
            db_connection.cursor.execute('SELECT * FROM final_genetic_info WHERE user_id = %s', (user_id,))
            allinfo = db_connection.cursor.fetchall()

            if allinfo:
                for parameter in allinfo:
                    item = QTreeWidgetItem([
                        parameter['gene'],
                        parameter['genetic_variant'],
                        parameter['disease'],
                        parameter.get('genotype', '')  # Handle missing genotype
                    ])
                    self.tree_genetic_variant.addTopLevelItem(item)

    def load_drug_review_data(self, la_name, fi_name):
        db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')
        db_connection.cursor.execute('SELECT user_id FROM patientsinfo WHERE last_name = %s AND first_name = %s', (la_name, fi_name))
        user_id_result = db_connection.cursor.fetchone()

        if user_id_result:
            user_id = user_id_result['user_id']
            query = """
                SELECT drug_name, GROUP_CONCAT(drug_conflict, ', ') AS drug_conflicts
                FROM drug_review
                WHERE user_id = %s
                GROUP BY drug_name
                ORDER BY drug_name
            """
            db_connection.cursor.execute(query, (user_id,))
            drugreviewinfo = db_connection.cursor.fetchall()

            if drugreviewinfo:
                self.tree_geneticinfo_variant.clear()
                for row in drugreviewinfo:
                    drug_name = row['drug_name']
                    drug_conflicts = row['drug_conflicts']

                    # Insert drug name in one row
                    drug_item = QTreeWidgetItem([drug_name, ""])
                    self.tree_geneticinfo_variant.addTopLevelItem(drug_item)

                    # Insert each drug conflict in a separate row below the drug name
                    for conflict in drug_conflicts.split(','):
                        conflict_item = QTreeWidgetItem(["", conflict.strip()])
                        self.tree_geneticinfo_variant.addTopLevelItem(conflict_item)

    def save_info(self, la_name, fi_name):
        gene = self.gene_entry.text()
        genetic_variant = self.variant_entry.text()
        disease = self.disease_entry.text()
        genotype = self.genotype_entry.text()

        url = f'https://api.pharmgkb.org/v1/data/variantAnnotation?location.genes.symbol={gene}&location.fingerprint={genetic_variant}'
        headers = {'accept': 'application/json'}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json().get("data", [])
                drug_reviews = []

                for item in data:
                    score = item.get("score", 0)
                    if score >= 3:
                        sentence = item.get("sentence", "")
                        related_chemicals = item.get("relatedChemicals", [])
                        drug_names = [chemical.get("name") for chemical in related_chemicals]
                        drug_reviews.extend([(drug_name, sentence) for drug_name in drug_names])

                # Database operations
                db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')
                db_connection.cursor.execute('SELECT user_id FROM patientsinfo WHERE last_name = %s AND first_name = %s', (la_name, fi_name))
                result = db_connection.cursor.fetchone()

                if result:
                    user_id = result['user_id']

                    # Insert genetic info
                    sql_insert_genetic_info = 'INSERT INTO final_genetic_info (user_id, gene, genetic_variant, disease) VALUES (%s, %s, %s, %s)'
                    values_genetic_info = (user_id, gene, genetic_variant, disease)
                    db_connection.cursor.execute(sql_insert_genetic_info, values_genetic_info)
                    db_connection.connection.commit()

                    # Insert drug reviews
                    for drug_name, drug_sentence in drug_reviews:
                        sql_insert_drug_review = 'INSERT INTO drug_review (user_id, drug_name, drug_conflict) VALUES (%s, %s, %s)'
                        values_drug_review = (user_id, drug_name, drug_sentence)
                        db_connection.cursor.execute(sql_insert_drug_review, values_drug_review)
                        db_connection.connection.commit()

                    # Refresh the tree
                    self.load_genetic_data(la_name, fi_name)

                    # Clear entries
                    self.gene_entry.clear()
                    self.variant_entry.clear()
                    self.disease_entry.clear()
                    self.genotype_entry.clear()

        except Exception as e:
            print(f"Error saving info: {e}")

    def delete_entry(self):
        current_item = self.tree_genetic_variant.currentItem()
        if current_item:
            gene = current_item.text(0)

            db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')
            db_connection.cursor.execute("SELECT genetic_info_id FROM final_genetic_info WHERE gene = %s", (gene,))
            genetic_info_id = db_connection.cursor.fetchone()

            if genetic_info_id:
                db_connection.cursor.execute('DELETE from final_genetic_info WHERE genetic_info_id= %s', (genetic_info_id['genetic_info_id'],))
                db_connection.connection.commit()

                # Remove from tree
                index = self.tree_genetic_variant.indexOfTopLevelItem(current_item)
                self.tree_genetic_variant.takeTopLevelItem(index)

    def delete_entry_variant(self):
        current_item = self.tree_geneticinfo_variant.currentItem()
        if current_item:
            drug_name = current_item.text(0)

            if drug_name:  # Only delete if it's a drug name row, not a conflict row
                db_connection = DatabaseConnection(host='localhost', user='pgx_user', password="", database='pgx_db')
                db_connection.cursor.execute("SELECT review_id FROM drug_review WHERE drug_name = %s", (drug_name,))
                review_id_result = db_connection.cursor.fetchone()

                if review_id_result:
                    review_id = review_id_result['review_id']
                    db_connection.cursor.execute('DELETE FROM drug_review WHERE review_id = %s', (review_id,))
                    db_connection.connection.commit()

                    # Refresh the tree
                    self.load_drug_review_data(self.l_name, self.f_name)

    def hide_frames(self):
        # Placeholder for hiding frames - implement as needed for your main window
        pass