from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QSizePolicy
)
import mysql.connector
from ReleaseToPatientWidget import ReleaseToPatientWidget
from PyQt6 import QtWidgets
class RxSearchWidget(QWidget):
    def __init__(self,db_connection):
        super().__init__()
        layout = QVBoxLayout(self)
        self.db_connection = db_connection
        self.label = QLabel("Enter patient name (use ',firstname' to search by first name only):")
        self.entry = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.setProperty("cssClass", "primary")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setProperty("cssClass", "secondary")
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Promise Time", "Rx#-Store#", "Patient Name", "Product", "Quantity", "Delivery", "Status"
        ])

        # Make table stretch across the available width
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.cellClicked.connect(self.open_release_window)


        self.search_button.clicked.connect(self.search_patient)
        self.refresh_button.clicked.connect(self.refresh_table)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.refresh_button)

        layout.addWidget(self.label)
        layout.addWidget(self.entry)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)

        self.refresh_table()

    def search_patient(self):
        query = self.entry.text().strip()
        if not query:
            self.refresh_table()
            return

        if query.startswith(","):
            first_name = query[1:].strip()
            last_name = None
        else:
            parts = query.split(",", 1)
            last_name = parts[0].strip()
            first_name = parts[1].strip() if len(parts) > 1 else None

        self.load_data(last_name, first_name)

    def refresh_table(self):
        self.entry.clear()
        self.table.setRowCount(0)
    def open_release_window(self, row, column):
        name_item = self.table.item(row, 2)
        if name_item:
            last_name, first_name = [s.strip() for s in name_item.text().split(",")]
            self.release_window = ReleaseToPatientWidget(first_name, last_name,db_connection=self.db_connection)
            self.release_window.show()



    def load_data(self, last_name=None, first_name=None):
        try:
            cursor = self.db_connection.cursor  # <-- use the existing cursor

            sql = """
                SELECT promise_time, rx_store_num, last_name, first_name, product, quantity, delivery, status
                FROM ActivatedPrescriptions
            """
            conditions = []
            params = []

            if last_name and first_name:
                conditions.append("last_name LIKE %s AND first_name LIKE %s")
                params.extend([f"%{last_name}%", f"%{first_name}%"])
            elif last_name:
                conditions.append("last_name LIKE %s")
                params.append(f"%{last_name}%")
            elif first_name:
                conditions.append("first_name LIKE %s")
                params.append(f"%{first_name}%")

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()

            self.table.setRowCount(0)
            for row_data in results:
                row_index = self.table.rowCount()
                self.table.insertRow(row_index)
                patient_name = f"{row_data.get('last_name','')}, {row_data.get('first_name','')}"
                data_to_display = [
                    row_data.get('promise_time', ''),
                    row_data.get('rx_store_num', ''),
                    patient_name,
                    row_data.get('product', ''),
                    row_data.get('quantity', ''),
                    row_data.get('delivery', ''),
                    row_data.get('status', ''),
                ]
                for col_index, item in enumerate(data_to_display):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(item)))

        except mysql.connector.Error as e:
            print(f"Database error: {e}")  # or log it
            # Optional: show in UI instead of crashing
            self.table.setRowCount(0)
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))

        except KeyError as ke:
            print(f"Column missing: {ke}")
            # Optional: show placeholder values in the table instead of crashing

        finally:
            # Do not close the cursor if you're using a persistent cursor in your DatabaseConnection class
            # cursor.close()  # only close if you created it locally
            pass
