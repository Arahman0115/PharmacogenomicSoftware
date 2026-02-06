from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView


class AllergiesTab(QWidget):
    """Allergies tab"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.init_ui()
        if db_connection and user_id:
            self.load_allergies()

    def init_ui(self):
        """Initialize the tab UI"""
        layout = QVBoxLayout(self)

        group = QGroupBox("Known Allergies")
        group_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Allergen", "Reaction", "Severity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.table)
        group.setLayout(group_layout)
        layout.addWidget(group)
        layout.addStretch()

    def load_allergies(self):
        """Load allergies from database"""
        if not self.db_connection or not self.user_id:
            return

        try:
            query = """
                SELECT allergen, reaction, severity
                FROM patient_allergies
                WHERE user_id = %s
                ORDER BY severity DESC
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            allergies = self.db_connection.cursor.fetchall()

            self.table.setRowCount(len(allergies))
            for row, allergy in enumerate(allergies):
                self.table.setItem(row, 0, QTableWidgetItem(allergy.get('allergen', '')))
                self.table.setItem(row, 1, QTableWidgetItem(allergy.get('reaction', '')))
                self.table.setItem(row, 2, QTableWidgetItem(allergy.get('severity', '')))

        except Exception as e:
            print(f"Error loading allergies: {e}")
