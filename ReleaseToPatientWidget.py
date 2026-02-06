from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QHeaderView, QSizePolicy, QMessageBox
)
import mysql.connector
from datetime import datetime


class ReleaseToPatientWidget(QWidget):
    def __init__(self, first_name, last_name,db_connection):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.db_connection = db_connection
        self.setWindowTitle(f"Release to Patient [{self.first_name} {self.last_name}]")

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Product", "Rx Number", "Status", "Bin", "Patient Pay", "Payment"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel Item")
        self.order_details_button = QPushButton("Order Details")
        self.print_options_button = QPushButton("Print Options")
        self.patient_profile_button = QPushButton("Patient Profile")
        self.historical_dur_button = QPushButton("Historical DUR")
        self.bin_assignment_button = QPushButton("Bin Assignment")
        self.edit_third_party_button = QPushButton("Edit Third Party")
        self.release_button = QPushButton("Release")
        self.release_all_button = QPushButton("Release All")
        self.decline_button = QPushButton("Decline")
        self.close_button = QPushButton("Close")

        # Contextual buttons (ghost/secondary)
        self.cancel_button.setProperty("cssClass", "ghost")
        self.order_details_button.setProperty("cssClass", "ghost")
        self.print_options_button.setProperty("cssClass", "ghost")
        self.patient_profile_button.setProperty("cssClass", "secondary")
        self.historical_dur_button.setProperty("cssClass", "ghost")
        self.bin_assignment_button.setProperty("cssClass", "ghost")
        self.edit_third_party_button.setProperty("cssClass", "ghost")

        for btn in [
            self.cancel_button, self.order_details_button, self.print_options_button,
            self.patient_profile_button, self.historical_dur_button, self.bin_assignment_button,
            self.edit_third_party_button,
        ]:
            self.button_layout.addWidget(btn)

        self.button_layout.addStretch()

        # Action buttons (success/danger/ghost)
        self.release_button.setProperty("cssClass", "success")
        self.release_all_button.setProperty("cssClass", "success")
        self.decline_button.setProperty("cssClass", "danger")
        self.close_button.setProperty("cssClass", "ghost")

        for btn in [self.release_button, self.release_all_button, self.decline_button, self.close_button]:
            self.button_layout.addWidget(btn)

        self.layout.addLayout(self.button_layout)

        self.release_button.clicked.connect(self.release_selected_prescription)
        self.release_all_button.clicked.connect(self.release_all_prescriptions)

        self.load_patient_data()

    def release_selected_prescription(self):
        selected_range = self.table.selectedItems()
        if not selected_range:
            QMessageBox.warning(self, "No Selection", "Please select a prescription to release.")
            return

        row = selected_range[0].row()
        product = self.table.item(row, 0).text()
        rx_number = self.table.item(row, 1).text()
        bin_number = self.table.item(row, 3).text()
        release_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.db_connection
        cursor = conn.cursor

        cursor.execute("""
            SELECT id, rx_store_num, quantity, delivery FROM ReadyForPickUp
            WHERE first_name = %s AND last_name = %s AND product = %s
            LIMIT 1
        """, (self.first_name, self.last_name, product))

        record = cursor.fetchone()

        if not record:
            QMessageBox.critical(self, "Error", "Prescription record not found.")
            cursor.close()
            conn.close()
            return

        cursor.execute("""
            INSERT INTO FinishedTransactions (
                release_time, rx_store_num, first_name, last_name, product, quantity, delivery, bin_number
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            release_time, record['rx_store_num'], self.first_name, self.last_name,
            product, record['quantity'], record['delivery'], bin_number
        ))

        cursor.execute("DELETE FROM ReadyForPickUp WHERE id = %s", (record['id'],))
        cursor.execute("DELETE FROM ActivatedPrescriptions WHERE prescription_id = %s", (record['prescription_id'],))

        conn.commit()


        QMessageBox.information(self, "Release", f"Prescription {rx_number} for {product} released successfully.")
        self.load_patient_data()

    def load_patient_data(self):
        cursor = self.db_connection.cursor  # ← already a dict cursor

        cursor.execute("""
            SELECT product, prescription_id, status, bin_number, patient_pay, payment
            FROM ReadyForPickUp
            WHERE first_name = %s AND last_name = %s
        """, (self.first_name, self.last_name))

        results = cursor.fetchall()

        self.table.setRowCount(0)

        for row_data in results:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)

            data = [
                row_data['product'],
                row_data['prescription_id'],
                row_data['status'],
                row_data['bin_number'],
                row_data['patient_pay'],
                row_data['payment'],
            ]

            for col, value in enumerate(data):
                self.table.setItem(row_index, col, QTableWidgetItem(str(value)))



    def release_all_prescriptions(self):
        conn = self.db_connection
        cursor = conn.cursor

        cursor.execute("""
            SELECT * FROM ReadyForPickUp
            WHERE first_name = %s AND last_name = %s
        """, (self.first_name, self.last_name))
        records = cursor.fetchall()

        if not records:
            QMessageBox.information(self, "No Prescriptions", "There are no prescriptions to release.")
            cursor.close()
            conn.close()
            return

        release_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for record in records:
            cursor.execute("""
                INSERT INTO FinishedTransactions (
                    release_time, rx_store_num, first_name, last_name,
                    product, quantity, delivery, bin_number
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                release_time, record['rx_store_num'], record['first_name'], record['last_name'],
                record['product'], record['quantity'], record['delivery'], record['bin_number']
            ))
            cursor.execute("DELETE FROM ReadyForPickUp WHERE prescription_id = %s", (record['prescription_id'],))
        self.db_connection.connection.commit()


        QMessageBox.information(self, "Released", f"All prescriptions released for {self.first_name} {self.last_name}.")
        self.load_patient_data()
