from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QGridLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from DataBaseConnection import DatabaseConnection
from datetime import datetime
from random import randint

class ProductQueue(QWidget):
    def __init__(self, db_connection,parent=None):
        super().__init__(parent)

        self.db_connection = db_connection
        self.db_cursor = self.db_connection.cursor()

        main_layout = QVBoxLayout(self)

        # Top filter/search area
        top_frame = QFrame()
        top_frame.setProperty("cssClass", "filter-panel")
        top_layout = QHBoxLayout(top_frame)

        # Find an Rx
        find_rx_frame = QFrame()
        find_rx_frame.setFixedWidth(300)
        find_rx_layout = QVBoxLayout(find_rx_frame)
        find_rx_label = QLabel("Find an Rx")
        find_rx_label.setProperty("cssClass", "section-heading")
        find_rx_text = QLabel("Scan or Enter Rx#:")
        self.scan_entry = QLineEdit()
        find_rx_layout.addWidget(find_rx_label)
        find_rx_layout.addWidget(find_rx_text)
        find_rx_layout.addWidget(self.scan_entry)
        top_layout.addWidget(find_rx_frame)

        # Filter section
        filter_frame = QFrame()
        filter_layout = QGridLayout(filter_frame)

        labels = [
            "Filter By:", "Promise Time:", "Rx #-Store #:", "Store Number:", "Patient Name:"
        ]
        for i, text in enumerate(labels):
            label = QLabel(text)
            if i == 0:
                label.setProperty("cssClass", "section-heading")
            filter_layout.addWidget(label, i, 0, 1, 1)

        self.promise_entry = QLineEdit()
        self.rxstore_entry = QLineEdit()
        self.storenum_entry = QLineEdit()
        self.ptname_entry = QLineEdit()

        # Filter entries styled via global theme

        filter_layout.addWidget(self.promise_entry, 1, 1)
        filter_layout.addWidget(self.rxstore_entry, 2, 1)
        filter_layout.addWidget(self.storenum_entry, 3, 1)
        filter_layout.addWidget(self.ptname_entry, 4, 1)

        top_layout.addWidget(filter_frame, stretch=1)
        main_layout.addWidget(top_frame)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Promise Time", "Rx#-Store#", "Patient name", "Product", "Quantity", "Delivery", "Printed"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table, stretch=3)

        # Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        self.print_selected_btn = QPushButton("Print Selected Order")
        self.print_selected_btn.setProperty("cssClass", "secondary")
        self.print_batch_btn = QPushButton("Print Batch")
        self.print_batch_btn.setProperty("cssClass", "secondary")
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setProperty("cssClass", "ghost")
        self.next_btn = QPushButton("Next")
        self.next_btn.setProperty("cssClass", "primary")
        self.next_btn.clicked.connect(self.next_click)

        buttons_layout.addWidget(self.print_selected_btn)
        buttons_layout.addWidget(self.print_batch_btn)
        buttons_layout.addWidget(self.ok_btn)
        buttons_layout.addWidget(self.next_btn)
        buttons_layout.addStretch()
        main_layout.addWidget(buttons_frame)

        # Patient info
        self.patient_detail_frame = QFrame()
        self.patient_detail_frame.setProperty("cssClass", "card")
        patient_layout = QHBoxLayout(self.patient_detail_frame)

        self.patient_info_label = QLabel()
        patient_layout.addWidget(self.patient_info_label, 1)

        self.middle_canvas = QLabel("Product Info Placeholder")
        self.middle_canvas.setFixedSize(QSize(480, 150))
        self.middle_canvas.setProperty("cssClass", "card")
        patient_layout.addWidget(self.middle_canvas, 1)

        self.right_canvas = QLabel()
        self.right_canvas.setFixedSize(QSize(480, 150))
        self.right_canvas.setProperty("cssClass", "card")
        patient_layout.addWidget(self.right_canvas, 1)

        main_layout.addWidget(self.patient_detail_frame, stretch=2)

        self.load_data()
        self.table.cellDoubleClicked.connect(self.on_row_double_click)

    def refresh(self):
        self.db_connection.connection.commit()
        self.load_data()

    def load_data(self):
        self.db_cursor.execute(
            "SELECT promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed FROM ProductQueue"
        )
        rows = self.db_cursor.fetchall()
        self.table.clearContents()
        self.table.setRowCount(len(rows))

        for row_idx, row_data in enumerate(rows):
            patient_name = f"{row_data.get('first_name', '')} {row_data.get('last_name', '')}".strip()
            promise_time = row_data.get("promise_time")
            if isinstance(promise_time, datetime):
                promise_time = promise_time.strftime("%Y-%m-%d %H:%M:%S")
            self.table.setItem(row_idx, 0, QTableWidgetItem(promise_time or ""))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data.get("rx_store_num") or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(patient_name))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data.get("product") or ""))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row_data.get("quantity") or "")))
            self.table.setItem(row_idx, 5, QTableWidgetItem(row_data.get("delivery") or ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem(row_data.get("printed") or ""))

        self.table.resizeColumnsToContents()

    def on_row_double_click(self, row, column):
        first_last = self.table.item(row, 2).text().split()
        if len(first_last) < 2:
            return
        first_name, last_name = first_last[0], first_last[1]
        self.db_cursor.execute(
            "SELECT * FROM ProductQueue WHERE first_name = %s AND last_name = %s LIMIT 1",
            (first_name, last_name)
        )
        result = self.db_cursor.fetchone()
        if result:
            self.show_patient_info(result)

    def show_patient_info(self, patient_info: dict):
        name = f"{patient_info.get('first_name', '')} {patient_info.get('last_name', '')}".strip()
        product = patient_info.get("product", "N/A")
        quantity = patient_info.get("quantity", "N/A")
        delivery = patient_info.get("delivery", "N/A")

        info_text = (
            f"Name: {name}\n"
            f"Product: {product}\n"
            f"Quantity: {quantity}\n"
            f"Delivery: {delivery}"
        )
        self.patient_info_label.setText(info_text)

        try:
            pixmap = QPixmap("PNGS/am.png").scaled(
                480, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.right_canvas.setPixmap(pixmap)
        except Exception:
            self.right_canvas.setText("Image load failed")

        pill_details = (
            "Pill Name: Amoxicillin 500 MG\n"
            "Pill NDC: 12-3456-789-01\n"
            "Pill Quantity: 30\n"
            "Pill Expiration Date: 2023-08-15\n"
            "Pill Manufacturer: Pfizer\n"
            "Pill Description: Antibiotic\n"
            "Pill Directions: Take 1 tablet by mouth"
        )
        self.middle_canvas.setText(pill_details)
        self.middle_canvas.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.middle_canvas.setWordWrap(True)

    def next_click(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No selection", "Please select a row to process.")
            return
        bin_number = randint(1, 100)  # Simulate a bin number for the example
        row = selected_rows[0].row()

        # Fetch data from the selected row
        promise_time_item = self.table.item(row, 0)
        rx_store_num_item = self.table.item(row, 1)
        first_last_name_item = self.table.item(row, 2)
        product_item = self.table.item(row, 3)
        quantity_item = self.table.item(row, 4)
        delivery_item = self.table.item(row, 5)
        printed_item = self.table.item(row, 6)

        if None in (promise_time_item, rx_store_num_item, first_last_name_item, product_item,
                    quantity_item, delivery_item, printed_item):
            QMessageBox.critical(self, "Error", "Selected row has missing data.")
            return

        # Parse first and last name
        names = first_last_name_item.text().split()
        if len(names) < 2:
            QMessageBox.critical(self, "Error", "Invalid patient name format.")
            return
        first_name, last_name = names[0], names[1]

        try:
            # Insert into ReadyForPickup
            self.db_cursor.execute(
                """INSERT INTO ReadyForPickUp
                (promise_time, rx_store_num, first_name, last_name, product, quantity, delivery, printed, bin_number, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    promise_time_item.text(),
                    rx_store_num_item.text(),
                    first_name,
                    last_name,
                    product_item.text(),
                    int(quantity_item.text()),
                    delivery_item.text(),
                    printed_item.text(),
                    bin_number,
                    "ReadyForPickup"
                )
            )

            # Update status in ActivatedPrescriptions BEFORE deleting from ProductQueue
            update_status_query = """
                UPDATE ActivatedPrescriptions
                SET status = 'ReadyForPickup'
                WHERE rx_store_num = %s AND first_name = %s AND last_name = %s AND product = %s
            """
            self.db_cursor.execute(update_status_query, (
                rx_store_num_item.text(),
                first_name,
                last_name,
                product_item.text()
            ))

            # Delete from ProductQueue
            self.db_cursor.execute(
                """DELETE FROM ProductQueue
                WHERE promise_time = %s AND rx_store_num = %s AND first_name = %s AND last_name = %s
                AND product = %s AND quantity = %s AND delivery = %s AND printed = %s
                LIMIT 1""",
                (
                    promise_time_item.text(),
                    rx_store_num_item.text(),
                    first_name,
                    last_name,
                    product_item.text(),
                    int(quantity_item.text()),
                    delivery_item.text(),
                    printed_item.text()
                )
            )

            self.db_connection.connection.commit()
            QMessageBox.information(self, "Success", "Record moved to ReadyForPickup and status updated.")
            self.load_data()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
