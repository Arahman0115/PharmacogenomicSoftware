from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView


class TransactionsTab(QWidget):
    """Transaction History tab"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.init_ui()
        if db_connection and user_id:
            self.load_transactions()

    def init_ui(self):
        """Initialize the tab UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("Transaction History")
        group_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Item", "Amount", "Payment Method", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.table)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def load_transactions(self):
        """Load transaction history from database"""
        if not self.db_connection or not self.user_id:
            return

        try:
            query = """
                SELECT release_time, medication_id, amount, payment_method, status
                FROM FinishedTransactions
                WHERE user_id = %s
                ORDER BY release_time DESC
                LIMIT 100
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            transactions = self.db_connection.cursor.fetchall()

            self.table.setRowCount(len(transactions))
            for row, trans in enumerate(transactions):
                self.table.setItem(row, 0, QTableWidgetItem(str(trans.get('release_time', ''))))
                self.table.setItem(row, 1, QTableWidgetItem(str(trans.get('medication_id', ''))))
                self.table.setItem(row, 2, QTableWidgetItem(str(trans.get('amount', ''))))
                self.table.setItem(row, 3, QTableWidgetItem(trans.get('payment_method', '')))
                self.table.setItem(row, 4, QTableWidgetItem(trans.get('status', '')))

        except Exception as e:
            print(f"Error loading transactions: {e}")
