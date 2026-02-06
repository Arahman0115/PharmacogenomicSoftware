from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox
from ui.components import PatientSearchWidget, PrescriptionTable
from .components.refill_section import RefillSection
from .components.order_options_section import OrderOptionsSection
from .components.order_summary_section import OrderSummarySection
from datetime import datetime


class CreateOrderView(QMainWindow):
    """Order creation dialog"""

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.selected_patient = None
        self.setWindowTitle("Create New Rx Order")
        self.setGeometry(50, 50, 1400, 900)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Patient search
        self.patient_search = PatientSearchWidget(db_connection=self.db_connection)
        self.patient_search.patient_selected.connect(self.on_patient_selected)
        layout.addWidget(self.patient_search, 2)

        # Prescription options (refill or new)
        self.refill_section = RefillSection(db_connection=self.db_connection)
        layout.addWidget(self.refill_section, 1)

        # Order options
        self.order_options = OrderOptionsSection()
        layout.addWidget(self.order_options, 1)

        # Order summary
        self.order_summary = OrderSummarySection()
        self.order_summary.order_submitted.connect(self.submit_order)
        layout.addWidget(self.order_summary, 2)

        self.setCentralWidget(central_widget)

    def on_patient_selected(self, patient_data):
        """Handle patient selection"""
        self.selected_patient = patient_data
        if patient_data:
            user_id = patient_data.get('user_id')
            self.refill_section.load_refills(user_id)

    def submit_order(self, order_data):
        """Submit the order to database"""
        if not self.selected_patient:
            QMessageBox.warning(self, "Error", "Please select a patient first")
            return

        try:
            user_id = self.selected_patient.get('user_id')
            options = self.order_options.get_options()

            # Insert into ProductSelectionQueue
            for item in order_data['items']:
                insert_query = """
                    INSERT INTO ProductSelectionQueue
                    (user_id, product, quantity, instructions, delivery, promise_time, status, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())
                """
                self.db_connection.cursor.execute(
                    insert_query,
                    (
                        user_id,
                        item['medication'],
                        item['quantity'],
                        item['instructions'],
                        options['delivery_type'],
                        options['promise_date']
                    )
                )

            self.db_connection.connection.commit()
            QMessageBox.information(self, "Success", f"Order created with {order_data['total']} items")
            self.order_summary.clear_order()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create order: {e}")
            self.db_connection.connection.rollback()
