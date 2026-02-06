from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QComboBox, QDateEdit, QSpinBox
from PyQt6.QtCore import QDate


class OrderOptionsSection(QWidget):
    """Order options section"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("Order Options")
        form_layout = QFormLayout(group)

        self.delivery_type = QComboBox()
        self.delivery_type.addItems(["Pick Up", "Delivery", "Mail"])
        form_layout.addRow("Delivery Type:", self.delivery_type)

        self.promise_date = QDateEdit()
        self.promise_date.setDate(QDate.currentDate())
        form_layout.addRow("Promise Date:", self.promise_date)

        self.promise_days = QSpinBox()
        self.promise_days.setValue(1)
        self.promise_days.setMinimum(0)
        self.promise_days.setMaximum(30)
        form_layout.addRow("Promise Days:", self.promise_days)

        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Insurance", "Card"])
        form_layout.addRow("Payment Method:", self.payment_method)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def get_options(self):
        """Get current order options"""
        return {
            'delivery_type': self.delivery_type.currentText(),
            'promise_date': self.promise_date.date().toString("yyyy-MM-dd"),
            'promise_days': self.promise_days.value(),
            'payment_method': self.payment_method.currentText()
        }
