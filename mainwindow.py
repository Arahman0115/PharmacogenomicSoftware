from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QMenuBar, QMenu, QApplication
)
from PyQt6.QtGui import QAction
import sys
from config import Theme, DatabaseConfig
from DataBaseConnection import DatabaseConnection

# Import new refactored views
from ui.views.queues.reception_queue import ReceptionQueueView
from ui.views.queues.data_entry_queue import DataEntryQueueView
from ui.views.queues.product_dispensing_queue import ProductDispensingQueueView
from ui.views.queues.drug_review_queue import DrugReviewQueueView
from ui.views.queues.release_queue import ReleaseQueueView
from ui.views.queues.rx_search_view import RxSearchView
from ui.views.queues.verification_queue import VerificationQueueView
from ui.views.patient.patient_search_view import PatientSearchView
from ui.views.prescription.create_order_view import CreateOrderView
from ui.views.prescription.edit_prescription_view import EditPrescriptionView
from ui.views.pgx_dashboard import PgxDashboardView
from ui.views.audit_log_dialog import ensure_audit_table, ensure_rx_number_column

class MainWindow(QMainWindow):
    def __init__(self,db_connection):
        super().__init__()
        self.setWindowTitle("Nexus Controls")
        self.db_connection = db_connection

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        self.queue_widgets = {}

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Menu bar styling handled by global theme (dark slate nav)

        file_menu = QMenu("File", self)
        self.menu_bar.addMenu(file_menu)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        rx_queues_menu = QMenu("Rx Queues", self)
        self.menu_bar.addMenu(rx_queues_menu)
        rx_queues_menu.addAction("Reception", lambda: self.show_queue("reception"))
        rx_queues_menu.addAction("Data Entry", lambda: self.show_queue("product_selection"))
        rx_queues_menu.addAction("Product Dispensing", lambda: self.show_queue("product_dispensing"))
        rx_queues_menu.addAction("Drug Review", lambda: self.show_queue("drug_review"))
        rx_queues_menu.addAction("Verification", lambda: self.show_queue("verification"))
        rx_queues_menu.addAction("Release to Patient", lambda: self.show_queue("release"))
        rx_queues_menu.addAction("Search All Rx", lambda: self.show_queue("rx_lookup"))

        search_menu = QMenu("Search", self)
        self.menu_bar.addMenu(search_menu)
        search_menu.addAction("Patient Management", lambda: self.show_queue("patient_management"))
        activity_menu = QMenu("Activity", self)
        self.menu_bar.addMenu(activity_menu)
        activity_menu.addAction("Create Order", lambda:self.show_queue("create_order"))

        dashboard_menu = QMenu("Dashboard", self)
        self.menu_bar.addMenu(dashboard_menu)
        dashboard_menu.addAction("PGx Dashboard", lambda: self.show_queue("pgx_dashboard"))

        # Ensure audit table exists
        ensure_audit_table(db_connection)
        # Ensure rx_number column exists
        ensure_rx_number_column(db_connection)

        # Show "Search All Rx" view on startup instead of "reception"
        self.show_queue("rx_lookup")
        self.resize(1200, 800)
        self.show()

    def refresh_current_queue(self):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget and hasattr(current_widget, "refresh"):
            current_widget.refresh()

    def instantiate_queue(self, queue_name: str) -> QWidget:
        # Use new refactored views where available
        if queue_name == "reception":
            return ReceptionQueueView(db_connection=self.db_connection)
        elif queue_name == "product_selection":
            return DataEntryQueueView(db_connection=self.db_connection)
        elif queue_name == "product_dispensing":
            return ProductDispensingQueueView(db_connection=self.db_connection)
        elif queue_name == "drug_review":
            return DrugReviewQueueView(db_connection=self.db_connection)
        elif queue_name == "verification":
            return VerificationQueueView(db_connection=self.db_connection)
        elif queue_name == "release":
            return ReleaseQueueView(db_connection=self.db_connection)
        elif queue_name == "rx_lookup":
            return RxSearchView(db_connection=self.db_connection)
        elif queue_name == "patient_management":
            return PatientSearchView(db_connection=self.db_connection)
        elif queue_name == "create_order":
            return CreateOrderView(db_connection=self.db_connection)
        elif queue_name == "edit_prescription":
            return EditPrescriptionView(db_connection=self.db_connection)
        elif queue_name == "pgx_dashboard":
            return PgxDashboardView(db_connection=self.db_connection)
        elif queue_name == "pharmacy_inventory":
            from ExpirationQueueFolder.PharmacyInventoryWidget import PharmacyInventoryWidget
            return PharmacyInventoryWidget(db_connection=self.db_connection)
        else:
            return QWidget()

    def show_queue(self, queue_name: str):
        if queue_name not in self.queue_widgets:
            widget = self.instantiate_queue(queue_name)
            self.queue_widgets[queue_name] = widget
            self.stacked_widget.addWidget(widget)
        self.stacked_widget.setCurrentWidget(self.queue_widgets[queue_name])

    # You will need to add db_connection property to MainWindow or pass db explicitly:

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(Theme.get_application_stylesheet())

    db_connection = DatabaseConnection(**DatabaseConfig.get_connection_params())
    main_win = MainWindow(db_connection=db_connection)
    sys.exit(app.exec())
