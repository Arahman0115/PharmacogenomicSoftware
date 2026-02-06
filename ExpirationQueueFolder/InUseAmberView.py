from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime


class InUseAmberView(QWidget):
    def __init__(self, db_connection=None):
        super().__init__()
        self.db = db_connection
        self.all_dispensed_items = []
        self.create_widgets()
        if self.db:
            self.refresh_data()

    def create_widgets(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Dispensed Items (In Use)")
        title_label.setProperty("cssClass", "page-title")
        layout.addWidget(title_label)

        # Controls row
        controls_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("cssClass", "secondary")
        refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(refresh_btn)

        return_btn = QPushButton("Return Selected")
        return_btn.setProperty("cssClass", "danger")
        return_btn.clicked.connect(self.return_selected)
        controls_layout.addWidget(return_btn)

        controls_layout.addStretch()

        # Status filter
        controls_layout.addWidget(QLabel("Status:"))
        self.status_group = QButtonGroup(self)
        self.status_active_radio = QRadioButton("Active")
        self.status_returned_radio = QRadioButton("Returned")
        self.status_all_radio = QRadioButton("All")
        self.status_active_radio.setChecked(True)

        self.status_group.addButton(self.status_active_radio)
        self.status_group.addButton(self.status_returned_radio)
        self.status_group.addButton(self.status_all_radio)

        for radio in [self.status_active_radio, self.status_returned_radio, self.status_all_radio]:
            radio.toggled.connect(self.apply_filter)
            controls_layout.addWidget(radio)

        # Bottle type filter
        controls_layout.addWidget(QLabel("Type:"))
        self.type_group = QButtonGroup(self)
        self.type_all_radio = QRadioButton("All")
        self.type_stock_radio = QRadioButton("Stock Bottles")
        self.type_amber_radio = QRadioButton("Amber Vials")
        self.type_all_radio.setChecked(True)

        self.type_group.addButton(self.type_all_radio)
        self.type_group.addButton(self.type_stock_radio)
        self.type_group.addButton(self.type_amber_radio)

        for radio in [self.type_all_radio, self.type_stock_radio, self.type_amber_radio]:
            radio.toggled.connect(self.apply_filter)
            controls_layout.addWidget(radio)

        layout.addLayout(controls_layout)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)
        self.tree.setHeaderLabels(
            ["Order ID", "Type", "Medication", "Item ID", "Quantity", "Expiration", "Dispensed Date", "Status"]
        )
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tree)

        # Legend and stats
        bottom_layout = QHBoxLayout()

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Legend:"))
        legend_layout.addWidget(self._make_legend_label("Stock Bottles", "#EBF2FA"))
        legend_layout.addWidget(self._make_legend_label("Amber Vials", "#FEF3C7"))
        legend_layout.addWidget(self._make_legend_label("Returned", "#C6F6D5"))
        legend_layout.addStretch()
        bottom_layout.addLayout(legend_layout)

        self.stats_label = QLabel("")
        self.stats_label.setProperty("cssClass", "text-muted")
        bottom_layout.addWidget(self.stats_label)

        layout.addLayout(bottom_layout)

    def _make_legend_label(self, text, bg_color):
        label = QLabel(text)
        label.setStyleSheet(f"background-color: {bg_color}; padding: 3px; border-radius: 3px;")
        return label

    def _get_status_filter(self):
        if self.status_active_radio.isChecked():
            return "active"
        elif self.status_returned_radio.isChecked():
            return "returned"
        return "all"

    def _get_type_filter(self):
        if self.type_stock_radio.isChecked():
            return "stock"
        elif self.type_amber_radio.isChecked():
            return "amber"
        return "all"

    def refresh_data(self):
        if not self.db:
            return

        self.tree.clear()
        self.all_dispensed_items.clear()

        query = """
            SELECT id, order_id, medication_name, bottle_type, quantity, expiration, dispensed_date, status
            FROM ReadyForPickUp
        """
        self.db.cursor.execute(query)
        rows = self.db.cursor.fetchall()

        for row in rows:
            item = {
                "_doc_id": row["id"],
                "_order_id": row["order_id"],
                "medication": row["medication_name"],
                "type": row["bottle_type"],
                "quantity": row["quantity"],
                "expiration": row["expiration"].strftime("%Y-%m-%d") if row["expiration"] else "Unknown",
                "dispensed_date": row["dispensed_date"].strftime("%Y-%m-%d %H:%M") if row["dispensed_date"] else "Unknown",
                "status": row["status"]
            }
            self.all_dispensed_items.append(item)

        self.apply_filter()

    def apply_filter(self):
        self.tree.clear()

        filter_type = self._get_type_filter()
        status_filter = self._get_status_filter()

        active = returned = stock = amber = 0
        order_parents = {}

        for item in self.all_dispensed_items:
            if filter_type != "all" and item.get("type") != filter_type:
                continue
            if status_filter != "all" and item.get("status", "").lower() != status_filter:
                continue

            order_id = item["_order_id"]
            if order_id not in order_parents:
                parent_item = QTreeWidgetItem([str(order_id)])
                self.tree.addTopLevelItem(parent_item)
                order_parents[order_id] = parent_item

            status = item.get("status", "").lower()
            item_type = item.get("type", "").lower()

            if status == "returned":
                returned += 1
            else:
                active += 1

            if item_type == "stock":
                stock += 1
            elif item_type == "amber":
                amber += 1

            child = QTreeWidgetItem([
                "",  # Order ID column (empty for children)
                item_type.title(),
                item.get("medication", "Unknown"),
                str(item["_doc_id"]),
                str(item.get("quantity", 0)),
                item.get("expiration", "Unknown"),
                item.get("dispensed_date", "Unknown"),
                status.title()
            ])

            # Color coding by type/status
            if status == "returned":
                bg = QColor("#C6F6D5")
            elif item_type == "stock":
                bg = QColor("#EBF2FA")
            elif item_type == "amber":
                bg = QColor("#FEF3C7")
            else:
                bg = QColor("white")

            for col in range(child.columnCount()):
                child.setBackground(col, bg)

            order_parents[order_id].addChild(child)

        self.update_statistics(active, returned, stock, amber)

    def update_statistics(self, active, returned, stock, amber):
        self.stats_label.setText(
            f"Active: {active} | Returned: {returned} | Stock: {stock} | Amber: {amber}"
        )

    def return_selected(self):
        if not self.db:
            return

        selected = self.tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Select an order to return")
            return

        item = selected[0]
        # Ensure it's a top-level item (order parent)
        if item.parent() is not None:
            QMessageBox.warning(self, "Warning", "Return one entire order at a time (select the order row)")
            return

        order_id = item.text(0)

        reply = QMessageBox.question(
            self, "Confirm",
            f"Return all active items in order '{order_id}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        update_query = """
            UPDATE ReadyForPickUp
            SET status = 'returned'
            WHERE order_id = %s AND status = 'active'
        """
        self.db.cursor.execute(update_query, (order_id,))
        self.db.connection.commit()

        self.refresh_data()
        QMessageBox.information(self, "Success", f"Order '{order_id}' returned.")
