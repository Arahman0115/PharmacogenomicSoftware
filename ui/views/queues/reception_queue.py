from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateTimeEdit,
    QComboBox, QMessageBox, QPushButton, QDialog, QGroupBox,
    QFormLayout, QFrame
)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QColor
from .base_queue_view import BaseQueueView
from config import Theme


class ReceptionQueueView(BaseQueueView):
    """Reception queue view - initial intake from ProductSelectionQueue table"""

    TABLE_NAME = "ProductSelectionQueue"
    WINDOW_TITLE = "Reception Queue"
    COLUMNS = [
        "Promise Time", "Rx# - Store#", "Patient Name",
        "Patient ID", "New / Refill", "Delivery", "Lock"
    ]

    def __init__(self, db_connection, parent=None):
        self.promise_date = None
        self.promise_time = None
        self.rx_store = None
        self.store_number = None
        self.patient_name = None
        self.patient_id = None
        self.results_label = None

        super().__init__(db_connection, parent)

    def create_filters(self, parent_layout):
        """Create filter controls for reception queue"""
        filter_label = QLabel("Filter By:")
        parent_layout.addWidget(filter_label)

        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel("Promise Time:"))
        self.promise_date = QDateTimeEdit()
        self.promise_date.setDateTime(QDateTime.currentDateTime())
        self.promise_date.setDisplayFormat("MM/dd/yyyy")
        row1_layout.addWidget(self.promise_date)
        row1_layout.addWidget(QLabel("at"))

        self.promise_time = QComboBox()
        self.promise_time.addItems(["AM", "PM"])
        row1_layout.addWidget(self.promise_time)
        row1_layout.addStretch()
        parent_layout.addLayout(row1_layout)

        row2_layout = QHBoxLayout()
        row2_layout.addWidget(QLabel("Rx# - Store#:"))
        self.rx_store = QLineEdit()
        self.rx_store.setMinimumWidth(300)
        row2_layout.addWidget(self.rx_store)
        row2_layout.addStretch()
        parent_layout.addLayout(row2_layout)

        row3_layout = QHBoxLayout()
        row3_layout.addWidget(QLabel("Store Number:"))
        self.store_number = QLineEdit()
        self.store_number.setMinimumWidth(300)
        row3_layout.addWidget(self.store_number)
        row3_layout.addStretch()
        parent_layout.addLayout(row3_layout)

        row4_layout = QHBoxLayout()
        row4_layout.addWidget(QLabel("Patient Name:"))
        self.patient_name = QLineEdit()
        self.patient_name.setPlaceholderText("LAST, FIRST")
        self.patient_name.setMinimumWidth(200)
        row4_layout.addWidget(self.patient_name)

        row4_layout.addWidget(QLabel("Patient ID:"))
        self.patient_id = QLineEdit()
        self.patient_id.setMinimumWidth(200)
        row4_layout.addWidget(self.patient_id)
        row4_layout.addStretch()
        parent_layout.addLayout(row4_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        filter_btn = QPushButton("Filter")
        filter_btn.setProperty("cssClass", "primary")
        filter_btn.clicked.connect(self.apply_filters_clicked)
        button_layout.addWidget(filter_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setProperty("cssClass", "secondary")
        reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_btn)

        parent_layout.addLayout(button_layout)

    def load_data(self):
        """Load reception queue data from ProductSelectionQueue table"""
        if not self.db_connection:
            return

        try:
            query = """
                SELECT
                    promise_time,
                    rx_store_num,
                    CONCAT(first_name, ', ', last_name) as patient_name,
                    id as patient_id,
                    CASE
                        WHEN refills > 0 THEN 'Refill'
                        ELSE 'New'
                    END as new_refill,
                    COALESCE(delivery, 'Waiting') as delivery,
                    '' as lock_status,
                    first_name,
                    last_name,
                    product,
                    quantity,
                    instructions,
                    refills,
                    id,
                    user_id,
                    status
                FROM ProductSelectionQueue
                WHERE status = 'pending'
                ORDER BY promise_time DESC
                LIMIT %s OFFSET %s
            """

            offset = self.get_offset()
            self.db_connection.cursor.execute(query, (self.page_size, offset))
            rows = self.db_connection.cursor.fetchall()

            self.db_connection.cursor.execute("SELECT COUNT(*) as count FROM ProductSelectionQueue WHERE status = 'pending'")
            count_result = self.db_connection.cursor.fetchone()
            self.total_records = count_result.get('count', 0)

            self.display_reception_data(rows)
            self.update_results_label()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            print(f"Error loading reception queue: {e}")

    def display_reception_data(self, rows):
        """Display reception queue data in table"""
        self.table.setRowCount(len(rows))
        self.current_data = rows

        for i, row in enumerate(rows):
            if row['promise_time']:
                promise_time = row['promise_time'].strftime("%m/%d/%Y %I:%M %p")
            else:
                promise_time = ""

            self.table.setItem(i, 0, self._create_row_item(promise_time, row))
            self.table.setItem(i, 1, self._create_row_item(str(row.get('rx_store_num', '')), row))
            self.table.setItem(i, 2, self._create_row_item(row.get('patient_name', ''), row))
            self.table.setItem(i, 3, self._create_row_item(str(row.get('patient_id', '')), row))
            self.table.setItem(i, 4, self._create_row_item(row.get('new_refill', ''), row))
            self.table.setItem(i, 5, self._create_row_item(row.get('delivery', ''), row))
            self.table.setItem(i, 6, self._create_row_item(row.get('lock_status', ''), row))

            if row.get('delivery') == 'Waiting':
                for col in range(self.table.columnCount()):
                    item = self.table.item(i, col)
                    if item:
                        item.setBackground(QColor(Theme.WARNING_LIGHT))

            self.table.setRowHeight(i, Theme.TABLE_ROW_HEIGHT)

    def _create_row_item(self, text, row_data):
        """Helper to create table item with row data attached"""
        from PyQt6.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem(text)
        item.setData(256, row_data)
        return item

    def apply_filters_clicked(self):
        self.current_page = 0
        self.load_data()

    def reset_filters(self):
        self.promise_date.setDateTime(QDateTime.currentDateTime())
        self.promise_time.setCurrentIndex(0)
        self.rx_store.clear()
        self.store_number.clear()
        self.patient_name.clear()
        self.patient_id.clear()
        self.current_page = 0
        self.load_data()

    def update_results_label(self):
        end_record = min((self.current_page + 1) * self.page_size, self.total_records)
        start_record = (self.current_page * self.page_size) + 1 if self.total_records > 0 else 0

        if self.total_records == 0:
            label_text = "Displaying results 1 to 0 of 0."
        else:
            label_text = f"Displaying results {start_record} to {end_record} of {self.total_records}."

        if self.results_label:
            self.results_label.setText(label_text)

    def on_row_double_clicked(self, item):
        """Open reception intake dialog on double-click"""
        row = item.row()
        row_data = self.table.item(row, 0).data(256)

        if row_data:
            dialog = ReceptionIntakeDialog(self.db_connection, row_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_data()


class ReceptionIntakeDialog(QDialog):
    """Dialog for reviewing an incoming prescription before sending to Data Entry.

    Shows Rx image area, store/patient info, and medication overview.
    """

    def __init__(self, db_connection, rx_data, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.rx_data = rx_data
        self.rx_id = rx_data.get('id')

        self.setWindowTitle(f"Reception Intake - {rx_data.get('patient_name')}")
        self.setGeometry(100, 100, 680, 560)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # ── Rx Image Area ──────────────────────────────────
        image_group = QGroupBox("Prescription Image")
        image_layout = QVBoxLayout()

        image_placeholder = QFrame()
        image_placeholder.setMinimumHeight(180)
        image_placeholder.setStyleSheet(
            f"background-color: {Theme.SURFACE}; "
            f"border: 2px dashed {Theme.BORDER_DEFAULT}; "
            f"border-radius: {Theme.BORDER_RADIUS_CARD};"
        )
        placeholder_inner = QVBoxLayout(image_placeholder)
        placeholder_label = QLabel("Rx Image")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setProperty("cssClass", "text-muted")
        placeholder_inner.addWidget(placeholder_label)

        scan_hint = QLabel("Scanned prescription image will appear here")
        scan_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_hint.setProperty("cssClass", "text-secondary")
        placeholder_inner.addWidget(scan_hint)

        image_layout.addWidget(image_placeholder)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # ── Prescription & Store Info ──────────────────────
        info_group = QGroupBox("Prescription Details")
        info_layout = QFormLayout()

        rx_store_num = str(self.rx_data.get('rx_store_num', ''))
        info_layout.addRow("Rx# - Store#:", QLabel(rx_store_num))

        # Parse store number from rx_store_num (format: "XXXXX-YYYYY")
        store_num = rx_store_num.split('-')[1] if '-' in rx_store_num else '1618'
        info_layout.addRow("Filling Store:", QLabel(store_num))

        new_refill = self.rx_data.get('new_refill', 'New')
        refills_remaining = self.rx_data.get('refills', 0)
        info_layout.addRow("Type:", QLabel(f"{new_refill}  ({refills_remaining} refills remaining)"))

        delivery = self.rx_data.get('delivery', 'Waiting')
        info_layout.addRow("Delivery:", QLabel(delivery))

        promise = self.rx_data.get('promise_time')
        if promise:
            info_layout.addRow("Promise Time:", QLabel(promise.strftime("%m/%d/%Y %I:%M %p")))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # ── Patient Info ───────────────────────────────────
        patient_group = QGroupBox("Patient")
        patient_layout = QFormLayout()

        patient_layout.addRow("Name:", QLabel(self.rx_data.get('patient_name', '')))
        patient_layout.addRow("Patient ID:", QLabel(str(self.rx_data.get('patient_id', ''))))

        patient_group.setLayout(patient_layout)
        layout.addWidget(patient_group)

        # ── Medication Overview ────────────────────────────
        med_group = QGroupBox("Medication")
        med_layout = QFormLayout()

        med_layout.addRow("Product:", QLabel(self.rx_data.get('product', '')))
        med_layout.addRow("Quantity:", QLabel(str(self.rx_data.get('quantity', ''))))

        med_group.setLayout(med_layout)
        layout.addWidget(med_group)

        # ── Action Buttons ─────────────────────────────────
        button_layout = QHBoxLayout()

        status = self.rx_data.get('status', 'pending')
        status_label = QLabel(f"Status: {status}")
        status_label.setProperty("cssClass", "text-secondary")
        button_layout.addWidget(status_label)

        button_layout.addStretch()

        send_btn = QPushButton("Send to Data Entry")
        send_btn.setProperty("cssClass", "primary")
        send_btn.clicked.connect(self.send_to_data_entry)
        button_layout.addWidget(send_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def send_to_data_entry(self):
        """Mark prescription as in_progress so Data Entry queue picks it up"""
        try:
            cursor = self.db_connection.cursor
            cursor.execute("""
                UPDATE ProductSelectionQueue
                SET status = 'in_progress'
                WHERE id = %s
            """, (self.rx_id,))
            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Sent",
                f"Prescription for {self.rx_data.get('patient_name')} sent to Data Entry."
            )
            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Error", f"Failed to send to data entry: {e}")
