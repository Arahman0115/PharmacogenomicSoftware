from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
import uuid

class InventoryAmberView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Amber Vials in Inventory")
        title_label.setProperty("cssClass", "page-title")
        layout.addWidget(title_label)

        controls_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("cssClass", "secondary")
        refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(refresh_btn)

        dispense_btn = QPushButton("Dispense Selected")
        dispense_btn.setProperty("cssClass", "primary")
        dispense_btn.clicked.connect(self.dispense_selected)
        controls_layout.addWidget(dispense_btn)

        sort_btn = QPushButton("Sort by Expiration")
        sort_btn.setProperty("cssClass", "secondary")
        sort_btn.clicked.connect(self.sort_by_expiration)
        controls_layout.addWidget(sort_btn)

        layout.addLayout(controls_layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(["Medication", "Vial ID", "Quantity", "Expiration", "Source", "Days Until Expiry"])
        self.tree.setSortingEnabled(False)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree)

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Legend:"))
        legend_layout.addWidget(self.make_legend_label("Expired", "#FFCDD2"))
        legend_layout.addWidget(self.make_legend_label("Expiring Soon (<30 days)", "#FFF3E0"))
        legend_layout.addWidget(self.make_legend_label("Normal", "white"))
        layout.addLayout(legend_layout)

        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label, alignment=Qt.AlignmentFlag.AlignRight)

    def make_legend_label(self, text, bg):
        label = QLabel(text)
        label.setStyleSheet(f"background-color: {bg}; padding: 3px; border-radius: 3px;")
        return label

    def refresh_data(self):
        self.tree.clear()
        total = expired = expiring_soon = 0

        docs = self.db.collection("medications").stream()
        for doc in docs:
            med_data = doc.to_dict()
            med_name = med_data.get("name", doc.id)

            for vial in med_data.get("amberVials", []):
                days_until = self.calculate_days_until_expiry(vial["expiration"])
                if days_until < 0:
                    bg = "#FFCDD2"
                    expired += 1
                elif days_until <= 30:
                    bg = "#FFF3E0"
                    expiring_soon += 1
                else:
                    bg = "white"

                item = QTreeWidgetItem([
                    med_name,
                    vial["id"],
                    str(vial["quantity"]),
                    vial["expiration"],
                    vial.get("source", "Unknown"),
                    str(days_until)
                ])
                for col in range(item.columnCount()):
                    item.setBackground(col, QColor(bg))

                self.tree.addTopLevelItem(item)
                total += 1

        self.update_statistics(total, expired, expiring_soon)

    def convert_to_datetime(self, expiration):
        if isinstance(expiration, datetime):
            return expiration
        if isinstance(expiration, str):
            try:
                return datetime.fromisoformat(expiration)
            except ValueError:
                return None
        return None

    def calculate_days_until_expiry(self, expiration_date):
        exp_datetime = self.convert_to_datetime(expiration_date)
        if exp_datetime is None:
            return 0
        today = datetime.now()
        return (exp_datetime - today).days

    def update_statistics(self, total, expired, expiring_soon):
        self.stats_label.setText(f"Total: {total} | Expired: {expired} | Expiring Soon: {expiring_soon}")

    def sort_by_expiration(self):
        items = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            items.append(item)

        items.sort(key=lambda x: x.text(3))

        self.tree.clear()
        for item in items:
            days = int(item.text(5))
            if days < 0:
                bg = "#FFCDD2"
            elif days <= 30:
                bg = "#FFF3E0"
            else:
                bg = "white"
            for col in range(item.columnCount()):
                item.setBackground(col, QColor(bg))
            self.tree.addTopLevelItem(item)

    def dispense_selected(self):
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a vial to dispense")
            return
        if len(selected) > 1:
            QMessageBox.warning(self, "Warning", "Please select only one vial at a time")
            return

        item = selected[0]
        med_name = item.text(0)
        vial_id = item.text(1)
        quantity = int(item.text(2))
        expiration = item.text(3)

        if self.calculate_days_until_expiry(expiration) < 0:
            proceed = QMessageBox.question(self, "Warning", "This vial is expired. Continue with dispense?")
            if proceed != QMessageBox.StandardButton.Yes:
                return

        confirm = QMessageBox.question(self, "Confirm", f"Dispense {quantity} pills from vial {vial_id}?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self.process_amber_dispense(med_name, vial_id, quantity, expiration)
        self.refresh_data()
        QMessageBox.information(self, "Success", "Amber vial dispensed successfully")

    def process_amber_dispense(self, med_name, vial_id, quantity, expiration):
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        item = {
            "medication": med_name,
            "type": "amber",
            "amber_vial_id": vial_id,
            "quantity": quantity,
            "expiration": expiration,
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        order_doc = {
            "order_id": order_id,
            "items": [item]
        }
        self.db.collection("dispensed_orders").document(order_id).set(order_doc)

        med_ref = self.db.collection("medications").document(med_name)
        med_doc = med_ref.get()
        if med_doc.exists:
            med_data = med_doc.to_dict()
            amber_vials = med_data.get("amberVials", [])
            updated_vials = [v for v in amber_vials if v["id"] != vial_id]
            med_ref.update({"amberVials": updated_vials})

    def get_expiring_vials(self, days=30):
        expiring = []
        docs = self.db.collection("medications").stream()
        for doc in docs:
            med_data = doc.to_dict()
            med_name = med_data.get("name", doc.id)
            for vial in med_data.get("amberVials", []):
                days_left = self.calculate_days_until_expiry(vial["expiration"])
                if 0 <= days_left <= days:
                    expiring.append({
                        "medication": med_name,
                        "vial_id": vial["id"],
                        "quantity": vial["quantity"],
                        "expiration": vial["expiration"],
                        "days_until_expiry": days_left
                    })
        return expiring
