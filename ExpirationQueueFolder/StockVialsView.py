from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QInputDialog, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from collections import defaultdict
from datetime import datetime
import uuid
from PyQt6.QtGui import QIntValidator

class StockVialsView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Stock Bottles Management")
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

        partial_btn = QPushButton("Partial Fill")
        partial_btn.setProperty("cssClass", "warning")
        partial_btn.clicked.connect(self.partial_fill)
        controls_layout.addWidget(partial_btn)

        layout.addLayout(controls_layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(["Medication", "Bottle ID", "Quantity", "Expiration", "Status"])
        self.tree.setSortingEnabled(False)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tree)

    def refresh_data(self):
        self.tree.clear()
        docs = self.db.collection("medications").stream()

        for doc in docs:
            med_data = doc.to_dict()
            med_name = med_data.get("name", doc.id)
            for bottle in med_data.get("stockBottles", []):
                item = QTreeWidgetItem([
                    med_name,
                    bottle["id"],
                    str(bottle["quantity"]),
                    bottle["expiration"],
                    bottle["status"]
                ])
                self.tree.addTopLevelItem(item)

    def dispense_selected(self):
        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select bottles to dispense")
            return

        bottles_by_med = defaultdict(list)
        for item in selected:
            med_name = item.text(0)
            bottle_id = item.text(1)
            quantity = int(item.text(2))
            exp = item.text(3)
            status = item.text(4)
            if status != "sealed":
                QMessageBox.warning(self, "Warning", f"Cannot dispense opened bottle {bottle_id}")
                return
            bottles_by_med[med_name].append({
                "id": bottle_id,
                "expiration": exp,
                "quantity": quantity
            })

        total_bottles = sum(len(b) for b in bottles_by_med.values())
        confirm = QMessageBox.question(self, "Confirm", f"Dispense {total_bottles} bottle(s)?")
        if confirm != QMessageBox.StandardButton.Yes:
            return

        order_id = f"order_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        order_items = []

        for med_name, bottles in bottles_by_med.items():
            order_items.append({
                "medication": med_name,
                "type": "stock",
                "status": "active",
                "timestamp": timestamp,
                "bottles": bottles
            })

        self.db.collection("dispensed_orders").document(order_id).set({
            "order_id": order_id,
            "items": order_items,
            "status": "active",
            "created_at": timestamp
        })

        for med_name, bottles in bottles_by_med.items():
            med_ref = self.db.collection("medications").document(med_name)
            med_doc = med_ref.get()
            if med_doc.exists:
                med_data = med_doc.to_dict()
                stock_bottles = med_data.get("stockBottles", [])
                updated_bottles = [b for b in stock_bottles if b["id"] not in [x["id"] for x in bottles]]
                med_ref.update({"stockBottles": updated_bottles})

        self.refresh_data()
        QMessageBox.information(self, "Success", "Bottles dispensed successfully")

    def partial_fill(self):
        selected = self.tree.selectedItems()
        if not selected or len(selected) > 1:
            QMessageBox.warning(self, "Warning", "Select one sealed bottle for partial fill")
            return

        item = selected[0]
        med_name = item.text(0)
        bottle_id = item.text(1)
        quantity = int(item.text(2))
        exp = item.text(3)
        status = item.text(4)

        if status != "sealed":
            QMessageBox.warning(self, "Warning", "Cannot partially fill an opened bottle")
            return

        dialog = PartialFillDialog(quantity)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            amount = dialog.get_quantity()
            if amount is not None:
                self.process_partial_fill(med_name, bottle_id, amount, quantity, exp)
                self.refresh_data()
                QMessageBox.information(self, "Success", f"Dispensed {amount} pills as amber vial")

    def process_partial_fill(self, med_name, bottle_id, quantity_to_dispense, current_quantity, bottle_exp):
        amber_vial_id = f"av_{uuid.uuid4().hex[:8]}"
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        amber_vial = {
            "id": amber_vial_id,
            "quantity": quantity_to_dispense,
            "expiration": bottle_exp,
            "source": bottle_id,
            "created_at": timestamp
        }

        self.db.collection("dispensed_orders").document(order_id).set({
            "order_id": order_id,
            "items": [{
                "medication": med_name,
                "type": "amber",
                "status": "active",
                "timestamp": timestamp,
                "bottles": [amber_vial]
            }],
            "status": "active",
            "created_at": timestamp
        })

        med_ref = self.db.collection("medications").document(med_name)
        med_doc = med_ref.get()
        if med_doc.exists:
            med_data = med_doc.to_dict()
            stock_bottles = med_data.get("stockBottles", [])

            for bottle in stock_bottles:
                if bottle["id"] == bottle_id:
                    remaining_quantity = current_quantity - quantity_to_dispense
                    if remaining_quantity <= 0:
                        stock_bottles = [b for b in stock_bottles if b["id"] != bottle_id]
                    else:
                        bottle["quantity"] = remaining_quantity
                        bottle["status"] = "opened"
                    break

            med_ref.update({"stockBottles": stock_bottles})


class PartialFillDialog(QDialog):
    def __init__(self, max_quantity):
        super().__init__()
        self.setWindowTitle("Partial Fill")
        self.setFixedSize(300, 150)
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText(f"Enter quantity (max {max_quantity})")
        self.quantity_input.setValidator(QIntValidator(1, max_quantity))
        self.max_quantity = max_quantity

        form = QFormLayout()
        form.addRow("Quantity to dispense:", self.quantity_input)

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.button_box)

    def get_quantity(self):
        try:
            value = int(self.quantity_input.text())
            if 1 <= value <= self.max_quantity:
                return value
        except ValueError:
            pass
        return None
