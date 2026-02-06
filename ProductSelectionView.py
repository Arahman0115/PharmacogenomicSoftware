from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit,
    QComboBox, QDateTimeEdit, QFrame, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter
from EditPrescriptionsView import EditPrescriptionView
from DataBaseConnection import DatabaseConnection
import datetime


class ProductSelectionView(QWidget):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Data Entry Queue - McKesson EnterpriseRx")
        self.setMinimumSize(1000, 700)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Create toolbar


        # Create filter section
        self.create_filters(main_layout)

        # Create table
        self.create_table(main_layout)

        # Create bottom section
        self.create_bottom_section(main_layout)

        # Load initial data
        self.load_queue()

    def create_toolbar(self, parent_layout):
        """Create the top toolbar with menu items"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.Box)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # Menu buttons
        menu_items = ["File", "Activities", "Tools", "Rx Queues", "Search", "Administration", "Help"]
        for item in menu_items:
            btn = QPushButton(item)
            toolbar_layout.addWidget(btn)

        toolbar_layout.addStretch()
        parent_layout.addWidget(toolbar_frame)

    def create_filters(self, parent_layout):
        """Create the filter section"""
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.Box)
        filter_frame.setProperty("cssClass", "filter-panel")

        filter_layout = QVBoxLayout(filter_frame)

        # Filter By label
        filter_label = QLabel("Filter By:")
        filter_layout.addWidget(filter_label)

        # First row of filters
        row1_layout = QHBoxLayout()

        # Promise Time
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
        filter_layout.addLayout(row1_layout)

        # Second row of filters
        row2_layout = QHBoxLayout()

        # Rx# - Store#
        row2_layout.addWidget(QLabel("Rx# - Store#:"))
        self.rx_store = QLineEdit()
        self.rx_store.setMinimumWidth(300)
        row2_layout.addWidget(self.rx_store)

        row2_layout.addStretch()
        filter_layout.addLayout(row2_layout)

        # Third row of filters
        row3_layout = QHBoxLayout()

        # Store Number
        row3_layout.addWidget(QLabel("Store Number:"))
        self.store_number = QLineEdit()
        self.store_number.setMinimumWidth(300)
        row3_layout.addWidget(self.store_number)

        row3_layout.addStretch()
        filter_layout.addLayout(row3_layout)

        # Fourth row of filters
        row4_layout = QHBoxLayout()

        # Patient Name and ID
        row4_layout.addWidget(QLabel("Patient Name:"))
        self.patient_name = QLineEdit()
        self.patient_name.setPlaceholderText("LAST, FIRST")
        self.patient_name.setMinimumWidth(200)
        row4_layout.addWidget(self.patient_name)

        row4_layout.addWidget(QLabel("Prescription ID:"))
        self.patient_id = QLineEdit()
        self.patient_id.setMinimumWidth(200)
        row4_layout.addWidget(self.patient_id)

        row4_layout.addStretch()
        filter_layout.addLayout(row4_layout)

        parent_layout.addWidget(filter_frame)

    def create_table(self, parent_layout):
        """Create the main data table"""
        # Extended View button
        view_layout = QHBoxLayout()
        self.extended_view_btn = QPushButton("Extended View")
        self.extended_view_btn.setProperty("cssClass", "secondary")
        view_layout.addWidget(self.extended_view_btn)
        view_layout.addStretch()

        # Filter and Reset buttons
        self.filter_btn = QPushButton("Filter")
        self.reset_btn = QPushButton("Reset")
        self.filter_btn.setProperty("cssClass", "primary")
        self.reset_btn.setProperty("cssClass", "ghost")

        view_layout.addWidget(self.filter_btn)
        view_layout.addWidget(self.reset_btn)
        parent_layout.addLayout(view_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Promise Time", "Rx# - Store#", "Patient Name",
            "Prescription ID", "New / Refill", "Delivery", "Lock"
        ])

        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setDefaultSectionSize(48)

        # Set table properties
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Promise Time
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Rx# - Store#
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Patient Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Patient ID
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # New/Refill
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Delivery
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Lock

        # Connect double click
        self.table.cellDoubleClicked.connect(self.on_row_clicked)

        parent_layout.addWidget(self.table)

        # Connect filter buttons
        self.filter_btn.clicked.connect(self.apply_filters)
        self.reset_btn.clicked.connect(self.reset_filters)

    def create_bottom_section(self, parent_layout):
        """Create the bottom section with results count and navigation"""
        bottom_layout = QHBoxLayout()

        # Results display
        self.results_label = QLabel("Displaying results 1 to 0 of 0.")
        self.results_label.setProperty("cssClass", "text-muted")
        bottom_layout.addWidget(self.results_label)

        bottom_layout.addStretch()

        # Page navigation buttons
        self.page_up_btn = QPushButton("Page Up")
        self.page_down_btn = QPushButton("Page Down")
        self.close_btn = QPushButton("Close")

        self.page_up_btn.setProperty("cssClass", "ghost")
        self.page_down_btn.setProperty("cssClass", "ghost")
        self.close_btn.setProperty("cssClass", "ghost")

        bottom_layout.addWidget(self.page_up_btn)
        bottom_layout.addWidget(self.page_down_btn)
        bottom_layout.addWidget(self.close_btn)

        # Connect close button
        self.close_btn.clicked.connect(self.close)

        parent_layout.addLayout(bottom_layout)

    def get_fresh_db_connection(self):
        """Create a fresh database connection each time"""
        return DatabaseConnection(

        host='127.0.0.1',
        user='pgx_user',
        password='Auddin',
        database='pgx_db',
        port=3307    )

    def load_queue(self):
        """Load queue data with completely fresh database connection"""
        self.table.setRowCount(0)

        # Create fresh connection for each refresh
        db = self.get_fresh_db_connection()

        try:
            db.cursor.execute("""
                SELECT
                    user_id,
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
                    refills
                FROM ProductSelectionQueue
                ORDER BY promise_time DESC
            """)
            rows = db.cursor.fetchall()


            print(f"Found {len(rows)} rows in ProductSelectionQueue")  # Debug line

            for i, row in enumerate(rows):
                self.table.insertRow(i)



                # Format promise time
                if row['promise_time']:
                    promise_time = row['promise_time'].strftime("%m/%d/%Y %I:%M %p")
                else:
                    promise_time = ""

                self.table.setItem(i, 0, QTableWidgetItem(promise_time))
                self.table.setItem(i, 1, QTableWidgetItem(str(row['rx_store_num']) if row['rx_store_num'] else ""))
                self.table.setItem(i, 2, QTableWidgetItem(row['patient_name']))
                self.table.setItem(i, 3, QTableWidgetItem(str(row['patient_id'])))
                self.table.setItem(i, 4, QTableWidgetItem(row['new_refill']))
                self.table.setItem(i, 5, QTableWidgetItem(row['delivery']))
                self.table.setItem(i, 6, QTableWidgetItem(row['lock_status']))
                self.table.setItem(i, 7, QTableWidgetItem(row['user_id']))
                # Set row height
                self.table.setRowHeight(i, 48)

                # Add warning icon for certain conditions (you can customize this logic)
                if row['delivery'] == 'Waiting':
                    # Create warning indicator (triangle icon)
                    warning_item = QTableWidgetItem("⚠")
                    warning_item.setBackground(Qt.GlobalColor.yellow)
                    # You could set this in a specific column or modify existing items

            # Update results label
            self.update_results_label(len(rows))

        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            print(f"Database error: {e}")  # Debug line
        finally:
            # Close the temporary connection
            try:
                db.connection.close()
            except:
                pass

    def apply_filters(self):
        """Apply filters to the data"""
        # This would implement filtering logic based on the filter inputs
        # For now, just reload the queue
        self.load_queue()

    def reset_filters(self):
        """Reset all filters to default values"""
        self.promise_date.setDateTime(QDateTime.currentDateTime())
        self.promise_time.setCurrentIndex(0)
        self.rx_store.clear()
        self.store_number.clear()
        self.patient_name.clear()
        self.patient_id.clear()
        self.load_queue()

    def update_results_label(self, count):
        """Update the results display label"""
        if count == 0:
            self.results_label.setText("Displaying results 1 to 0 of 0.")
        else:
            self.results_label.setText(f"Displaying results 1 to {count} of {count}.")

    def on_row_clicked(self, row, col):
        # Create fresh connection for this operation too
        db = self.get_fresh_db_connection()

        try:
            # Get the patient name from the table (already formatted as "LAST, FIRST")
            patient_name_item = self.table.item(row, 2)  # Patient Name column
            if not patient_name_item:
                raise Exception("Patient name not found")

            patient_name = patient_name_item.text()

            # Parse the name (format: "FIRST, LAST")
            if ', ' in patient_name:
                first_name, last_name = patient_name.split(', ', 1)
            else:
                # Fallback if format is different
                name_parts = patient_name.split(' ')
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                else:
                    first_name = patient_name
                    last_name = ""

            # Get the patient ID for more precise matching
            patient_id_item = self.table.item(row, 3)  # Patient ID column
            patient_id = patient_id_item.text() if patient_id_item else ""

            # Query using the ID for precise matching
            db.cursor.execute(
                "SELECT * FROM ProductSelectionQueue WHERE id = %s LIMIT 1",
                (patient_id,)
            )
            entry = db.cursor.fetchone()
            if not entry:
                raise Exception("Entry not found")

            self.edit_view = EditPrescriptionView(entry)
            # Connect to the custom signal
            self.edit_view.prescription_processed.connect(self.on_prescription_processed)
            self.edit_view.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            print(f"Error opening prescription: {e}")
        finally:
            try:
                db.connection.close()
            except:
                pass

    def on_prescription_processed(self):
        """Called when a prescription is successfully processed"""
        print("Prescription processed, refreshing table...")  # Debug line
        # Immediately refresh without delay since we're using fresh connections
        self.load_queue()