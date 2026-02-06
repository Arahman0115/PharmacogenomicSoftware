from PyQt6.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout
)

from StockVialsView import StockVialsView
from InUseAmberView import InUseAmberView
from ExpirationQueue import ExpirationQueueView
from InventoryAmberView import InventoryAmberView

class PharmacyInventoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Styled via global theme

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab containers
        self.stock_tab = QWidget()
        self.inventory_tab = QWidget()
        self.in_use_tab = QWidget()
        self.expiration_tab = QWidget()

        self.tabs.addTab(self.stock_tab, "Stock Vials")
        self.tabs.addTab(self.inventory_tab, "Amber Vials in Inventory")
        self.tabs.addTab(self.in_use_tab, "In Use")
        self.tabs.addTab(self.expiration_tab, "Expiration Queue")

        self.setup_views()

    def setup_views(self):
        stock_layout = QVBoxLayout()
        stock_layout.addWidget(StockVialsView())  # no db passed
        self.stock_tab.setLayout(stock_layout)

        inventory_layout = QVBoxLayout()
        inventory_layout.addWidget(InventoryAmberView())  # no db passed
        self.inventory_tab.setLayout(inventory_layout)

        in_use_layout = QVBoxLayout()
        in_use_layout.addWidget(InUseAmberView())  # no db passed
        self.in_use_tab.setLayout(in_use_layout)

        expiration_layout = QVBoxLayout()
        expiration_layout.addWidget(ExpirationQueueView())  # no db passed
        self.expiration_tab.setLayout(expiration_layout)
