from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QDateEdit, QComboBox, QGridLayout
)
from PyQt6.QtCore import QDate
from datetime import datetime


class InsuranceTab(QWidget):
    """Insurance / Third-Party tab - NCPDP-standard billing fields"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self._ensure_columns()
        self.init_ui()
        if db_connection and user_id:
            self.load_insurance()

    def _ensure_columns(self):
        """Add missing columns to patient_insurance if table/columns don't exist"""
        if not self.db_connection:
            return
        try:
            cursor = self.db_connection.cursor
            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patient_insurance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    plan_name VARCHAR(100),
                    insurance_provider VARCHAR(100),
                    bin_number VARCHAR(6),
                    pcn VARCHAR(20),
                    group_number VARCHAR(30),
                    cardholder_id VARCHAR(30),
                    person_code VARCHAR(5),
                    relationship_code VARCHAR(3),
                    policy_number VARCHAR(50),
                    member_id VARCHAR(50),
                    plan_type VARCHAR(30) DEFAULT 'Commercial',
                    effective_date DATE,
                    expiration_date DATE,
                    copay_generic DECIMAL(6,2),
                    copay_brand DECIMAL(6,2),
                    UNIQUE KEY unique_user (user_id)
                )
            """)
            # Add columns that might be missing on older tables
            new_columns = [
                ("plan_name", "VARCHAR(100)"),
                ("bin_number", "VARCHAR(6)"),
                ("pcn", "VARCHAR(20)"),
                ("cardholder_id", "VARCHAR(30)"),
                ("person_code", "VARCHAR(5)"),
                ("relationship_code", "VARCHAR(3)"),
                ("plan_type", "VARCHAR(30) DEFAULT 'Commercial'"),
                ("effective_date", "DATE"),
                ("expiration_date", "DATE"),
                ("copay_generic", "DECIMAL(6,2)"),
                ("copay_brand", "DECIMAL(6,2)"),
            ]
            for col_name, col_type in new_columns:
                try:
                    cursor.execute(
                        f"ALTER TABLE patient_insurance ADD COLUMN {col_name} {col_type}"
                    )
                except Exception:
                    pass
            self.db_connection.connection.commit()
        except Exception as e:
            print(f"Error ensuring insurance columns: {e}")

    def init_ui(self):
        """Initialize the tab UI with Plan Info and Coverage Details groups"""
        layout = QGridLayout(self)

        # ── Plan Information (NCPDP fields) ───────────────
        plan_group = QGroupBox("Plan Information")
        plan_layout = QFormLayout()

        self.plan_name = QLineEdit()
        self.plan_name.setReadOnly(True)
        plan_layout.addRow("Plan Name:", self.plan_name)

        self.provider = QLineEdit()
        self.provider.setReadOnly(True)
        plan_layout.addRow("Insurance Provider:", self.provider)

        self.bin_number = QLineEdit()
        self.bin_number.setReadOnly(True)
        self.bin_number.setMaximumWidth(120)
        plan_layout.addRow("BIN:", self.bin_number)

        self.pcn = QLineEdit()
        self.pcn.setReadOnly(True)
        plan_layout.addRow("PCN:", self.pcn)

        self.group_num = QLineEdit()
        self.group_num.setReadOnly(True)
        plan_layout.addRow("Group Number:", self.group_num)

        self.cardholder_id = QLineEdit()
        self.cardholder_id.setReadOnly(True)
        plan_layout.addRow("Cardholder ID:", self.cardholder_id)

        self.person_code = QLineEdit()
        self.person_code.setReadOnly(True)
        self.person_code.setMaximumWidth(80)
        plan_layout.addRow("Person Code:", self.person_code)

        self.relationship_code = QLineEdit()
        self.relationship_code.setReadOnly(True)
        self.relationship_code.setMaximumWidth(80)
        plan_layout.addRow("Relationship Code:", self.relationship_code)

        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group, 0, 0)

        # ── Coverage Details ──────────────────────────────
        coverage_group = QGroupBox("Coverage Details")
        coverage_layout = QFormLayout()

        self.plan_type = QComboBox()
        self.plan_type.addItems([
            "Commercial", "Medicare Part D", "Medicaid",
            "Workers Comp", "TRICARE", "VA", "Other"
        ])
        self.plan_type.setEnabled(False)
        coverage_layout.addRow("Plan Type:", self.plan_type)

        self.policy_num = QLineEdit()
        self.policy_num.setReadOnly(True)
        coverage_layout.addRow("Policy Number:", self.policy_num)

        self.member_id = QLineEdit()
        self.member_id.setReadOnly(True)
        coverage_layout.addRow("Member ID:", self.member_id)

        self.effective_date = QDateEdit(calendarPopup=True)
        self.effective_date.setReadOnly(True)
        coverage_layout.addRow("Effective Date:", self.effective_date)

        self.expiration_date = QDateEdit(calendarPopup=True)
        self.expiration_date.setReadOnly(True)
        coverage_layout.addRow("Expiration Date:", self.expiration_date)

        self.copay_generic = QLineEdit()
        self.copay_generic.setReadOnly(True)
        self.copay_generic.setMaximumWidth(100)
        coverage_layout.addRow("Copay (Generic):", self.copay_generic)

        self.copay_brand = QLineEdit()
        self.copay_brand.setReadOnly(True)
        self.copay_brand.setMaximumWidth(100)
        coverage_layout.addRow("Copay (Brand):", self.copay_brand)

        coverage_group.setLayout(coverage_layout)
        layout.addWidget(coverage_group, 0, 1)

        layout.setRowStretch(1, 1)

    def load_insurance(self):
        """Load insurance information from database"""
        if not self.db_connection or not self.user_id:
            return

        try:
            query = """
                SELECT plan_name, insurance_provider, bin_number, pcn,
                       group_number, cardholder_id, person_code, relationship_code,
                       policy_number, member_id, plan_type,
                       effective_date, expiration_date,
                       copay_generic, copay_brand
                FROM patient_insurance
                WHERE user_id = %s
                LIMIT 1
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            ins = self.db_connection.cursor.fetchone()

            if ins:
                self.plan_name.setText(ins.get('plan_name', '') or '')
                self.provider.setText(ins.get('insurance_provider', '') or '')
                self.bin_number.setText(ins.get('bin_number', '') or '')
                self.pcn.setText(ins.get('pcn', '') or '')
                self.group_num.setText(ins.get('group_number', '') or '')
                self.cardholder_id.setText(ins.get('cardholder_id', '') or '')
                self.person_code.setText(ins.get('person_code', '') or '')
                self.relationship_code.setText(ins.get('relationship_code', '') or '')
                self.policy_num.setText(ins.get('policy_number', '') or '')
                self.member_id.setText(ins.get('member_id', '') or '')

                # Plan type combo
                plan_type = ins.get('plan_type', 'Commercial') or 'Commercial'
                pt_idx = self.plan_type.findText(plan_type)
                if pt_idx >= 0:
                    self.plan_type.setCurrentIndex(pt_idx)

                # Dates
                eff = ins.get('effective_date')
                if eff:
                    try:
                        d = datetime.strptime(str(eff), '%Y-%m-%d').date()
                        self.effective_date.setDate(QDate(d.year, d.month, d.day))
                    except (ValueError, TypeError):
                        pass

                exp = ins.get('expiration_date')
                if exp:
                    try:
                        d = datetime.strptime(str(exp), '%Y-%m-%d').date()
                        self.expiration_date.setDate(QDate(d.year, d.month, d.day))
                    except (ValueError, TypeError):
                        pass

                # Copays
                copay_g = ins.get('copay_generic')
                if copay_g is not None:
                    self.copay_generic.setText(f"${copay_g:.2f}")
                copay_b = ins.get('copay_brand')
                if copay_b is not None:
                    self.copay_brand.setText(f"${copay_b:.2f}")

        except Exception as e:
            print(f"Error loading insurance data: {e}")
