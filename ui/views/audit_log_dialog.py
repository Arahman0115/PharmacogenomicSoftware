"""Audit Log - Prescription audit trail for HIPAA compliance"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


def ensure_audit_table(db_connection):
    """Create the prescription_audit_log table if it doesn't exist"""
    try:
        cursor = db_connection.cursor
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescription_audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prescription_id INT NOT NULL,
                from_status VARCHAR(100),
                to_status VARCHAR(100) NOT NULL,
                action VARCHAR(255) NOT NULL,
                performed_by VARCHAR(100) DEFAULT 'pharmacist',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_prescription_id (prescription_id),
                INDEX idx_created_at (created_at)
            )
        """)
        db_connection.connection.commit()
    except Exception as e:
        print(f"Warning: Could not create audit table: {e}")


def log_transition(db_connection, prescription_id, from_status, to_status, action, performed_by="pharmacist", notes=None):
    """Log a prescription status transition for audit trail"""
    try:
        cursor = db_connection.cursor
        cursor.execute("""
            INSERT INTO prescription_audit_log
            (prescription_id, from_status, to_status, action, performed_by, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (prescription_id, from_status, to_status, action, performed_by, notes))
        # Don't commit here - let the caller handle the transaction
    except Exception as e:
        print(f"Warning: Could not log audit entry: {e}")


class AuditLogDialog(QDialog):
    """Dialog showing the audit trail for a specific prescription"""

    def __init__(self, db_connection, prescription_id, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.prescription_id = prescription_id

        self.setWindowTitle(f"Audit Log - Rx #{prescription_id}")
        self.setGeometry(100, 100, 800, 500)
        self.init_ui()
        self.load_log()

    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        title = QLabel(f"Prescription Audit Trail - Rx #{self.prescription_id}")
        title.setProperty("cssClass", "section-heading")
        layout.addWidget(title)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "Timestamp", "From Status", "To Status", "Action", "Performed By", "Notes"
        ])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setShowGrid(False)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.log_table)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "ghost")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def load_log(self):
        """Load audit log entries for this prescription"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                SELECT created_at, from_status, to_status, action, performed_by, notes
                FROM prescription_audit_log
                WHERE prescription_id = %s
                ORDER BY created_at ASC
            """, (self.prescription_id,))
            entries = cursor.fetchall()

            self.log_table.setRowCount(len(entries))
            for i, entry in enumerate(entries):
                timestamp = str(entry.get('created_at', ''))
                self.log_table.setItem(i, 0, QTableWidgetItem(timestamp))
                self.log_table.setItem(i, 1, QTableWidgetItem(entry.get('from_status', '') or ''))
                self.log_table.setItem(i, 2, QTableWidgetItem(entry.get('to_status', '')))
                self.log_table.setItem(i, 3, QTableWidgetItem(entry.get('action', '')))
                self.log_table.setItem(i, 4, QTableWidgetItem(entry.get('performed_by', '')))
                self.log_table.setItem(i, 5, QTableWidgetItem(entry.get('notes', '') or ''))

            if not entries:
                self.log_table.setRowCount(1)
                self.log_table.setItem(0, 0, QTableWidgetItem("No audit entries found"))
                self.log_table.setSpan(0, 0, 1, 6)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit log: {e}")
