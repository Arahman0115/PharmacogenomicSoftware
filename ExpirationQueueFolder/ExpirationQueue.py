import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox,
    QTextEdit, QTreeWidget, QTreeWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime


class ExpirationQueueView(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.days_var = "90"
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("Expiration Queue")
        title.setProperty("cssClass", "page-title")
        layout.addWidget(title)

        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("cssClass", "secondary")
        self.refresh_btn.clicked.connect(self.refresh_data)
        controls.addWidget(self.refresh_btn)

        self.remove_btn = QPushButton("Remove Expired")
        self.remove_btn.setProperty("cssClass", "danger")
        self.remove_btn.clicked.connect(self.remove_expired)
        controls.addWidget(self.remove_btn)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Show items expiring within:")
        self.days_combo = QComboBox()
        self.days_combo.addItems(["7", "14", "30", "60", "90", "180", "365"])
        self.days_combo.setCurrentText("90")
        self.days_combo.currentTextChanged.connect(lambda: self.refresh_data())
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.days_combo)
        filter_layout.addWidget(QLabel("days"))
        filter_layout.addStretch()
        controls.addLayout(filter_layout)

        layout.addLayout(controls)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(7)
        self.tree.setHeaderLabels(
            ["Type", "Medication", "Item ID", "Quantity", "Expiration", "Days Until Expiry", "Priority"]
        )
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tree)

        self.stats_label = QLabel("")
        layout.addWidget(self.stats_label)

        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        layout.addWidget(self.alerts_text)

    def connect_db(self):
        return sqlite3.connect(self.db_path)

    def refresh_data(self):
        self.tree.clear()
        filter_days = int(self.days_combo.currentText())
        all_items = []
        expired_count = critical_count = warning_count = normal_count = 0

        conn = self.connect_db()
        cursor = conn.cursor()

        # Query stock bottles
        cursor.execute("""
            SELECT 'Stock' as type, m.name, sb.id, sb.quantity, sb.expiration
            FROM stock_bottles sb
            JOIN medications m ON sb.medication_id = m.id
        """)
        stock_rows = cursor.fetchall()

        # Query amber vials
        cursor.execute("""
            SELECT 'Amber' as type, m.name, av.id, av.quantity, av.expiration
            FROM amber_vials av
            JOIN medications m ON av.medication_id = m.id
        """)
        amber_rows = cursor.fetchall()

        conn.close()

        for type_, med_name, item_id, quantity, expiration in stock_rows + amber_rows:
            days_until_expiry = self.calculate_days_until_expiry(expiration)
            if days_until_expiry <= filter_days:
                priority, tag = self.get_priority_and_tag(days_until_expiry)
                all_items.append({
                    "type": type_,
                    "medication": med_name,
                    "item_id": item_id,
                    "quantity": quantity,
                    "expiration": expiration,
                    "days_until_expiry": days_until_expiry,
                    "priority": priority,
                    "tag": tag
                })

                if days_until_expiry < 0:
                    expired_count += 1
                elif days_until_expiry <= 7:
                    critical_count += 1
                elif days_until_expiry <= 90:
                    warning_count += 1
                else:
                    normal_count += 1

        for item in sorted(all_items, key=lambda x: x["days_until_expiry"]):
            twi = QTreeWidgetItem([
                item["type"], item["medication"], item["item_id"],
                str(item["quantity"]), item["expiration"],
                str(item["days_until_expiry"]), item["priority"]
            ])
            color = self.get_color_by_tag(item["tag"])
            for col in range(7):
                twi.setForeground(col, color)
            self.tree.addTopLevelItem(twi)

        self.update_statistics(expired_count, critical_count, warning_count, normal_count)
        self.update_alerts(expired_count, critical_count, warning_count)

    def calculate_days_until_expiry(self, exp):
        try:
            dt = datetime.strptime(exp, "%Y-%m-%d")
            return (dt - datetime.now()).days
        except Exception:
            return 0

    def get_priority_and_tag(self, days):
        if days < 0:
            return "EXPIRED", "expired"
        elif days <= 7:
            return "CRITICAL", "critical"
        elif days <= 90:
            return "Due to Pull", "warning"
        else:
            return "NORMAL", "normal"

    def get_color_by_tag(self, tag):
        return {
            "expired": QColor("#B71C1C"),
            "critical": QColor("#E65100"),
            "warning": QColor("#F57C00"),
            "normal": QColor("#2E7D32")
        }.get(tag, QColor("#000000"))

    def update_statistics(self, expired, critical, warning, normal):
        total = expired + critical + warning + normal
        self.stats_label.setText(
            f"Total: {total} | Expired: {expired} | Critical: {critical} | Due to Pull: {warning} | Normal: {normal}"
        )

    def update_alerts(self, expired, critical, warning):
        alerts = []
        if expired > 0:
            alerts.append(f"🚨 {expired} items have EXPIRED and should be removed immediately!")
        if critical > 0:
            alerts.append(f"⚠️ {critical} items expire within 7 days.")
        if warning > 0:
            alerts.append(f"💡 {warning} items expire within 90 days.")
        if not alerts:
            alerts.append("✅ No urgent expiration alerts.")
        self.alerts_text.setPlainText("\n".join(alerts))

    def remove_expired(self):
        conn = self.connect_db()
        cursor = conn.cursor()

        # Remove expired stock bottles
        cursor.execute("""
            DELETE FROM stock_bottles WHERE expiration < DATE('now')
        """)
        removed_stock = cursor.rowcount

        # Remove expired amber vials
        cursor.execute("""
            DELETE FROM amber_vials WHERE expiration < DATE('now')
        """)
        removed_amber = cursor.rowcount

        conn.commit()
        conn.close()

        removed = removed_stock + removed_amber

        if removed > 0:
            confirm = QMessageBox.question(
                self, "Confirm Removal",
                f"{removed} expired items removed. Refresh now?"
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.refresh_data()
                QMessageBox.information(self, "Removed", f"{removed} expired items removed.")
        else:
            QMessageBox.information(self, "Info", "No expired items to remove.")
