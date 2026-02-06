from DataBaseConnection import DatabaseConnection
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from DataBaseConnection import db_connection


class PatientSearchSystem(QWidget):
    def __init__(self, db_connection,parent=None):
        super().__init__(parent)
        # Styling handled by global theme
        self.db_connection = db_connection

        self.result = None
        self.dob = None
        self.last_name = None
        self.first_name = None
        self.l_name = None
        self.f_name = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()

        lname_layout = QVBoxLayout()
        lname_label = QLabel("Last Name (Min chars:4) and/or Phone")
        self.lname_entry = QLineEdit()
        self.lname_entry.setFixedWidth(300)
        lname_layout.addWidget(lname_label)
        lname_layout.addWidget(self.lname_entry)

        fname_layout = QVBoxLayout()
        fname_label = QLabel("First Name (Min chars:2)")
        self.fname_entry = QLineEdit()
        self.fname_entry.setFixedWidth(200)
        fname_layout.addWidget(fname_label)
        fname_layout.addWidget(self.fname_entry)

        dob_layout = QVBoxLayout()
        dob_label = QLabel("Date of Birth (DD/MM/YYYY)")

        dob_inputs_layout = QHBoxLayout()
        self.dob_day = QLineEdit()
        self.dob_day.setPlaceholderText("DD")
        self.dob_day.setMaxLength(2)
        self.dob_day.setFixedWidth(40)
        self.dob_month = QLineEdit()
        self.dob_month.setPlaceholderText("MM")
        self.dob_month.setMaxLength(2)
        self.dob_month.setFixedWidth(40)
        self.dob_year = QLineEdit()
        self.dob_year.setPlaceholderText("YYYY")
        self.dob_year.setMaxLength(4)
        self.dob_year.setFixedWidth(60)

        dob_inputs_layout.addWidget(self.dob_day)
        dob_inputs_layout.addWidget(QLabel("/"))
        dob_inputs_layout.addWidget(self.dob_month)
        dob_inputs_layout.addWidget(QLabel("/"))
        dob_inputs_layout.addWidget(self.dob_year)

        dob_layout.addWidget(dob_label)
        dob_layout.addLayout(dob_inputs_layout)

        form_layout.addLayout(lname_layout)
        form_layout.addLayout(fname_layout)
        form_layout.addLayout(dob_layout)
        form_layout.addStretch()

        button_layout = QHBoxLayout()

        search_button = QPushButton("Search Local")
        search_button.setProperty("cssClass", "primary")
        search_button.clicked.connect(self.search_patient)

        search_buttonc = QPushButton("Search Corporate")
        search_buttonc.setProperty("cssClass", "secondary")
        search_buttonc.clicked.connect(self.search_patient)

        new_pt_button = QPushButton("New Patient")
        new_pt_button.setProperty("cssClass", "success")
        new_pt_button.clicked.connect(lambda: self.open_patient_profile(self.result, self.last_name, self.first_name, self.dob))

        button_layout.addWidget(search_button)
        button_layout.addWidget(search_buttonc)
        button_layout.addWidget(new_pt_button)
        button_layout.addStretch()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["First Name", "Last Name", "Street", "City", "State", "Phone", "DOB"])
        self.tree.itemDoubleClicked.connect(self.on_row_select)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree)

    def get_dob_string(self):
        day = self.dob_day.text().strip()
        month = self.dob_month.text().strip()
        year = self.dob_year.text().strip()

        if not (day and month and year):
            return None
        try:
            day_i = int(day)
            month_i = int(month)
            year_i = int(year)

            if year_i < 100:
                if year_i <= 30:
                    year_i += 2000
                else:
                    year_i += 1900

            from datetime import datetime
            dob_obj = datetime(year_i, month_i, day_i)
            return dob_obj.strftime("%Y-%m-%d")
        except Exception:
            return None

    def search_patient(self):
        self.last_name = self.lname_entry.text().strip()
        self.first_name = self.fname_entry.text().strip()
        self.dob = self.get_dob_string()

        db_connection = self.db_connection

        query = "SELECT * FROM patientsinfo"
        conditions = []
        params = []

        if self.first_name:
            conditions.append("first_name LIKE %s")
            params.append(f"{self.first_name}%")

        if self.last_name:
            conditions.append("last_name LIKE %s")
            params.append(f"{self.last_name}%")

        if self.dob:
            conditions.append("Dateofbirth = %s")
            params.append(self.dob)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        else:
            self.display_patients([])
            return

        db_connection.cursor.execute(query, tuple(params))
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
        self.l_name = item.text(1)
        self.f_name = item.text(0)

        db_connection = self.db_connection
        db_connection.cursor.execute(
            'SELECT * from patientsinfo WHERE last_name= %s AND first_name=%s',
            (self.l_name, self.f_name))
        self.result = db_connection.cursor.fetchone()

        if self.result:
            self.dob = self.result['Dateofbirth']
            self.open_patient_profile(self.result, self.l_name, self.f_name, self.dob)
        else:
            print("No results")

    def open_patient_profile(self, result, la_name, fi_name, dob):
        from patient_profile import PatientProfileSystem

        profile_system = PatientProfileSystem(db_connection=self.db_connection)

        if result and 'user_id' in result:
            profile_system.selected_user_id = result['user_id']
        else:
            profile_system.selected_user_id = None

        profile_system.patient_first_name = fi_name
        profile_system.patient_last_name = la_name

        profile_system.show_patient_profile(result, la_name, fi_name, dob)

    def hide_frames(self):
        pass
