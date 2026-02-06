from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal


class OrderSummarySection(QWidget):
    """Order summary display"""

    order_submitted = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("Order Summary")
        group_layout = QVBoxLayout(group)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Medication", "Quantity", "Instructions", "Status"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        group_layout.addWidget(self.summary_table)

        # Total section
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel("Total Items: 0")
        total_layout.addWidget(self.total_label)
        group_layout.addLayout(total_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.submit_btn = QPushButton("Submit Order")
        self.submit_btn.setProperty("cssClass", "success")
        self.submit_btn.clicked.connect(self.submit_order)
        button_layout.addWidget(self.submit_btn)

        self.clear_btn = QPushButton("Clear Order")
        self.clear_btn.setProperty("cssClass", "danger")
        self.clear_btn.clicked.connect(self.clear_order)
        button_layout.addWidget(self.clear_btn)

        group_layout.addLayout(button_layout)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def add_to_summary(self, medication, quantity, instructions):
        """Add item to order summary"""
        row = self.summary_table.rowCount()
        self.summary_table.insertRow(row)

        self.summary_table.setItem(row, 0, QTableWidgetItem(medication))
        self.summary_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.summary_table.setItem(row, 2, QTableWidgetItem(instructions))
        self.summary_table.setItem(row, 3, QTableWidgetItem("Pending"))

        self.update_total()

    def update_total(self):
        """Update total items count"""
        count = self.summary_table.rowCount()
        self.total_label.setText(f"Total Items: {count}")

    def submit_order(self):
        """Submit the order"""
        if self.summary_table.rowCount() == 0:
            return

        order_data = {
            'items': [],
            'total': self.summary_table.rowCount()
        }

        for row in range(self.summary_table.rowCount()):
            item_data = {
                'medication': self.summary_table.item(row, 0).text(),
                'quantity': self.summary_table.item(row, 1).text(),
                'instructions': self.summary_table.item(row, 2).text()
            }
            order_data['items'].append(item_data)

        self.order_submitted.emit(order_data)

    def clear_order(self):
        """Clear all items from order"""
        self.summary_table.setRowCount(0)
        self.update_total()
