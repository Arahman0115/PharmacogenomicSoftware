from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel,
    QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt
from DataBaseConnection import DatabaseConnection
from datetime import datetime
import json

class DrugReviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection(host='localhost', user='pgx_user', password='pgx_password', database='pgx_db')
        self.init_ui()
        self.load_active_prescriptions()

    def init_ui(self):
        self.setWindowTitle("Drug Review Queue")
        self.resize(1200, 800)
        main_layout = QVBoxLayout(self)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("cssClass", "secondary")
        refresh_btn.clicked.connect(self.load_active_prescriptions)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.prescriptions_tree = QTreeWidget()
        self.prescriptions_tree.setHeaderLabels(["Promise Time", "Rx Store#", "First Name", "Last Name", "Product"])
        self.prescriptions_tree.itemDoubleClicked.connect(self.on_prescription_selected)
        main_layout.addWidget(QLabel("Drug Review Queue:"))
        main_layout.addWidget(self.prescriptions_tree)

        review_label = QLabel("Drug Review Details")
        review_label.setProperty("cssClass", "section-heading")
        main_layout.addWidget(review_label)

        self.drug_review_tree = QTreeWidget()
        self.drug_review_tree.setHeaderLabels(["Drug Name", "Drug Conflict","Gene", "Genetic Variant","Genotype"])
        main_layout.addWidget(self.drug_review_tree)

        approve_btn = QPushButton("Approve Drug")
        approve_btn.setProperty("cssClass", "success")
        approve_btn.clicked.connect(self.approve_drug)
        main_layout.addWidget(approve_btn, alignment=Qt.AlignmentFlag.AlignRight)

        patient_info_layout = QHBoxLayout()
        labels = [
            ("First Name: ", "first_name_label", "first_name_value"),
            ("Last Name: ", "last_name_label", "last_name_value"),
            ("DOB: ", "dob_label", "dob_value"),
        ]

        for text, label_attr, value_attr in labels:
            label = QLabel(text)
            value = QLabel("")
            setattr(self, label_attr, label)
            setattr(self, value_attr, value)
            patient_info_layout.addWidget(label)
            patient_info_layout.addWidget(value)
        patient_info_layout.addStretch()
        main_layout.addLayout(patient_info_layout)

    def load_active_prescriptions(self):
        self.prescriptions_tree.clear()
        self.db.cursor.execute("SELECT * FROM drugreviewqueue LIMIT 30")
        records = self.db.cursor.fetchall()
        for rec in records:
            item = QTreeWidgetItem([
                str(rec['promise_time']),
                rec['rx_store_num'],
                rec['first_name'],
                rec['last_name'],
                rec['product']
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, rec)
            self.prescriptions_tree.addTopLevelItem(item)

    def on_prescription_selected(self, item, column):
        record = item.data(0, Qt.ItemDataRole.UserRole)
        if not record:
            return

        self.selected_record = record

        first_name = record['first_name']
        last_name = record['last_name']
        product = record['product']
        base_drug_name = product.split()[0].lower()

        self.db.cursor.execute(
            "SELECT user_id, Dateofbirth FROM patientsinfo WHERE first_name=%s AND last_name=%s",
            (first_name, last_name)
        )
        patient_record = self.db.cursor.fetchone()
        if not patient_record:
            QMessageBox.warning(self, "Patient Not Found", f"No patient found with name {first_name} {last_name}")
            return

        self.selected_user_id = patient_record['user_id']
        self.dob_value.setText(str(patient_record['Dateofbirth']))
        self.first_name_value.setText(first_name)
        self.last_name_value.setText(last_name)

        self.db.cursor.execute(
            "SELECT drug_name, drug_conflict, gene, genetic_variant, genotype FROM drug_review WHERE user_id=%s AND LOWER(drug_name) = %s",
            (self.selected_user_id, base_drug_name)
        )
        reviews = self.db.cursor.fetchall()

        self.drug_review_tree.clear()
        if reviews:
            for rev in reviews:
                item = QTreeWidgetItem([
                    rev['drug_name'],
                    rev['drug_conflict'],
                    rev['gene'],
                    rev['genetic_variant'],
                    rev['genotype']
                ])
                self.drug_review_tree.addTopLevelItem(item)
        else:
            self.drug_review_tree.addTopLevelItem(QTreeWidgetItem(["No conflicts found for this drug."]))

    def approve_drug(self):
        if not hasattr(self, 'selected_record') or not hasattr(self, 'selected_user_id'):
            QMessageBox.warning(self, "No Selection", "Please select a prescription to approve.")
            return

        rec = self.selected_record

        insert_query = """
            INSERT INTO ProductQueue
            (promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, selected_bottles)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.cursor.execute(insert_query, (
            rec['promise_time'], rec['rx_store_num'], rec['first_name'], rec['last_name'],
            rec['product'], rec['quantity'], rec['delivery'], rec['printed'],
            rec.get('selected_bottles')
        ))
        self.db.connection.commit()

        self.db.cursor.execute(
            "DELETE FROM drugreviewqueue WHERE promise_time=%s AND rx_store_num=%s AND first_name=%s AND last_name=%s AND product=%s",
            (rec['promise_time'], rec['rx_store_num'], rec['first_name'], rec['last_name'], rec['product'])
        )
        self.db.connection.commit()

        # Update status in ActivatedPrescriptions
        update_status_query = """
            UPDATE ActivatedPrescriptions
            SET status = 'ProductQueue'
            WHERE rx_store_num = %s AND first_name = %s AND last_name = %s AND product = %s
        """
        self.db.cursor.execute(update_status_query, (
            rec['rx_store_num'], rec['first_name'], rec['last_name'], rec['product']
        ))
        self.db.connection.commit()

        QMessageBox.information(self, "Success", "Drug approved and moved to ProductQueue.")
        self.drug_review_tree.clear()
        self.load_active_prescriptions()

