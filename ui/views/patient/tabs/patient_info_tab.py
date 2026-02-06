from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QGroupBox, QFormLayout, QLineEdit,
    QDateEdit, QComboBox, QCheckBox, QVBoxLayout, QLabel
)
from PyQt6.QtCore import QDate
from datetime import datetime


class PatientInfoTab(QWidget):
    """Patient Information tab - comprehensive demographics, contact, address, and preferences"""

    def __init__(self, patient_data=None, db_connection=None):
        super().__init__()
        self.patient_data = patient_data or {}
        self.db_connection = db_connection
        self._ensure_columns()
        self.init_ui()

    def _ensure_columns(self):
        """Add missing columns to patientsinfo if they don't exist"""
        if not self.db_connection:
            return
        new_columns = [
            ("gender", "VARCHAR(20)"),
            ("race_ethnicity", "VARCHAR(50)"),
            ("language", "VARCHAR(30) DEFAULT 'English'"),
            ("address_2", "VARCHAR(255)"),
            ("zip_code", "VARCHAR(10)"),
            ("cell_phone", "VARCHAR(20)"),
            ("work_phone", "VARCHAR(20)"),
            ("email", "VARCHAR(100)"),
            ("emergency_contact_name", "VARCHAR(100)"),
            ("emergency_contact_phone", "VARCHAR(20)"),
            ("preferred_location", "VARCHAR(100)"),
            ("child_resistant_caps", "TINYINT(1) DEFAULT 1"),
            ("generic_substitution", "TINYINT(1) DEFAULT 1"),
            ("large_print_labels", "TINYINT(1) DEFAULT 0"),
        ]
        try:
            cursor = self.db_connection.cursor
            for col_name, col_type in new_columns:
                try:
                    cursor.execute(
                        f"ALTER TABLE patientsinfo ADD COLUMN {col_name} {col_type}"
                    )
                except Exception:
                    pass  # Column already exists
            self.db_connection.connection.commit()

            # Reload patient data with new columns
            user_id = self.patient_data.get('user_id')
            if user_id:
                cursor.execute("SELECT * FROM patientsinfo WHERE user_id = %s", (user_id,))
                refreshed = cursor.fetchone()
                if refreshed:
                    self.patient_data = refreshed
        except Exception as e:
            print(f"Error ensuring patient columns: {e}")

    def init_ui(self):
        """Initialize the tab UI with 4 groups in a 2x2 grid"""
        layout = QGridLayout(self)

        # ── Demographics ──────────────────────────────────
        demo_group = QGroupBox("Demographics")
        demo_layout = QFormLayout()

        self.first_name = QLineEdit(self.patient_data.get('first_name', ''))
        self.first_name.setReadOnly(True)
        demo_layout.addRow("First Name:", self.first_name)

        self.last_name = QLineEdit(self.patient_data.get('last_name', ''))
        self.last_name.setReadOnly(True)
        demo_layout.addRow("Last Name:", self.last_name)

        self.dob_edit = QDateEdit(calendarPopup=True)
        self.dob_edit.setReadOnly(True)
        try:
            dob_str = self.patient_data.get('Dateofbirth', '')
            dob_date = datetime.strptime(str(dob_str), '%Y-%m-%d').date()
            self.dob_edit.setDate(QDate(dob_date.year, dob_date.month, dob_date.day))
        except (ValueError, TypeError):
            pass
        demo_layout.addRow("Date of Birth:", self.dob_edit)

        self.gender = QComboBox()
        self.gender.addItems(["", "Male", "Female", "Non-Binary", "Other", "Prefer Not to Say"])
        self.gender.setEnabled(False)
        current_gender = self.patient_data.get('gender', '')
        idx = self.gender.findText(current_gender)
        if idx >= 0:
            self.gender.setCurrentIndex(idx)
        demo_layout.addRow("Gender:", self.gender)

        self.race_ethnicity = QLineEdit(self.patient_data.get('race_ethnicity', ''))
        self.race_ethnicity.setReadOnly(True)
        demo_layout.addRow("Race / Ethnicity:", self.race_ethnicity)

        self.language = QComboBox()
        self.language.addItems([
            "English", "Spanish", "French", "Mandarin", "Cantonese",
            "Vietnamese", "Korean", "Arabic", "Portuguese", "Other"
        ])
        self.language.setEnabled(False)
        current_lang = self.patient_data.get('language', 'English')
        lang_idx = self.language.findText(current_lang or 'English')
        if lang_idx >= 0:
            self.language.setCurrentIndex(lang_idx)
        demo_layout.addRow("Language:", self.language)

        demo_group.setLayout(demo_layout)
        layout.addWidget(demo_group, 0, 0)

        # ── Address ───────────────────────────────────────
        addr_group = QGroupBox("Address")
        addr_layout = QFormLayout()

        self.address_1 = QLineEdit(self.patient_data.get('address_1', ''))
        self.address_1.setReadOnly(True)
        addr_layout.addRow("Street Line 1:", self.address_1)

        self.address_2 = QLineEdit(self.patient_data.get('address_2', ''))
        self.address_2.setReadOnly(True)
        addr_layout.addRow("Street Line 2:", self.address_2)

        self.city = QLineEdit(self.patient_data.get('city', ''))
        self.city.setReadOnly(True)
        addr_layout.addRow("City:", self.city)

        self.state = QLineEdit(self.patient_data.get('state', ''))
        self.state.setReadOnly(True)
        addr_layout.addRow("State:", self.state)

        self.zip_code = QLineEdit(self.patient_data.get('zip_code', ''))
        self.zip_code.setReadOnly(True)
        addr_layout.addRow("Zip Code:", self.zip_code)

        addr_group.setLayout(addr_layout)
        layout.addWidget(addr_group, 0, 1)

        # ── Contact Information ───────────────────────────
        contact_group = QGroupBox("Contact Information")
        contact_layout = QFormLayout()

        self.phone = QLineEdit(self.patient_data.get('phone', ''))
        self.phone.setReadOnly(True)
        contact_layout.addRow("Home Phone:", self.phone)

        self.cell_phone = QLineEdit(self.patient_data.get('cell_phone', ''))
        self.cell_phone.setReadOnly(True)
        contact_layout.addRow("Cell Phone:", self.cell_phone)

        self.work_phone = QLineEdit(self.patient_data.get('work_phone', ''))
        self.work_phone.setReadOnly(True)
        contact_layout.addRow("Work Phone:", self.work_phone)

        self.email = QLineEdit(self.patient_data.get('email', ''))
        self.email.setReadOnly(True)
        contact_layout.addRow("Email:", self.email)

        # Emergency contact sub-section
        ec_label = QLabel("Emergency Contact")
        ec_label.setProperty("cssClass", "text-secondary")
        contact_layout.addRow("", ec_label)

        self.ec_name = QLineEdit(self.patient_data.get('emergency_contact_name', ''))
        self.ec_name.setReadOnly(True)
        contact_layout.addRow("Name:", self.ec_name)

        self.ec_phone = QLineEdit(self.patient_data.get('emergency_contact_phone', ''))
        self.ec_phone.setReadOnly(True)
        contact_layout.addRow("Phone:", self.ec_phone)

        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group, 1, 0)

        # ── Preferences ───────────────────────────────────
        pref_group = QGroupBox("Prescription Preferences")
        pref_layout = QVBoxLayout()

        self.child_caps = QCheckBox("Child-Resistant Caps")
        self.child_caps.setChecked(bool(self.patient_data.get('child_resistant_caps', 1)))
        self.child_caps.setEnabled(False)
        pref_layout.addWidget(self.child_caps)

        self.generic_sub = QCheckBox("Generic Substitution Allowed")
        self.generic_sub.setChecked(bool(self.patient_data.get('generic_substitution', 1)))
        self.generic_sub.setEnabled(False)
        pref_layout.addWidget(self.generic_sub)

        self.large_print = QCheckBox("Large-Print Labels")
        self.large_print.setChecked(bool(self.patient_data.get('large_print_labels', 0)))
        self.large_print.setEnabled(False)
        pref_layout.addWidget(self.large_print)

        pref_form = QFormLayout()
        self.preferred_location = QLineEdit(self.patient_data.get('preferred_location', ''))
        self.preferred_location.setReadOnly(True)
        pref_form.addRow("Preferred Location:", self.preferred_location)
        pref_layout.addLayout(pref_form)

        pref_layout.addStretch()

        pref_group.setLayout(pref_layout)
        layout.addWidget(pref_group, 1, 1)
